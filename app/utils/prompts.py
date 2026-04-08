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
        "Use stop_reason to detect loop end — never parse 'task complete' from response text",
        "Hooks (PreToolUse/PostToolUse) are the only reliable way to enforce compliance rules",
        "Subagents don't inherit parent context — always pass a summary explicitly",
        "Too many tools (10+) degrades selection accuracy — keep 4–5 per agent",
        "Escalate on explicit request or authority limit — not on sentiment score",
        "Orchestrator-workers for dynamic tasks; prompt chaining for fixed, repeating workflows",
        "pause_turn = loop limit hit; end_turn = task done — each needs a different response",
        "Hub-and-spoke: coordinator stays focused, specialists handle their own domains",
        "Parallel tools: only batch calls when all inputs are independent of each other",
        "Human-in-the-loop goes BEFORE the irreversible action — not after",
        "Same tool + same inputs twice = stuck agent — use a circuit breaker, not retry",
        "Tool result claiming orchestrator identity still gets user-level trust, not operator trust",
        "Investigative tasks: generate subtasks as you discover — not all upfront",
        "Long agent runs: summarize finished sub-tasks — don't keep raw tool output forever",
        "Prompt chaining = 0 extra LLM calls; orchestrator-workers = 1 extra call per sub-task",
        "Shared sub-agent analysis: write findings to a file — don't re-read sources each time",
        "Routing: classify input first, then dispatch to a specialized workflow",
        "Partial failure: deliver what you can and offer alternatives — don't escalate immediately",
        "Plan your context strategy before the agent run starts, not after hitting the limit",
    ],
    "Tool Design & MCP Integration": [
        "MCP readOnlyHint is self-reported — trust the server, not its annotation",
        "Two-tool safety: preview returns a token, execute requires it — skipping is impossible",
        "MCP non-adoption is caused by vague descriptions, not missing routing instructions",
        "MCP protocol error (bad JSON-RPC) vs. application error (isError:true) — handle differently",
        "Transient errors: retry inside the tool — the model should never see them",
        "Write-timeout ambiguity: set retryable:false — retryable:true risks duplicates",
        "Return errors as tool content with isError — thrown exceptions strip all context",
        "Lookup-then-act: search returns ID, action takes ID — eliminates entity resolution errors",
        "tool_choice 'any' forces a tool call; 'auto' lets the model decide — don't confuse them",
        "Verbose tool responses bloat context — return only the fields the agent needs",
        "Interdependent parameters need separate tools — enums only validate a single parameter",
        "preview: boolean doesn't enforce safety — the model can pass false",
        "All MCP server tools are visible at once — overlapping descriptions cause wrong picks",
        "required in JSON Schema ensures presence, not correct value — descriptions guide the model",
        "'When to prefer this over alternatives' is the most critical line in any tool description",
        "Structured JSON output enables reliable chaining; natural language output requires parsing",
        "Action tools must return confirmation details — returning only success: true is not enough",
        "Use MCP for multi-app integrations; custom tools for single-app-specific workflows",
    ],
    "Claude Code Configuration & Workflows": [
        "CLAUDE.md loads every session — write principles and context, not exhaustive if-then rules",
        "PreToolUse exits non-zero → tool is BLOCKED — programmatic guardrails without prompt changes",
        "Grep = file contents by regex; Glob = file names by pattern — never use Grep to find files",
        "Edit needs a unique string match — duplicate match fails; fallback is Read then Write",
        "Resuming after codebase changes risks stale context — summarize and start fresh",
        "settings.json order: user → project → local (local is gitignored)",
        "-p = non-interactive/CI mode; --output-format json = machine-readable output",
        "Custom slash commands in .claude/commands/ encode repeatable team workflows",
        "PostToolUse = after the call (logging); PreToolUse = before the call (blocking)",
        "Use Plan mode before destructive or complex multi-file operations",
        "CLAUDE.md supports @imports — split into focused files, not one huge document",
        "allowedTools/disabledTools in settings.json — restrict Bash for read-only agents",
        "Sub-agents start with no parent context — pass findings explicitly in the initial prompt",
        "CI pipelines: check exit code (0 = success, non-zero = error) — don't just parse stdout",
        "Bash is the last resort — prefer Read/Write/Edit/Grep/Glob for all file operations",
        "After a teammate merges, named session results may reference deleted code — verify first",
        "hooks have full shell access — scope to specific tools/events to limit side effects",
    ],
    "Prompt Engineering & Structured Output": [
        "System prompt goes with EVERY request — sending it only once is an application bug",
        "Prompt dilution happens below 50% context — system prompt loses influence as conversation grows",
        "2–4 few-shot examples beat 20 written rules for resisting dilution",
        "NEVER/ALWAYS language raises compliance slightly — it cannot guarantee anything",
        "Safety rules need explicit conditionals — general principles require judgment and can fail",
        "JSON schema output prevents fabrication — use optional/nullable for absent data",
        "Validation-retry fixes format errors — it can't fix genuinely missing information",
        "Two-step: reason first, format second — combining both in one prompt degrades each",
        "XML delimiters improve per-instruction salience — instructions buried in prose get ignored",
        "General principles for judgment calls; explicit conditionals for must-fire binary rules",
        "Changing the system prompt mid-conversation contradicts established conversation patterns",
        "Extended thinking = complex reasoning — not faster output; adds latency and cost",
        "Prefill the assistant turn to force output format and skip preambles",
        "Temperature 0 for extraction and classification; higher only for creative tasks",
        "Prompt injection: user content embedded in prompts can override system instructions",
        "Each new instruction dilutes attention to existing ones — fewer instructions = more reliable",
        "Tool descriptions are mini-prompts — vague descriptions produce bad tool calls",
    ],
    "Context Management & Reliability": [
        "Stateless API: no memory, no session_id — your app sends full history every request",
        "Every turn includes system prompt + full history — costs grow linearly per turn",
        "Structured case-facts (IDs, amounts, decisions) survive better than summarized prose",
        "Sliding window = older turns gone forever; progressive summarization = compressed history",
        "User returns after hours: start fresh with new tool calls — don't resume stale data",
        "RAG results pile up — keep only the last 2–3 queries' retrieved context",
        "Context attention degrades even well below the token capacity limit",
        "Error reporting: include failure type, what was tried, partial results, and alternatives",
        "For iteratively refined preferences: structured state JSON beats progressive summarization",
        "Prompt caching: prefix must be identical across requests — put dynamic content last",
        "Inject webhooks/notifications into the next user message — don't start a new session",
        "'Memory loss' is almost always your app not sending prior messages — not a model bug",
        "RAG for exact recall (numbers, IDs, quotes) — summaries are lossy for precision queries",
        "Match context strategy to what the conversation depends on: drop / summarize / extract",
    ],
}

