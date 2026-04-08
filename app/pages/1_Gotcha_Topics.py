import random

import streamlit as st
from utils.claude_client import get_claude_response, is_api_configured
from utils.prompts import EXAM_CATEGORIES, GOTCHA_TOPICS, SYSTEM_PROMPT_GOTCHA

st.set_page_config(page_title="Gotcha Topics", page_icon="🎯", layout="wide")

with st.sidebar:
    if is_api_configured():
        st.success("🔑 API Connected")
    else:
        st.warning("⚠️ API Key Missing")

    st.header("Select Category")
    category = st.selectbox("Category", EXAM_CATEGORIES, label_visibility="collapsed")

st.title("🎯 Gotcha Topics")
st.markdown(f"**Category:** {category}")

col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("These are the concepts most likely to trip you up. Click any topic for a Claude explanation.")
with col2:
    if st.button("🔄 Refresh", key=f"refresh_{category}", help="Show a different set of gotchas"):
        batch_key = f"gotcha_batch_{category}"
        all_topics = GOTCHA_TOPICS.get(category, [])
        current = st.session_state.get(batch_key, [])
        remaining = [t for t in all_topics if t not in current]
        pool = remaining if len(remaining) >= 4 else all_topics
        st.session_state[batch_key] = random.sample(pool, min(4, len(pool)))
        st.rerun()

st.divider()

all_topics = GOTCHA_TOPICS.get(category, [])
batch_key = f"gotcha_batch_{category}"

if batch_key not in st.session_state:
    st.session_state[batch_key] = random.sample(all_topics, min(4, len(all_topics)))

topics = st.session_state[batch_key]

for i, topic in enumerate(topics):
    topic_id = str(abs(hash(topic)))[-8:]
    with st.expander(f"**{i+1}.** {topic}"):
        btn_key = f"explain_{category}_{topic_id}"
        response_key = f"response_{category}_{topic_id}"

        if st.button("Explain with Claude", key=btn_key):
            with st.spinner("Asking Claude..."):
                prompt = f"Explain this gotcha concept for the Claude Certified Architect Foundations exam in simple terms with an example: {topic}"
                result = get_claude_response(prompt, system_prompt=SYSTEM_PROMPT_GOTCHA)
                st.session_state[response_key] = result

        if response_key in st.session_state:
            st.markdown(st.session_state[response_key])

st.divider()

st.subheader("Ask Claude anything about this category")
st.caption(f"Ask any question related to: {category}")

user_question = st.text_area(
    "Your question",
    placeholder=f"e.g. What's the difference between cache writes and cache reads in terms of pricing?",
    key=f"freetext_{category}",
    label_visibility="collapsed",
)

if st.button("Ask Claude", key=f"ask_{category}", type="primary"):
    if not user_question.strip():
        st.warning("Please enter a question first.")
    else:
        system = f"{SYSTEM_PROMPT_GOTCHA}\n\nThe user is asking about the category: {category}."
        st.markdown("**Claude's answer:**")

        response_placeholder = st.empty()
        full_response = ""

        with st.spinner("Thinking..."):
            stream_ctx = get_claude_response(user_question, system_prompt=system, stream=True)

        with stream_ctx as stream:
            for text in stream.text_stream:
                full_response += text
                response_placeholder.markdown(full_response + "▌")
        response_placeholder.markdown(full_response)
