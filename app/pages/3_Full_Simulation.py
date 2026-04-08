import streamlit as st
import time
from utils.prompts import EXAM_CATEGORIES, SIMULATION_GENERATION_PROMPT, SYSTEM_PROMPT_QUIZ
from utils.claude_client import get_claude_json, is_api_configured, stream_question_chat, inject_chat_styles
from utils.storage import save_result, load_sample_questions
from utils.inspiration import build_inspired_prompt

MISTAKE_CATEGORY_COLORS = {
    "Prompt-over-Structure Fallacy": "🔴",
    "Over-Engineering": "🟠",
    "Correct Direction Wrong Order": "🟡",
    "Surface-Level Fix": "🟡",
    "Non-Existent Feature": "⚫",
    "Wrong Layer": "🟠",
    "Repeating Failed Strategy": "🔴",
    "Ignoring Constraint": "🔴",
    "Misread Constraint": "🟡",
    "Lagging Signal": "🟠",
    "Correct Direction, Wrong Order": "🟡",
    "Correct Direction, Wrong Scope": "🟡",
}

st.set_page_config(page_title="Full Simulation", page_icon="🏆", layout="wide")
inject_chat_styles()

TOTAL_QUESTIONS = 60
EXAM_DURATION = 120 * 60  # 120 minutes in seconds (matches real CCA-F exam)
PASS_PCT = 75  # ≈ 720/1000 scaled score on the real exam


def reset_sim():
    for key in ["sim_questions", "sim_answers", "sim_start_time", "sim_finished",
                "sim_current", "sim_flagged", "sim_score_saved"]:
        st.session_state.pop(key, None)


def load_sim():
    # Start with sample bank questions, then fill remainder with AI-generated
    sample_qs = load_sample_questions()
    n_samples = len(sample_qs)
    n_ai = max(0, TOTAL_QUESTIONS - n_samples)

    questions = list(sample_qs)

    if n_ai > 0:
        with st.spinner(f"Generating {n_ai} additional scenario-based questions…"):
            prompt = build_inspired_prompt(SIMULATION_GENERATION_PROMPT.format(n=n_ai))
            ai_qs = get_claude_json(prompt, system_prompt=SYSTEM_PROMPT_QUIZ)
        if ai_qs and isinstance(ai_qs, list):
            questions += ai_qs

    if not questions:
        st.error("Failed to generate exam questions. Please try again.")
        return False

    import random
    random.shuffle(questions)

    st.session_state["sim_questions"] = questions[:TOTAL_QUESTIONS]
    st.session_state["sim_answers"] = {}
    st.session_state["sim_flagged"] = set()
    st.session_state["sim_start_time"] = time.time()
    st.session_state["sim_finished"] = False
    st.session_state["sim_current"] = 0
    st.session_state["sim_score_saved"] = False
    st.session_state["sim_learn_more_history"] = {}
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
    **Exam Rules (mirrors real CCA-F format):**
    - {TOTAL_QUESTIONS} scenario-based questions across all 5 official domains
    - 120-minute time limit
    - Pass mark: **{PASS_PCT}%** (≈ 720/1,000 scaled score on the real exam)
    - All questions are production scenario-anchored — no trivia
    - Flag questions for review; auto-submits when time expires
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
            with st.expander(f"❌ Q{i+1}: {q['question'][:90]}…"):
                st.markdown(f"**Your answer:** {user_ans} | **Correct answer:** {correct_ans}")
                for opt in q.get("options", []):
                    marker = " ✓" if opt.startswith(correct_ans) else (" ✗" if opt.startswith(str(user_ans)) and user_ans != correct_ans else "")
                    st.markdown(f"- {opt}{marker}")
                st.divider()
                _render_distractor_analysis(q, user_ans, i)
    else:
        st.success("Perfect score — no wrong answers!")

    if st.button("Retake Exam", type="primary"):
        reset_sim()
        st.rerun()


def _render_distractor_analysis(q: dict, user_ans: str, q_index: int):
    correct_ans = q.get("answer", "")
    explanation = q.get("explanation", "")
    distractor_analysis = q.get("distractor_analysis", {})
    close_options = q.get("close_options", [])
    close_vs_correct = q.get("close_vs_correct", "")

    st.markdown(f"**Why {correct_ans} is correct:**")
    st.info(explanation)

    if close_options and close_vs_correct:
        close_labels = " and ".join(close_options)
        st.markdown(f"**Close distractor{'s' if len(close_options) > 1 else ''}: {close_labels}**")
        st.warning(f"⚠️ {close_vs_correct}")

    if distractor_analysis:
        st.markdown("---")
        st.markdown("**Option-by-option analysis:**")
        for opt_letter, analysis in distractor_analysis.items():
            opt_letter = opt_letter.strip()
            is_close = opt_letter in close_options
            is_chosen = opt_letter == user_ans and user_ans != correct_ans
            icon = "🎯 " if is_close else ""
            chosen_tag = " ← your answer" if is_chosen else ""
            mistake_cat = analysis.get("mistake_category", "")
            color_icon = MISTAKE_CATEGORY_COLORS.get(mistake_cat, "⚪")
            with st.expander(
                f"{icon}Option {opt_letter}{chosen_tag} — {color_icon} {mistake_cat}",
                expanded=is_chosen or is_close,
            ):
                st.markdown("**Why this is wrong here:**")
                st.markdown(analysis.get("why_wrong", ""))
                st.markdown(f"**When {opt_letter} would be the right answer:**")
                st.markdown(f"_{analysis.get('when_correct', '')}_")

    st.markdown("---")
    _render_learn_more_chat(q, q_index)


def _render_learn_more_chat(q: dict, q_index: int):
    """Question-scoped chat. Input is always below messages; history is oldest-first."""
    chat_store_key = "sim_learn_more_history"
    all_histories = st.session_state.get(chat_store_key, {})
    history = all_histories.get(q_index, [])

    with st.expander("💬 Learn More — chat about this question", expanded=False):
        st.caption(
            "Ask anything about this question's concepts, why options are right/wrong, "
            "or how to apply this pattern in production. Stays focused on this question."
        )

        # Messages oldest-first so newest is at the bottom
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input below messages — form clears on submit and Enter key works
        with st.form(key=f"sim_lm_form_{q_index}", clear_on_submit=True):
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                user_input = st.text_input(
                    "Your question",
                    label_visibility="collapsed",
                    placeholder="Ask about this question…",
                )
            with col_btn:
                send = st.form_submit_button("Send")

        if send and user_input.strip():
            msg_text = user_input.strip()
            history.append({"role": "user", "content": msg_text})
            with st.chat_message("user"):
                st.markdown(msg_text)
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                with stream_question_chat(q, history[:-1], msg_text) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            history.append({"role": "assistant", "content": full_response})
            all_histories[q_index] = history
            st.session_state[chat_store_key] = all_histories
            st.rerun()
