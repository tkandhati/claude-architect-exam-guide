import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

# Sources ordered by priority:
# 1. Raw/structured content (most parseable, highest signal)
# 2. Dedicated exam prep sites (actual practice questions)
# 3. Technical blogs and guides (scenario explanations, anti-patterns)
INSPIRATION_SOURCES = [
    # --- Tier 1: Raw structured content ---
    {
        "url": "https://raw.githubusercontent.com/paullarionov/claude-certified-architect/main/README.md",
        "label": "github/paullarionov claude-certified-architect",
        "priority": 1,
    },
    {
        "url": "https://gist.github.com/tvytlx/2e0c4c823e56e1ddcce8f0634d1f36e6",
        "label": "github gist tvytlx become-a-claude-architect",
        "priority": 1,
    },
    # --- Tier 2: Dedicated exam prep (practice questions) ---
    {
        "url": "https://claudecertifications.com/claude-certified-architect/exam-guide",
        "label": "claudecertifications.com exam guide",
        "priority": 2,
    },
    {
        "url": "https://tutorialsdojo.com/cca-f-claude-certified-architect-foundations-study-guide/",
        "label": "tutorialsdojo.com CCA-F study guide",
        "priority": 2,
    },
    {
        "url": "https://www.ai.cc/blogs/claude-certified-architect-foundations-cca-f-exam-guide-2026/",
        "label": "ai.cc CCA-F exam guide 2026",
        "priority": 2,
    },
    {
        "url": "https://flashgenius.net/blog-article/a-guide-to-the-claude-certified-architect-foundations-certification",
        "label": "flashgenius.net CCA-F foundations guide",
        "priority": 2,
    },
    # --- Tier 3: Technical blogs (scenario explanations, anti-patterns) ---
    {
        "url": "https://pub.towardsai.net/claude-certified-architect-the-complete-guide-to-passing-the-cca-foundations-exam-9665ce7342a8",
        "label": "towardsai.net complete guide to passing CCA-F",
        "priority": 3,
    },
    {
        "url": "https://dev.to/mcrolly/inside-anthropics-claude-certified-architect-program-what-it-tests-and-who-should-pursue-it-1dk6",
        "label": "dev.to CCA-F what it tests",
        "priority": 3,
    },
    {
        "url": "https://zenvanriel.com/ai-engineer-blog/claude-certified-architect-anthropic-certification-guide/",
        "label": "zenvanriel.com CCA-F certification guide",
        "priority": 3,
    },
    {
        "url": "https://dynamicbalaji.medium.com/claude-certified-architect-foundations-certification-preparation-guide-c70546b51f51",
        "label": "medium/balaji CCA-F preparation guide",
        "priority": 3,
    },
]

_HEADERS = {"User-Agent": "Mozilla/5.0"}
_MAX_CHARS_PER_SOURCE = 1500
_MAX_TOTAL_CHARS = 12000
_SESSION_KEY = "_exam_inspiration"


def _fetch_one(source: dict, timeout: int) -> tuple[int, str, str] | None:
    """Fetch a single source. Returns (priority, label, content) or None on failure."""
    try:
        resp = requests.get(source["url"], timeout=timeout, headers=_HEADERS)
        if resp.status_code == 200:
            text = resp.text.strip()
            if len(text) > 200:
                return (source["priority"], source["label"], text[:_MAX_CHARS_PER_SOURCE])
    except Exception:
        pass
    return None


def fetch_exam_inspiration(timeout: int = 6) -> str:
    """
    Fetch real CCA-F exam question examples from all sources in parallel.
    Results are sorted by priority tier and cached in session state for the session.
    Returns combined content string, or "" if all sources fail.
    """
    if _SESSION_KEY in st.session_state:
        return st.session_state[_SESSION_KEY]

    results = []
    with ThreadPoolExecutor(max_workers=len(INSPIRATION_SOURCES)) as executor:
        futures = {executor.submit(_fetch_one, src, timeout): src for src in INSPIRATION_SOURCES}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # Sort by priority tier so highest-quality sources appear first
    results.sort(key=lambda x: x[0])

    chunks = [f"[Source: {label}]\n{content}" for _, label, content in results]
    combined = "\n\n".join(chunks)[:_MAX_TOTAL_CHARS]

    st.session_state[_SESSION_KEY] = combined
    return combined


def build_inspired_prompt(base_prompt: str) -> str:
    """
    Prepend real exam examples to a generation prompt.
    If all fetches fail, returns base_prompt unchanged.
    """
    inspiration = fetch_exam_inspiration()
    if not inspiration:
        return base_prompt

    prefix = (
        "Below are real exam questions and study material from official CCA-F preparation sources. "
        "Study their scenario structure, question wording, answer option style, and which concepts they test. "
        "Generate questions that match this exact style and difficulty level.\n\n"
        f"{inspiration}\n\n"
        "---\n\n"
        "Now generate questions following the instructions below:\n\n"
    )
    return prefix + base_prompt
