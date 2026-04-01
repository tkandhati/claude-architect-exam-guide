import streamlit as st
import time
from utils.prompts import EXAM_CATEGORIES, QUIZ_GENERATION_PROMPT, SYSTEM_PROMPT_QUIZ
from utils.claude_client import get_claude_json, is_api_configured
from utils.storage import save_result

st.set_page_config(page_title="Quick Test", page_icon="⚡", layout="wide")

with st.sidebar:
    if is_api_configured():
        st.success("🔑 API Connected")
    else:
        st.warning("⚠️ API Key Missing")

    st.header("Quiz Settings")

    # Allow pre-filtering from Page 4
    default_cat_idx = 0
    if "preselect_category" in st.session_state:
        cat = st.session_state.pop("preselect_category")
        if cat in EXAM_CATEGORIES:
            default_cat_idx = EXAM_CATEGORIES.index(cat)

    category = st.selectbox("Category", EXAM_CATEGORIES, index=default_cat_idx)
    n_questions = st.selectbox("Number of questions", [5, 10, 15], index=1)

    generate_btn = st.button("Generate Quiz", type="primary", use_container_width=True)
    regenerate_btn = st.button("Regenerate", use_container_width=True)

st.title("⚡ Quick Test")


def reset_quiz():
    for key in ["qt_questions", "qt_answers", "qt_start_time", "qt_finished",
                "qt_current", "qt_category", "qt_score_saved"]:
        st.session_state.pop(key, None)


def load_quiz(cat, n):
    with st.spinner(f"Generating {n} questions for '{cat}'..."):
        prompt = QUIZ_GENERATION_PROMPT.format(n=n, category=cat)
        questions = get_claude_json(prompt, system_prompt=SYSTEM_PROMPT_QUIZ)

    if not questions or not isinstance(questions, list):
        st.error("Failed to generate questions. Please try again.")
        return

    st.session_state["qt_questions"] = questions[:n]
    st.session_state["qt_answers"] = {}
    st.session_state["qt_start_time"] = time.time()
    st.session_state["qt_finished"] = False
    st.session_state["qt_current"] = 0
    st.session_state["qt_category"] = cat
    st.session_state["qt_score_saved"] = False


if generate_btn or regenerate_btn:
    reset_quiz()
    load_quiz(category, n_questions)

questions = st.session_state.get("qt_questions")

if not questions:
    st.info("Select a category and click **Generate Quiz** to start.")
    st.stop()

answers = st.session_state.get("qt_answers", {})
finished = st.session_state.get("qt_finished", False)
current = st.session_state.get("qt_current", 0)
cat = st.session_state.get("qt_category", category)
total = len(questions)

if not finished:
    # Show one question at a time
    st.markdown(f"**Question {current + 1} of {total}** — {cat}")
    elapsed = int(time.time() - st.session_state.get("qt_start_time", time.time()))
    st.caption(f"Time elapsed: {elapsed // 60}m {elapsed % 60}s")

    q = questions[current]
    st.markdown(f"### {q['question']}")

    options = q.get("options", [])
    selected = st.radio("Choose an answer:", options, key=f"q_{current}", index=None)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Submit Answer", disabled=selected is None):
            answers[current] = selected[0] if selected else None
            st.session_state["qt_answers"] = answers

    if current in answers:
        user_ans = answers[current]
        correct_ans = q.get("answer", "")
        is_correct = user_ans == correct_ans

        if is_correct:
            st.success(f"✅ Correct! The answer is **{correct_ans}**.")
        else:
            st.error(f"❌ Incorrect. The correct answer is **{correct_ans}**.")
        st.info(f"**Explanation:** {q.get('explanation', '')}")

        # Navigation
        col_prev, col_next = st.columns(2)
        with col_prev:
            if current > 0:
                if st.button("← Previous"):
                    st.session_state["qt_current"] = current - 1
                    st.rerun()
        with col_next:
            if current < total - 1:
                if st.button("Next →", type="primary"):
                    st.session_state["qt_current"] = current + 1
                    st.rerun()
            else:
                if st.button("Finish Quiz", type="primary"):
                    st.session_state["qt_finished"] = True
                    st.rerun()

else:
    # Results
    elapsed = int(time.time() - st.session_state.get("qt_start_time", time.time()))
    score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q.get("answer"))

    st.subheader("Quiz Complete!")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total}")
    with col2:
        pct = round(score / total * 100)
        st.metric("Percentage", f"{pct}%")
    with col3:
        st.metric("Time", f"{elapsed // 60}m {elapsed % 60}s")

    if pct >= 75:
        st.success("🎉 Great job! You passed this category.")
    elif pct >= 50:
        st.warning("📚 Good effort. Keep reviewing this category.")
    else:
        st.error("🔴 Needs more work. Review the gotcha topics for this category.")

    if not st.session_state.get("qt_score_saved"):
        save_result(cat, score, total, "quick")
        st.session_state["qt_score_saved"] = True
        st.caption("✓ Result saved to progress tracker.")

    st.divider()
    st.subheader("Review All Questions")
    for i, q in enumerate(questions):
        user_ans = answers.get(i, "—")
        correct_ans = q.get("answer", "")
        icon = "✅" if user_ans == correct_ans else "❌"
        with st.expander(f"{icon} Q{i+1}: {q['question'][:80]}…"):
            st.markdown(f"**Your answer:** {user_ans}")
            st.markdown(f"**Correct answer:** {correct_ans}")
            for opt in q.get("options", []):
                st.markdown(f"- {opt}")
            st.info(f"**Explanation:** {q.get('explanation', '')}")

    if st.button("New Quiz", type="primary"):
        reset_quiz()
        st.rerun()
