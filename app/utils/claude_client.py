import json
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

        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[: text.rfind("```")]

        return json.loads(text.strip())

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
