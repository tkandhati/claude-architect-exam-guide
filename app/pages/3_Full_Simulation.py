import streamlit as st
import time
from utils.prompts import EXAM_CATEGORIES, SIMULATION_GENERATION_PROMPT, SYSTEM_PROMPT_QUIZ
from utils.claude_client import get_claude_json, is_api_configured
from utils.storage import save_result

st.set_page_config(page_title="Full Simulation", page_icon="🏆", layout="wide")

TOTAL_QUESTIONS = 40
EXAM_DURATION = 60 * 60  # 60 minutes in seconds
PASS_PCT = 75


def reset_sim():
    for key in ["sim_questions", "sim_answers", "sim_start_time", "sim_finished",
                "sim_current", "sim_flagged", "sim_score_saved"]:
        st.session_state.pop(key, None)


def load_sim():
    per_cat = TOTAL_QUESTIONS // len(EXAM_CATEGORIES)
    with st.spinner(f"Generating {TOTAL_QUESTIONS} questions across all categories…"):
        prompt = SIMULATION_GENERATION_PROMPT.format(n=TOTAL_QUESTIONS, per_cat=per_cat)
        questions = get_claude_json(prompt, system_prompt=SYSTEM_PROMPT_QUIZ)

    if not questions or not isinstance(questions, list):
        st.error("Failed to generate exam questions. Please try again.")
        return False

    st.session_state["sim_questions"] = questions[:TOTAL_QUESTIONS]
    st.session_state["sim_answers"] = {}
    st.session_state["sim_flagged"] = set()
    st.session_state["sim_start_time"] = time.time()
    st.session_state["sim_finished"] = False
    st.session_state["sim_current"] = 0
    st.session_state["sim_score_saved"] = False
    return True


# Sidebar
with st.sidebar:
    if is_api_configured():
        st.success("🔑 API Connected")
    else:
        st.warning("⚠️ API Key Missing")

    questions = st.session_state.get("sim_questions")
    finished = st.session_state.get("sim_finished", False)

    if questions and not finished:
        elapsed = int(time.time() - st.session_state.get("sim_start_time", time.time()))
        remaining = max(0, EXAM_DURATION - elapsed)
        mins, secs = divmod(remaining, 60)

        color = "red" if remaining < 600 else "orange" if remaining < 1800 else "green"
        st.markdown(f"### ⏱️ Time Remaining")
        st.markdown(f"## :{color}[{mins:02d}:{secs:02d}]")

        if remaining == 0:
            st.warning("Time's up! Auto-submitting…")
            st.session_state["sim_finished"] = True
            st.rerun()

        answered = len(st.session_state.get("sim_answers", {}))
        flagged = len(st.session_state.get("sim_flagged", set()))
        st.metric("Answered", f"{answered}/{TOTAL_QUESTIONS}")
        st.metric("Flagged", flagged)

        current = st.session_state.get("sim_current", 0)
        st.markdown("**Jump to question:**")
        cols = st.columns(5)
        for i in range(TOTAL_QUESTIONS):
            ans = st.session_state.get("sim_answers", {})
            fl = st.session_state.get("sim_flagged", set())
            icon = "🚩" if i in fl else ("✓" if i in ans else str(i + 1))
            with cols[i % 5]:
                if st.button(icon, key=f"jump_{i}", help=f"Q{i+1}"):
                    st.session_state["sim_current"] = i
                    st.rerun()

        st.divider()
        if st.button("Submit Exam", type="primary", use_container_width=True):
            st.session_state["sim_finished"] = True
            st.rerun()

st.title("🏆 Full Simulation Exam")

if not questions:
    st.markdown(f"""
    **Exam Rules:**
    - {TOTAL_QUESTIONS} questions across all 7 categories
    - 60-minute time limit
    - Pass mark: **{PASS_PCT}%**
    - Flag questions for review
    - Auto-submits when time expires
    """)
    if st.button("Start Exam", type="primary"):
        if load_sim():
            st.rerun()
    st.stop()

