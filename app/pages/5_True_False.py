import random
import streamlit as st
from utils.prompts import EXAM_CATEGORIES, TRUE_FALSE_QUESTIONS

st.set_page_config(page_title="True / False", page_icon="✅", layout="wide")

with st.sidebar:
    st.header("Select Category")
    category = st.selectbox("Category", EXAM_CATEGORIES, label_visibility="collapsed")

st.title("✅ True / False Practice")
st.markdown(f"**Category:** {category}")
st.divider()

queue_key = f"tf_queue_{category}"
answered_key = f"tf_answered_{category}"

all_questions = TRUE_FALSE_QUESTIONS.get(category, [])

# Initialise a shuffled queue for this category
if queue_key not in st.session_state:
    q = all_questions[:]
    random.shuffle(q)
    st.session_state[queue_key] = q
    st.session_state[answered_key] = None   # None = not answered yet

queue = st.session_state[queue_key]

if not queue:
    st.success("You've gone through all questions for this category!")
    if st.button("Restart", type="primary"):
        q = all_questions[:]
        random.shuffle(q)
        st.session_state[queue_key] = q
        st.session_state[answered_key] = None
        st.rerun()
else:
    current = queue[0]
    answered = st.session_state[answered_key]

    remaining = len(queue)
    st.caption(f"{remaining} question{'s' if remaining != 1 else ''} remaining")

    st.markdown(f"### {current['q']}")
    st.write("")

    if answered is None:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("True", key="btn_true", use_container_width=True, type="primary"):
                st.session_state[answered_key] = True
                st.rerun()
        with col2:
            if st.button("False", key="btn_false", use_container_width=True, type="primary"):
                st.session_state[answered_key] = False
                st.rerun()
    else:
        correct = answered == current["a"]
        if correct:
            st.success("Correct ✓")
        else:
            correct_word = "True" if current["a"] else "False"
            st.error(f"Wrong ✗  —  Answer is **{correct_word}**")

        if st.button("Next →", type="primary"):
            st.session_state[queue_key] = queue[1:]
            st.session_state[answered_key] = None
            st.rerun()
