import json
import re
import streamlit as st
import anthropic

MODEL = "claude-opus-4-6"
MAX_TOKENS = 20000


def _get_client() -> anthropic.Anthropic:
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = None
    if not api_key or api_key == "your-key-here":
        st.error("API key not configured. Add your key to `.streamlit/secrets.toml`.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


def is_api_configured() -> bool:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        return bool(key) and key != "your-key-here"
    except Exception:
        return False


def get_claude_response(prompt: str, system_prompt: str = "", stream: bool = False):
    """Call Claude and return full text response, or a stream object if stream=True."""
    client = _get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = dict(model=MODEL, max_tokens=MAX_TOKENS, messages=messages)
    if system_prompt:
        kwargs["system"] = system_prompt

    try:
        if stream:
            return client.messages.stream(**kwargs)
        response = client.messages.create(**kwargs)
        for block in response.content:
            if block.type == "text":
                return block.text
        return ""
    except anthropic.AuthenticationError:
        st.error("Invalid API key. Check your `.streamlit/secrets.toml`.")
        st.stop()
    except anthropic.RateLimitError:
        st.error("Rate limit reached. Please wait a moment and try again.")
        st.stop()
    except anthropic.APIError as e:
        st.error(f"API error: {e}")
        st.stop()


def stream_question_chat(question: dict, chat_history: list[dict], user_message: str):
    """
    Stream a chat response anchored strictly to one exam question's concepts.
    chat_history: list of {"role": "user"|"assistant", "content": str}
    Returns a stream context manager.
    """
    client = _get_client()

    q_text = question.get("question", "")
    options = "\n".join(question.get("options", []))
    answer = question.get("answer", "")
    explanation = question.get("explanation", "")
    category = question.get("category", "")

    system = f"""You are a focused exam tutor for the Claude Certified Architect – Foundations (CCA-F) exam.
Your job is to help the learner deeply understand ONE specific question and the concepts it tests.
Stay strictly on-topic — only discuss concepts directly relevant to this question.
Do not answer unrelated questions; politely redirect to the question's topic if needed.

=== QUESTION CONTEXT ===
Category: {category}

Question: {q_text}

Options:
{options}

Correct Answer: {answer}
Explanation: {explanation}
========================

When explaining:
- Connect concepts to the specific scenario in the question
- Use analogies from production engineering when helpful
- If asked about a wrong option, explain the exact production failure mode
- If asked about the correct answer, explain WHY it provides a structural guarantee the others don't
- Be concise but precise — this is exam prep, not a lecture"""

    messages = chat_history + [{"role": "user", "content": user_message}]

    return client.messages.stream(
        model=MODEL,
        max_tokens=1024,
        system=system,
        messages=messages,
    )


def _extract_json(raw: str) -> list | dict:
    """
    Robustly extract a JSON array or object from raw text.
    Tries multiple strategies in order of reliability.
    """
    text = raw.strip()

    # Strategy 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: find the outermost JSON array using regex (handles surrounding prose/fences)
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 3: find the outermost JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 4: strip markdown code fences (handles ``` and ```json)
    stripped = re.sub(r'^```[a-z]*\n?', '', text, flags=re.MULTILINE)
    stripped = re.sub(r'\n?```$', '', stripped, flags=re.MULTILINE)
    stripped = stripped.strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    raise json.JSONDecodeError("Could not extract JSON from response", text, 0)


def _validate_questions(questions: list) -> list:
    """
    Filter out malformed question objects (e.g. template echoes with bad keys).
    A valid question must have 'question', 'options', and 'answer' as plain string keys.
    """
    valid = []
    required = {"question", "options", "answer"}
    for q in questions:
        if not isinstance(q, dict):
            continue
        # Keys must be clean strings with no newlines or quotes
        keys = set(q.keys())
        if not required.issubset(keys):
            continue
        if any('\n' in k or '"' in k for k in keys):
            continue
        # question must be a non-empty string
        if not isinstance(q.get("question"), str) or not q["question"].strip():
            continue
        # options must be a list of 4 items
        if not isinstance(q.get("options"), list) or len(q["options"]) < 2:
            continue
        valid.append(q)
    return valid


def get_claude_json(prompt: str, system_prompt: str = "") -> list | dict | None:
    """Call Claude and parse the response as JSON. Returns parsed object or None on error."""
    client = _get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = dict(model=MODEL, max_tokens=MAX_TOKENS, messages=messages)
    if system_prompt:
        kwargs["system"] = system_prompt

    try:
        response = client.messages.create(**kwargs)
        raw = ""
        for block in response.content:
            if block.type == "text":
                raw = block.text
                break

        result = _extract_json(raw)

        # If it's a list of question dicts, validate and clean them
        if isinstance(result, list) and result and isinstance(result[0], dict):
            result = _validate_questions(result)
            if not result:
                st.error("Claude returned questions with malformed keys. Please regenerate.")
                return None

        return result

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse Claude's response as JSON: {e}")
        return None
    except anthropic.AuthenticationError:
        st.error("Invalid API key. Check your `.streamlit/secrets.toml`.")
        st.stop()
    except anthropic.RateLimitError:
        st.error("Rate limit reached. Please wait and try again.")
        st.stop()
    except anthropic.APIError as e:
        st.error(f"API error: {e}")
        st.stop()
