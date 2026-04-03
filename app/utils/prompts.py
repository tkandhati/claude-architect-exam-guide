EXAM_CATEGORIES = [
    "Agentic Architecture & Orchestration",
    "Tool Design & MCP Integration",
    "Claude Code Configuration & Workflows",
    "Prompt Engineering & Structured Output",
    "Context Management & Reliability",
]

SYSTEM_PROMPT_GOTCHA = """You are an expert tutor for the Claude Certified Architect – Foundations (CCA-F) exam.
Your explanations are grounded in Anthropic's official documentation and real production behavior.
Focus on WHY the correct answer is correct (deterministic vs. probabilistic, structural vs. prompt-based).
Use concrete production scenarios. Highlight the exact mistake a candidate would make if they got this wrong."""

SYSTEM_PROMPT_QUIZ = """You are an exam question writer for the Claude Certified Architect – Foundations (CCA-F) certification.

The real CCA-F exam format:
- 60 scenario-based multiple-choice questions, 120 minutes
- Every question drops the candidate into a PRODUCTION scenario (customer support agent, CI/CD pipeline, multi-agent system, structured data extraction, developer productivity tooling)
- Wrong answers represent real engineering mistakes — all 4 options must be architecturally plausible
- Questions test JUDGMENT and TRADE-OFFS, not trivia or memorization
- The most-tested principle: programmatic/structural enforcement beats prompt-based guidance whenever consequences are financial, security-related, or compliance-related

You MUST return ONLY a valid JSON array with no markdown, no code fences, no explanation outside the JSON.
Each object must have exactly these keys: question, options (array of 4 strings starting with A/B/C/D), answer (single letter e.g. "B"), explanation."""

GOTCHA_TOPICS = {
    "Agentic Architecture & Orchestration": [
        "Check stop_reason field to detect loop termination — never parse natural language like 'task complete'",
        "Programmatic hooks (PreToolUse/PostToolUse) are the ONLY reliable enforcement for financial/compliance rules",
        "Subagents do NOT inherit coordinator context — always pass a summary explicitly",
        "Optimal tool count per agent is 4–5; assigning 10+ tools degrades selection accuracy",
        "Escalation triggers: explicit customer request, policy exception, authority limit — NOT sentiment score or self-reported confidence",
        "Orchestrator-workers for dynamic tasks; prompt chaining for fixed repeating workflows — never swap them",
        "pause_turn = server-side loop limit hit; end_turn = task complete — require different application responses",
        "Hub-and-spoke architecture: coordinator delegates to specialists, keeps its own context focused",
    ],
    "Tool Design & MCP Integration": [
        "MCP readOnlyHint is self-reported by the server — a rogue server can lie; trust the server, not the annotation",
        "Two-tool safety pattern: preview tool returns one-time token, execute tool requires that token — makes unsafe path impossible",
        "MCP non-adoption root cause: vague tool description, NOT missing system prompt routing instructions",
        "Protocol-level MCP error (malformed JSON-RPC) vs. application-level error (isError:true in tool result) — different response required",
        "Transient errors (network timeout): retry with backoff INSIDE the tool — the model never sees it",
        "Uncertain state after a write timeout: communicate ambiguity explicitly, set retryable:false — NOT retryable:true",
        "Return errors as tool content with isError flag — thrown exceptions strip all context from the model",
        "Lookup-then-act: search tool returns unambiguous ID, action tool takes that ID — eliminates entity resolution errors",
    ],
    "Claude Code Configuration & Workflows": [
        "CLAUDE.md is loaded at the start of EVERY session — write principles and context, not exhaustive conditionals",
        "PreToolUse hook exits non-zero → tool call is BLOCKED — this is how programmatic guardrails work without modifying prompts",
        "Grep searches file CONTENTS by regex; Glob finds files by NAME/PATH pattern — never use Grep to find files by name",
        "Edit requires a UNIQUE string match — if the string appears twice, Edit fails; fallback is Read then Write",
        "--resume with a changed codebase risks stale context referencing renamed/deleted code; summarize and start fresh",
        "settings.json hierarchy: user (~/.claude/) → project (.claude/) → local (.claude/settings.local.json, gitignored)",
        "-p flag enables non-interactive/CI mode; --output-format json for machine-readable pipeline integration",
        "Custom slash commands in .claude/commands/ (project-scoped) let teams encode repeatable workflows as reusable prompts",
    ],
    "Prompt Engineering & Structured Output": [
        "System prompt is sent with EVERY API request — if your app sends it only once, that's an application bug",
        "Dilution happens even below 50% context capacity — attention to system prompt weakens as conversation grows",
        "Few-shot examples resist dilution better than verbose written rules — 2–4 targeted examples outperform 20 bullet points",
        "NEVER/ALWAYS language may slightly increase compliance but CANNOT guarantee it — use programmatic enforcement for hard rules",
        "Safety-critical rules need EXPLICIT conditionals, not general principles — principles require judgment; compliance rules must fire deterministically",
        "Structured output via JSON schema prevents fabrication — use optional/nullable fields for data that may be absent",
        "Validation-retry loop works for FORMAT errors; it fails when the information is genuinely absent in the source",
        "Two-step pattern: reason first, format second — asking the model to reason AND format simultaneously degrades both",
    ],
    "Context Management & Reliability": [
        "Stateless API: NO memory between calls, NO session_id, NO built-in memory — your app sends the full history every request",
        "Input tokens include system prompt + FULL conversation history on every single turn — costs grow linearly",
        "Structured case-facts block preserves transactional data (IDs, amounts, decisions) more reliably than summarization",
        "Sliding window = complete loss of older turns; progressive summarization preserves compressed history — know when each applies",
        "Stale tool results: when a user returns after hours, start a new session with fresh tool calls — don't resume with outdated data",
        "RAG results accumulate and crowd out conversation history — keep only the last 2–3 queries' retrieved context",
        "Context attention degrades with conversation length EVEN when well under the token capacity limit",
        "Error propagation: pass failure type, what was attempted, partial results, and alternatives — never silently suppress errors",
    ],
}