if not finished:
    current = st.session_state.get("sim_current", 0)
    q = questions[current]
    answers = st.session_state.get("sim_answers", {})
    flagged = st.session_state.get("sim_flagged", set())

    st.markdown(f"**Question {current + 1} of {TOTAL_QUESTIONS}**")
    cat_label = q.get("category", "General")
    st.caption(f"Category: {cat_label}")

    st.markdown(f"### {q['question']}")

    options = q.get("options", [])
    prev_answer = answers.get(current)

    # Find previous answer index
    prev_idx = None
    if prev_answer:
        for j, opt in enumerate(options):
            if opt.startswith(prev_answer):
                prev_idx = j
                break

    selected = st.radio(
        "Select your answer:",
        options,
        index=prev_idx,
        key=f"sim_q_{current}",
        label_visibility="collapsed",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if current > 0:
            if st.button("← Previous"):
                if selected:
                    answers[current] = selected[0]
                    st.session_state["sim_answers"] = answers
                st.session_state["sim_current"] = current - 1
                st.rerun()
    with col2:
        if current < TOTAL_QUESTIONS - 1:
            if st.button("Next →", type="primary"):
                if selected:
                    answers[current] = selected[0]
                    st.session_state["sim_answers"] = answers
                st.session_state["sim_current"] = current + 1
                st.rerun()
    with col3:
        flag_label = "🚩 Unflag" if current in flagged else "🚩 Flag"
        if st.button(flag_label):
            if selected:
                answers[current] = selected[0]
                st.session_state["sim_answers"] = answers
            if current in flagged:
                flagged.discard(current)
            else:
                flagged.add(current)
            st.session_state["sim_flagged"] = flagged
            st.rerun()
    with col4:
        if selected:
            answers[current] = selected[0]
            st.session_state["sim_answers"] = answers

else:
    # Results page
    answers = st.session_state.get("sim_answers", {})
    score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q.get("answer"))
    pct = round(score / TOTAL_QUESTIONS * 100, 1)
    passed = pct >= PASS_PCT
    elapsed = int(time.time() - st.session_state.get("sim_start_time", time.time()))

    if passed:
        st.success(f"🎉 PASSED! Score: {score}/{TOTAL_QUESTIONS} ({pct}%)")
    else:
        st.error(f"❌ Did not pass. Score: {score}/{TOTAL_QUESTIONS} ({pct}%)")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{pct}%")
    with col2:
        st.metric("Result", "PASS ✓" if passed else "FAIL ✗")
    with col3:
        elapsed_m = elapsed // 60
        elapsed_s = elapsed % 60
        st.metric("Time Taken", f"{elapsed_m}m {elapsed_s}s")

    # Save result
    if not st.session_state.get("sim_score_saved"):
        save_result("Full Simulation", score, TOTAL_QUESTIONS, "simulation")
        for cat in EXAM_CATEGORIES:
            cat_qs = [(i, q) for i, q in enumerate(questions) if q.get("category") == cat]
            if cat_qs:
                cat_score = sum(1 for i, q in cat_qs if answers.get(i) == q.get("answer"))
                save_result(cat, cat_score, len(cat_qs), "simulation")
        st.session_state["sim_score_saved"] = True
        st.caption("✓ Results saved.")

    st.divider()
    st.subheader("Score Breakdown by Category")

    cat_results = {}
    for i, q in enumerate(questions):
        cat = q.get("category", "Unknown")
        if cat not in cat_results:
            cat_results[cat] = {"correct": 0, "total": 0}
        cat_results[cat]["total"] += 1
        if answers.get(i) == q.get("answer"):
            cat_results[cat]["correct"] += 1

    cols = st.columns(3)
    for idx, (cat, res) in enumerate(cat_results.items()):
        with cols[idx % 3]:
            cat_pct = round(res["correct"] / res["total"] * 100) if res["total"] else 0
            color = "green" if cat_pct >= 75 else "orange" if cat_pct >= 50 else "red"
            st.metric(
                cat,
                f"{res['correct']}/{res['total']} ({cat_pct}%)",
            )

    st.divider()
    st.subheader("Review Wrong Answers")
    wrong = [(i, q) for i, q in enumerate(questions) if answers.get(i) != q.get("answer")]
    if wrong:
        for i, q in wrong:
            user_ans = answers.get(i, "—")
            correct_ans = q.get("answer", "")
            with st.expander(f"❌ Q{i+1}: {q['question'][:80]}…"):
                st.markdown(f"**Your answer:** {user_ans}")
                st.markdown(f"**Correct answer:** {correct_ans}")
                for opt in q.get("options", []):
                    st.markdown(f"- {opt}")
                st.info(f"**Explanation:** {q.get('explanation', '')}")
    else:
        st.success("Perfect score — no wrong answers!")

    if st.button("Retake Exam", type="primary"):
        reset_sim()
        st.rerun()
