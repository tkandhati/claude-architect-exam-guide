import streamlit as st
import time
from utils.prompts import EXAM_CATEGORIES, QUIZ_GENERATION_PROMPT, SYSTEM_PROMPT_QUIZ
from utils.claude_client import get_claude_json, is_api_configured, stream_question_chat, inject_chat_styles
from utils.storage import save_result, load_sample_questions
from utils.inspiration import build_inspired_prompt

st.set_page_config(page_title="Quick Test", page_icon="⚡", layout="wide")
inject_chat_styles()

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

with st.sidebar:
    if is_api_configured():
        st.success("🔑 API Connected")
    else:
        st.warning("⚠️ API Key Missing")

    st.header("Quiz Settings")

    default_cat_idx = 0
    if "preselect_category" in st.session_state:
        cat = st.session_state.pop("preselect_category")
        if cat in EXAM_CATEGORIES:
            default_cat_idx = EXAM_CATEGORIES.index(cat)

    category = st.selectbox("Category", EXAM_CATEGORIES, index=default_cat_idx)
    n_questions = st.selectbox("Number of questions", [5, 10, 15], index=1)

    source_mode = st.radio(
        "Question source",
        ["Sample bank (from official practice exam)", "AI-generated"],
        index=0,
    )

    generate_btn = st.button("Generate Quiz", type="primary", use_container_width=True)
    regenerate_btn = st.button("Regenerate", use_container_width=True)

st.title("⚡ Quick Test")


def reset_quiz():
    for key in ["qt_questions", "qt_answers", "qt_start_time", "qt_finished",
                "qt_current", "qt_category", "qt_score_saved", "qt_learn_more_history"]:
        st.session_state.pop(key, None)


def load_quiz(cat, n, use_samples):
    if use_samples:
        questions = load_sample_questions(n=n)
        if not questions:
            st.warning("Sample bank empty for this category — falling back to AI-generated questions.")
            use_samples = False

    if not use_samples:
        with st.spinner(f"Generating {n} questions for '{cat}'…"):
            prompt = build_inspired_prompt(QUIZ_GENERATION_PROMPT.format(n=n, category=cat))
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
    st.session_state["qt_learn_more_history"] = {}


if generate_btn or regenerate_btn:
    reset_quiz()
    use_samples = source_mode.startswith("Sample")
    load_quiz(category, n_questions, use_samples)

questions = st.session_state.get("qt_questions")

if not questions:
    st.info("Select a category and click **Generate Quiz** to start.")
    st.markdown("""
**Sample bank** uses real questions collected from the official Anthropic practice exam.
**AI-generated** creates fresh scenario-based questions in the same style.
    """)
    st.stop()

answers = st.session_state.get("qt_answers", {})
finished = st.session_state.get("qt_finished", False)
current = st.session_state.get("qt_current", 0)
cat = st.session_state.get("qt_category", category)
total = len(questions)


def render_distractor_analysis(q: dict, user_ans: str, q_index: int):
    """Render the enhanced explanation panel with per-option analysis and Learn More chat."""
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
    chat_store_key = "qt_learn_more_history"
    all_histories = st.session_state.get(chat_store_key, {})
    history = all_histories.get(q_index, [])

    with st.expander("💬 Learn More — chat about this question", expanded=False):
        st.caption(
            "Ask anything about this question's concepts, why options are right/wrong, "
            "or how to apply this pattern in production. Stays focused on this question."
        )

        # Messages — oldest first so newest is at the bottom
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Input below messages — form clears on submit and Enter key works
        with st.form(key=f"qt_lm_form_{q_index}", clear_on_submit=True):
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


if not finished:
    st.markdown(f"**Question {current + 1} of {total}** — {cat}")
    elapsed = int(time.time() - st.session_state.get("qt_start_time", time.time()))
    st.caption(f"Time elapsed: {elapsed // 60}m {elapsed % 60}s")

    q = questions[current]

    # Source badge
    if q.get("source") == "official_sample":
        st.caption("📋 Official practice exam question")

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

        render_distractor_analysis(q, user_ans, current)

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
        st.success("Great job! You passed this category.")
    elif pct >= 50:
        st.warning("Good effort. Keep reviewing this category.")
    else:
        st.error("Needs more work. Review the gotcha topics for this category.")

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
        with st.expander(f"{icon} Q{i+1}: {q['question'][:90]}…"):
            st.markdown(f"**Your answer:** {user_ans} | **Correct answer:** {correct_ans}")
            for opt in q.get("options", []):
                marker = " ✓" if opt.startswith(correct_ans) else (" ✗" if opt.startswith(user_ans) and user_ans != correct_ans else "")
                st.markdown(f"- {opt}{marker}")
            st.divider()
            render_distractor_analysis(q, user_ans, i)

    if st.button("New Quiz", type="primary"):
        reset_quiz()
        st.rerun()
