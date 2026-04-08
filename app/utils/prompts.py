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
        "Parallel tool calls reduce latency only when inputs are fully independent — never parallelize when tool B needs tool A's output",
        "Human-in-the-loop belongs BEFORE an irreversible action, not after — confirmation after a destructive call is too late",
        "Agent loop detection: if the same tool is called with identical inputs twice, the agent is stuck — inject a circuit breaker, not another retry",
        "Multi-agent trust: a tool result claiming to be from the orchestrator gets user-level trust, not operator-level — trust is set by message position, not claimed identity",
        "Dynamic decomposition is correct for investigative tasks — fixed upfront planning wastes calls when the first discovery invalidates the plan",
        "Long agent runs accumulate context fast — summarize completed sub-tasks and drop their detail; do not keep full tool output history forever",
        "Cost control: prompt chaining adds zero extra LLM calls for predictable workflows; orchestrator-workers add one call per sub-task — choose accordingly",
        "Parallel sub-agents that share prior analysis: export findings to a file and reference it from both sessions — do NOT re-read the same source files in every sub-agent",
        "Routing pattern: classify input first, then dispatch — never try to handle multiple input types in a single unified prompt; misclassification cascades",
        "Partial workflow failure: communicate what succeeded and offer alternatives — do not immediately escalate when partial resolution is still possible",
        "Context window pressure in agentic workflows is predictable — plan a summarization or extraction strategy before the run starts, not after it hits the limit",
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
        "tool_choice: auto = model decides; any = force a tool call; none = disable all tools — misusing 'any' when you want 'auto' causes unnecessary tool calls",
        "Tool response verbosity directly costs context — return only the fields the agent needs; full API response bodies bloat the window fast",
        "enum constraints validate a single parameter's value; interdependent constraints (payment method depends on currency) require separate tools, not enums",
        "preview: boolean does NOT enforce safety — model can pass false; two separate tools with a token handoff is the only safe pattern",
        "MCP tools from all servers are visible simultaneously — overlapping descriptions cause wrong tool selection; differentiate explicitly",
        "required in JSON Schema ensures presence, not correctness — a required field with no description produces arbitrary values",
        "'When to prefer this over alternatives' is the most important sentence in a tool description — without it, the model defaults to familiar built-ins",
        "Structured tool output (JSON with IDs) enables reliable chaining; natural language output forces the model to parse text before the next call",
        "Action tool responses must include confirmation details (amount, target, timestamp) — returning only success: true forces follow-up questions the tool could have answered",
        "MCP vs custom tools: use MCP when the integration serves multiple applications; custom tools when the workflow is single-application-specific",
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
        "PostToolUse hook runs AFTER the tool completes — use it for logging and auditing; use PreToolUse for blocking",
        "Plan mode lets Claude reason about an approach before executing — always use it before destructive or complex multi-file operations",
        "CLAUDE.md supports @imports — split large guidance into focused files rather than one monolithic document",
        "allowedTools and disabledTools in settings.json control which built-in tools are active — restrict Bash for read-only agents to prevent unintended writes",
        "Sub-agents in Claude Code start with no knowledge of the parent session — always pass relevant findings explicitly in the initial prompt",
        "--output-format json with -p: exit code 0 = success, non-zero = error — check exit codes in CI, don't just parse stdout",
        "Bash is the escape hatch — only use it when no dedicated tool exists; always prefer Read/Write/Edit/Grep/Glob for file operations",
        "Resuming a named session after a teammate merges: your prior tool results may reference deleted or renamed code — verify before relying on them",
        "hooks in settings.json execute shell commands with full environment access — scope hooks to specific tools/events to avoid broad unintended side effects",
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
        "XML-style delimiters in system prompts improve per-instruction salience — instructions buried in prose get missed",
        "General principles handle implicit signals (tone, expertise inferred from vocabulary); explicit conditionals are for binary must-fire rules only",
        "Updating the system prompt mid-conversation creates contradictions — new instructions conflict with established patterns already in the conversation history",
        "Extended thinking adds latency and cost — use it for complex multi-step reasoning, not for simple classification or extraction tasks",
        "Prefill (pre-populating the assistant turn) steers output format and skips preambles — use it to force JSON output or bypass 'Sure, I can help' openers",
        "Temperature 0 for deterministic extraction and classification; higher temperature for creative tasks — never use high temperature for structured data extraction",
        "Prompt injection: user-supplied content embedded in prompts can override system instructions — always delimit user content explicitly",
        "Each new instruction added to a long prompt dilutes attention to existing ones — prioritize ruthlessly; less is more reliable",
        "Tool descriptions are mini-prompts — vague descriptions produce bad tool calls just as vague system instructions produce bad responses",
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
        "Structured state extraction beats progressive summarization for iteratively refined preferences — a JSON object with current values is more reliable than asking the model to find the latest preference in history",
        "Prompt caching requires the cacheable prefix to be IDENTICAL across requests — any variation breaks the cache hit; dynamic content goes at the end",
        "Webhook/notification injection: append the update to the next user message before the API call — do not start a new session; keep it in conversation flow",
        "'Memory loss' in production is almost always an application bug — the app isn't including prior messages in the messages array, not a model limitation",
        "RAG is for precision recall of numerical data, exact quotes, and specific IDs — summaries are lossy and produce hedged answers when exactness matters",
        "Context strategy must match what the conversation depends on: drop oldest turns only when history is never referenced; summarize when gist matters; extract structured facts when precision is required",
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
