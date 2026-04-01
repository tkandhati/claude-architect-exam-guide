EXAM_CATEGORIES = [
    "Core Concepts & Models",
    "Prompt Engineering",
    "API & Tool Use",
    "Safety & Constitutional AI",
    "Agentic Systems & Memory",
    "Architecture Patterns & RAG",
    "Pricing, Limits & Deployment",
]

SYSTEM_PROMPT_GOTCHA = """You are an expert tutor for the Claude Certified Architect – Foundations exam.
Your explanations are clear, accurate, and grounded in Anthropic's official documentation.
Use simple language with concrete examples. Highlight common misconceptions."""

SYSTEM_PROMPT_QUIZ = """You are an exam question generator for the Claude Certified Architect – Foundations certification.
Generate challenging, realistic multiple-choice questions that test deep understanding.
You MUST return ONLY a valid JSON array with no markdown, no code fences, no explanation outside the JSON.
Each object in the array must have exactly these keys: question, options (array of 4 strings starting with A), answer (e.g. "A"), explanation."""

SYSTEM_PROMPT_STUDY_PLAN = """You are a personalized study coach for the Claude Certified Architect – Foundations exam.
Provide specific, actionable 7-day study plans based on score data. Be concise and focused."""

GOTCHA_TOPICS = {
    "Core Concepts & Models": [
        "Context window vs. max_tokens: what each controls",
        "Why Claude refuses vs. why it gives an unexpected answer",
        "Model versioning: aliases vs. pinned IDs",
        "Temperature 0 does NOT guarantee deterministic output",
        "Tokens ≠ words: multi-byte characters count differently",
        "stop_reason 'max_tokens' vs 'end_turn' implications",
        "System prompt is NOT the first user turn",
        "Claude models do not have memory between API calls",
    ],
    "Prompt Engineering": [
        "Prompt injection: user content can override instructions",
        "Few-shot examples position matters (before vs. after instructions)",
        "XML tags improve structure but are not required",
        "Negative instructions ('do not') are often less reliable than positive framing",
        "Chain-of-thought emerges but isn't always the most token-efficient approach",
        "Role prompting ('You are an expert…') can backfire with over-confidence",
        "Prefilling assistant turn to steer format has tradeoffs",
        "Temperature and top_p interact — don't set both simultaneously",
    ],
    "API & Tool Use": [
        "tool_choice='any' forces a tool call but not which one",
        "Tool results must include the matching tool_use_id",
        "Multiple tool calls in one turn: all must be answered before continuing",
        "stop_reason='tool_use' means Claude is waiting — you must respond",
        "Tool input is JSON but arrives as a string — always parse it",
        "Streaming and tool use: tool inputs stream as input_json_delta",
        "Tool descriptions are instructions — vague descriptions cause misuse",
        "Max 64 tools per request; performance degrades well before that",
    ],
    "Safety & Constitutional AI": [
        "Constitutional AI trains values, not just filters responses",
        "Harmlessness ≠ refusal — over-refusal is also a safety failure",
        "RLHF vs. RLAIF: the difference in the feedback source",
        "Jailbreaks work by shifting context, not breaking the model",
        "Safety measures are layered: training, RLHF, system prompts, guardrails",
        "Claude can discuss dangerous topics educationally but won't provide operational uplift",
        "The 'helpful, harmless, honest' hierarchy isn't always in that order",
        "Prompt injection in agentic contexts is a critical security concern",
    ],
    "Agentic Systems & Memory": [
        "pause_turn vs end_turn: server-side loop hit limit vs. completed",
        "Memory types: in-context, external, in-weights, in-cache",
        "Agentic loops need explicit termination conditions to avoid infinite loops",
        "Tool calls in agentic flows can have cascading unintended effects",
        "Subagents share no state by default — pass context explicitly",
        "Prompt caching in agents: dynamic content breaks cache for everything after",
        "Human-in-the-loop checkpoints matter for irreversible actions",
        "ReAct pattern: reason → act → observe — not just act",
    ],
    "Architecture Patterns & RAG": [
        "Chunk size vs. retrieval quality: larger chunks = more noise",
        "Embedding model and LLM must be chosen as a pair for RAG",
        "Reranking retrieved chunks before passing to Claude improves accuracy",
        "Hybrid search (dense + sparse) outperforms either alone in most domains",
        "RAG hallucinations: Claude may still confabulate if retrieved docs are ambiguous",
        "Metadata filtering reduces latency and improves precision in vector stores",
        "Query transformation (HyDE, step-back) improves recall for complex questions",
        "System prompt placement for RAG context affects caching efficiency",
    ],
    "Pricing, Limits & Deployment": [
        "Input tokens include system prompt + conversation history every turn",
        "Cache writes cost MORE than regular input (1.25×), not less",
        "Cache reads cost ~10× less than regular input — break-even is 2+ requests",
        "Rate limits are per-API-key, not per-model",
        "Batch API is 50% cheaper but has up to 24-hour latency",
        "Output tokens cost 3-5× more than input tokens",
        "Streaming does NOT reduce token cost — only reduces perceived latency",
        "Context caching TTL: 5 minutes default, 1 hour available (costs more to write)",
    ],
}

QUIZ_GENERATION_PROMPT = """Generate {n} multiple-choice exam questions for the category: "{category}"
for the Claude Certified Architect – Foundations certification exam.

Requirements:
- Questions must be challenging and test real architectural understanding
- Each question must have exactly 4 options labeled A, B, C, D
- Include one clearly correct answer and three plausible distractors
- Explanations must reference official Claude/Anthropic behavior

Return ONLY a valid JSON array. No markdown. No code fences. No text before or after the JSON.
Format:
[
  {{
    "question": "Question text here?",
    "options": ["A. option one", "B. option two", "C. option three", "D. option four"],
    "answer": "A",
    "explanation": "Explanation of why A is correct and why others are wrong."
  }}
]"""

SIMULATION_GENERATION_PROMPT = """Generate exactly {n} multiple-choice exam questions covering ALL of these 7 categories for the Claude Certified Architect – Foundations exam:
1. Core Concepts & Models
2. Prompt Engineering
3. API & Tool Use
4. Safety & Constitutional AI
5. Agentic Systems & Memory
6. Architecture Patterns & RAG
7. Pricing, Limits & Deployment

Include approximately {per_cat} questions per category. Mix difficulty levels.

Return ONLY a valid JSON array. No markdown. No code fences. No text before or after the JSON.
Format:
[
  {{
    "question": "Question text here?",
    "options": ["A. option one", "B. option two", "C. option three", "D. option four"],
    "answer": "A",
    "explanation": "Why A is correct.",
    "category": "Core Concepts & Models"
  }}
]"""

STUDY_PLAN_PROMPT = """Based on these exam scores by category: {scores_json}

I am preparing for the Claude Certified Architect – Foundations exam. Give me a specific 7-day study plan with focus areas, resources to review, and practice tips. Be concise and actionable."""