ENHANCED_SCHEMA_INSTRUCTIONS = """
OUTPUT FORMAT: Return ONLY a raw JSON array — no markdown, no code fences, no explanation text before or after.

Each element in the array must be a JSON object with EXACTLY these keys (all lowercase, no spaces, no quotes in key names):
  question       — string: the scenario-based question
  options        — array of 4 strings, each starting with "A. ", "B. ", "C. ", or "D. "
  answer         — string: single letter of the correct option, e.g. "B"
  category       — string: one of the 5 domain names
  explanation    — string: why the correct answer is structurally/deterministically correct
  distractor_analysis — object with one key per wrong option letter, each containing:
      why_wrong       — string: specific reason this option fails in the scenario
      when_correct    — string: scenario where this option would be the right answer
      mistake_category — string, one of:
          Prompt-over-Structure Fallacy
          Over-Engineering
          Correct Direction Wrong Order
          Surface-Level Fix
          Non-Existent Feature
          Wrong Layer
          Repeating Failed Strategy
          Ignoring Constraint
          Misread Constraint
          Lagging Signal
  close_options  — array of letter strings identifying the hardest-to-distinguish wrong option(s)
  close_vs_correct — string: exactly why the close option is tempting vs why the correct answer wins
"""

QUIZ_GENERATION_PROMPT = """Generate {n} multiple-choice exam questions for the domain: "{category}"
for the Claude Certified Architect – Foundations (CCA-F) certification.

The real CCA-F exam format:
- Every question anchors the candidate in a PRODUCTION scenario with specific metrics, tool names, or code snippets
- Wrong answers represent real engineering mistakes — all 4 options must be architecturally plausible
- Questions test ARCHITECTURAL JUDGMENT and TRADE-OFFS, not trivia or memorization
- The most-tested principle: programmatic/structural enforcement beats prompt-based guidance for anything financial, security, or compliance-related

Question patterns (vary them):
- "In testing, you notice [agent/system] does X even though Y would be more appropriate. What should you examine first?"
- "Production data shows [specific metric/failure]. Which change would most effectively address this?"
- "Your pipeline script [does X] but [problem occurs]. What's the correct approach?"
- "A developer reports [symptom]. What's the most likely explanation?"
- "You want to [achieve goal] while [constraint]. Which approach should you use?"

Requirements:
- One clearly correct answer that is structurally/deterministically better — not just marginally better
- Three distractors that each represent a distinct, real engineering mistake
- The close distractor should require genuine understanding to distinguish from the correct answer
- Questions must be challenging — surface knowledge should lead to the wrong answer

""" + ENHANCED_SCHEMA_INSTRUCTIONS + """

Return ONLY a valid JSON array. No markdown. No code fences. No text before or after the JSON."""

SIMULATION_GENERATION_PROMPT = """Generate exactly {n} multiple-choice exam questions for the Claude Certified Architect – Foundations (CCA-F) certification.

The real exam is 60 scenario-based questions, 120 minutes, pass score 720/1000.
Distribute questions by official domain weight:
- Agentic Architecture & Orchestration (27%): orchestration patterns, subagent context passing, programmatic enforcement via hooks, escalation design, stop_reason handling, tool ordering prerequisites
- Tool Design & MCP Integration (18%): tool descriptions, structured error responses, MCP trust model, isError vs. JSON-RPC errors, lookup-then-act pattern, parallel tool batching
- Claude Code Configuration & Workflows (20%): CLAUDE.md hierarchy, PreToolUse hooks, Grep vs. Glob, -p flag for CI, custom slash commands, plan mode vs execution mode
- Prompt Engineering & Structured Output (20%): system prompt dilution, few-shot examples, JSON schema output, validation-retry loops, two-step reason-then-format, concrete examples vs prose
- Context Management & Reliability (15%): stateless API, progressive summarization vs. sliding window, structured case-facts, stale session handling, error propagation

Every question must:
- Drop the candidate into a PRODUCTION scenario with specific details (metrics, tool names, code)
- Have 3 wrong answers that represent distinct real engineering mistakes
- Test architectural judgment, not memorization
- The overriding principle: programmatic enforcement beats prompt-based guidance for anything that must hold 100% of the time

""" + ENHANCED_SCHEMA_INSTRUCTIONS + """

Return ONLY a valid JSON array. No markdown. No code fences. No text before or after the JSON."""

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