QUIZ_GENERATION_PROMPT = """Generate {n} multiple-choice exam questions for the domain: "{category}"
for the Claude Certified Architect – Foundations (CCA-F) certification.

The real CCA-F exam format:
- Every question anchors the candidate in a PRODUCTION scenario (customer support agent, CI/CD pipeline, multi-agent research system, structured data extraction, developer productivity tooling)
- Wrong answers represent real engineering mistakes — all 4 options must be architecturally plausible
- Questions test ARCHITECTURAL JUDGMENT and TRADE-OFFS, not trivia or memorization
- The most-tested principle: programmatic/structural enforcement beats prompt-based guidance for anything financial, security, or compliance-related

Use these question patterns (vary them):
- "A team built [agent/workflow]. [Problem occurs]. What is the MOST LIKELY cause / correct fix?"
- "Which approach BEST ensures [requirement] in a production [system]?"
- "A developer [did X]. Why does [symptom] occur / what should they do instead?"
- "An agent [does X]. Which design decision explains this behavior?"
- "Which of the following correctly describes [behavior/trade-off]?"

Requirements:
- One clearly correct answer; three distractors that represent real plausible mistakes
- Explanations must state WHY the correct answer is deterministic/structural AND why each wrong answer fails in production
- Questions must be challenging — candidates with surface knowledge should pick the wrong answer

Return ONLY a valid JSON array. No markdown. No code fences. No text before or after the JSON.
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "B",
    "explanation": "B is correct because [deterministic/structural reason]. A fails because [why it breaks in production]. C fails because [reason]. D fails because [reason]."
  }}
]"""

SIMULATION_GENERATION_PROMPT = """Generate exactly {n} multiple-choice exam questions for the Claude Certified Architect – Foundations (CCA-F) certification.

The real exam is 60 scenario-based questions, 120 minutes, pass score 720/1000.
Distribute questions by official domain weight:
- Agentic Architecture & Orchestration (27%): orchestration patterns, subagent context passing, programmatic enforcement via hooks, escalation design, stop_reason handling
- Tool Design & MCP Integration (18%): tool descriptions, structured error responses, MCP trust model, isError vs. JSON-RPC errors, lookup-then-act pattern
- Claude Code Configuration & Workflows (20%): CLAUDE.md hierarchy, PreToolUse hooks, Grep vs. Glob, Edit unique-match requirement, -p flag for CI, custom slash commands
- Prompt Engineering & Structured Output (20%): system prompt dilution, few-shot examples, JSON schema output, validation-retry loops, two-step reason-then-format
- Context Management & Reliability (15%): stateless API, progressive summarization vs. sliding window, structured case-facts, stale session handling, error propagation

Every question must:
- Drop the candidate into a PRODUCTION scenario
- Have 3 wrong answers that represent real engineering mistakes (all plausible)
- Test architectural judgment, not memorization
- The overriding principle: programmatic enforcement beats prompt-based guidance for anything that must hold 100% of the time

Return ONLY a valid JSON array. No markdown. No code fences. No text before or after the JSON.
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
    "answer": "A",
    "explanation": "Why A is correct and why B/C/D fail in production.",
    "category": "Agentic Architecture & Orchestration"
  }}
]"""

STUDY_PLAN_PROMPT = """Based on these exam scores by domain: {scores_json}

I am preparing for the Claude Certified Architect – Foundations (CCA-F) exam (60 questions, 120 min, pass score 720/1000 scaled ≈ 75%).

The 5 official domains by weight:
1. Agentic Architecture & Orchestration (27%)
2. Claude Code Configuration & Workflows (20%)
3. Prompt Engineering & Structured Output (20%)
4. Tool Design & MCP Integration (18%)
5. Context Management & Reliability (15%)

The single most-tested concept across all domains: programmatic/structural enforcement beats prompt-based guidance whenever consequences are financial, security-related, or compliance-related.

Give me a specific 7-day study plan. For each weak domain, specify:
- The exact concepts to focus on (not just the topic name)
- One or two concrete scenarios to practice reasoning through
- The anti-pattern to avoid

Be concise and actionable. Prioritize domains by weight × weakness."""
