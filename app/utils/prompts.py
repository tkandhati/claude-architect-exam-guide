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
        "Check the stop_reason field to detect when an agent loop ends — never parse 'task complete' from the response text",
        "Programmatic hooks (PreToolUse/PostToolUse) are the only reliable way to enforce financial or compliance rules",
        "Sub-agents don't automatically know what the parent agent learned — always pass a context summary explicitly",
        "Giving an agent 10+ tools degrades selection accuracy — the sweet spot is 4–5 tools per agent",
        "Escalate to a human when the customer asks or the issue exceeds authority limits — not based on sentiment score",
        "Use orchestrator-workers when steps are unknown upfront; use prompt chaining when steps are always the same",
        "pause_turn means the server hit a loop limit and needs resuming; end_turn means the task completed — handle them differently",
        "Hub-and-spoke: the coordinator delegates to domain specialists and stays context-focused itself",
        "Batch parallel tool calls only when all inputs are fully independent — never when one tool needs another's output",
        "Human-in-the-loop confirmation belongs BEFORE the irreversible action fires — not after",
        "If the same tool is called with the same inputs twice, the agent is stuck in a loop — use a circuit breaker, not another retry",
        "In multi-agent systems, a tool result claiming to come from the orchestrator still gets user-level trust — trust is set by message position, not claimed identity",
        "For investigative tasks (debugging, exploration), generate subtasks as you discover — don't plan everything upfront",
        "In long agent runs, summarize completed sub-tasks and discard their raw output — don't let tool history fill the context window",
        "Prompt chaining adds zero extra LLM calls; orchestrator-workers add one LLM call per sub-task — factor this into cost",
        "When two sub-agents share prior analysis, write findings to a file they both reference — don't re-read source files in each session",
        "Routing pattern: classify the input type first, then dispatch to a specialized workflow — one prompt for all types causes failures",
        "On partial workflow failure, communicate what succeeded and offer alternatives — don't immediately escalate when partial resolution is possible",
        "Decide your context management strategy (summarize, extract, drop) before the agent run starts — not after hitting the limit",
    ],
    "Tool Design & MCP Integration": [
        "MCP readOnlyHint is declared by the server itself — a rogue server can lie, so base trust on the server, not its own label",
        "For destructive operations, use two separate tools: preview generates a one-time token, execute requires that token — skipping the preview becomes impossible",
        "When agents ignore MCP tools and use built-ins instead, the root cause is almost always a vague tool description",
        "MCP has two error tiers: protocol errors (bad JSON-RPC format) and application errors (isError:true in the result) — they require different handling",
        "For transient failures like network timeouts, retry with backoff inside the tool itself — the model should never see these",
        "When a write operation times out and you don't know if it succeeded, set retryable:false — retryable:true risks sending duplicates",
        "Return errors inside the tool's content field with isError:true — throwing exceptions strips the error detail before it reaches the model",
        "Lookup-then-act pattern: a search tool returns a specific record ID, and the action tool takes that ID — avoids errors from matching by name",
        "tool_choice 'any' forces the model to call a tool; 'auto' lets it decide — using 'any' when you mean 'auto' causes unnecessary calls",
        "Returning the full API response from a tool bloats the context window — return only the fields the agent actually needs",
        "When parameters are interdependent (e.g., payment type depends on currency), split into separate tools — enums can't capture cross-parameter rules",
        "A preview:boolean flag doesn't enforce safety — the model can pass false and skip the preview; use the two-tool token pattern instead",
        "All tools from all connected MCP servers are visible to the agent at the same time — overlapping descriptions cause the model to pick the wrong one",
        "The JSON Schema 'required' field only guarantees the parameter is present — it doesn't help the model choose the right value; descriptions do that",
        "The single most important line in a tool description is when to prefer it over built-in alternatives — without it, the model defaults to familiar tools",
        "Tool responses with structured JSON (including IDs) enable reliable chaining; natural language responses force the model to parse text before the next call",
        "Action tool responses must include confirmation details like amount, target, and timestamp — returning only success:true forces unnecessary follow-up questions",
        "Use MCP when the integration needs to serve multiple applications; use a custom tool when it is specific to one application's workflow",
    ],
    "Claude Code Configuration & Workflows": [
        "CLAUDE.md is loaded at the start of every session — write high-level principles and project context, not long if-then rules",
        "When a PreToolUse hook exits with a non-zero code, the tool call is blocked — this is how you enforce guardrails without changing any prompts",
        "Grep searches inside file contents by regex pattern; Glob finds files by name or path pattern — never use Grep when you mean Glob",
        "The Edit tool requires a unique string match — if the target string appears more than once, Edit fails; fall back to Read then Write",
        "Resuming an old session after the codebase changed risks referencing renamed or deleted code — summarize prior findings and start a fresh session",
        "settings.json loads in this order: user-level → project-level → local (local is gitignored and won't be committed)",
        "The -p flag puts Claude Code in non-interactive mode for CI pipelines; add --output-format json for machine-readable results",
        "Team workflows can be encoded as custom slash commands stored in .claude/commands/ and shared via version control",
        "PostToolUse hooks run after the tool completes and are good for logging; PreToolUse hooks run before and are used for blocking",
        "Use Plan mode to have Claude think through an approach before executing — especially before destructive or multi-file operations",
        "CLAUDE.md supports @file imports — break large guidance into focused files rather than one monolithic document",
        "Use allowedTools and disabledTools in settings.json to control which built-in tools an agent can access — restrict Bash for read-only agents",
        "Sub-agents in Claude Code start with no knowledge of the parent session — pass the relevant findings in the initial prompt explicitly",
        "In CI pipelines, always check the exit code (0 = success, non-zero = error) — don't rely on parsing stdout alone",
        "Bash is the escape hatch for shell operations — for file work, always prefer the dedicated tools: Read, Write, Edit, Grep, Glob",
        "After a teammate merges changes, a named session's prior tool results may reference code that no longer exists — verify before relying on them",
        "Claude Code hooks execute shell commands with full environment access — scope each hook to specific tools or events to prevent unintended side effects",
    ],
    "Prompt Engineering & Structured Output": [
        "The system prompt is included in every API request — if your app only sends it on the first turn, that is a bug",
        "System prompt influence fades as a conversation grows, even when you are well below the context limit",
        "2–4 concrete few-shot examples in the system prompt outlast 20 written rules as conversation length increases",
        "Writing NEVER or ALWAYS in a system prompt slightly increases compliance but cannot guarantee it — use programmatic enforcement for hard rules",
        "Safety-critical rules need explicit conditionals that fire deterministically — general principles leave room for the model to use judgment and sometimes fail",
        "Using a JSON schema for output prevents the model from fabricating fields — mark fields that may be absent as optional or nullable",
        "A validation-retry loop fixes format errors effectively — it cannot recover information that is genuinely absent from the source",
        "Ask the model to reason first, then format the output in a second step — combining reasoning and formatting in one prompt degrades both",
        "Use XML-style section tags in system prompts to make each instruction stand out — instructions buried in plain prose are more likely to be missed",
        "Use general principles when the model needs to apply judgment to varied situations; use explicit conditionals when a rule must fire every single time",
        "Updating the system prompt mid-conversation creates contradictions between new instructions and the patterns already established in the conversation",
        "Extended thinking is for complex multi-step reasoning problems — it adds latency and cost and is not appropriate for simple extraction or classification",
        "Prefilling the assistant turn (providing its opening words) forces a specific output format and skips verbose preambles like 'Sure, I can help with that'",
        "Use temperature 0 for extraction, classification, or any task requiring consistent output — reserve higher temperatures for creative generation",
        "Prompt injection risk: if user-supplied text is embedded in your prompt without delimiters, it can override your system instructions",
        "Every new instruction you add to a long system prompt dilutes the model's attention to all existing ones — prioritize and cut aggressively",
        "Tool descriptions function like mini system prompts — a vague description produces bad tool calls just as a vague system prompt produces bad responses",
    ],
    "Context Management & Reliability": [
        "The Claude API is stateless — there is no built-in memory or session; your application must send the full conversation history every request",
        "Every API call includes the system prompt plus the entire conversation history — input token costs grow with every turn",
        "Preserving key facts (IDs, amounts, decisions) as structured data is more reliable than including them only in a narrative summary",
        "Sliding window discards older turns completely; progressive summarization compresses them — know which trade-off your use case can tolerate",
        "When a user returns after a long gap, start a new session with fresh tool calls — resuming with hours-old tool results risks acting on stale data",
        "Retrieved context (RAG) accumulates across turns and crowds out real conversation — keep only the last 2–3 queries' results",
        "Context attention degrades as conversation length grows, even when you are comfortably under the token limit",
        "When a tool fails, report the failure type, what was attempted, any partial results, and suggested alternatives — never silently suppress errors",
        "When users iteratively refine preferences, maintain a structured JSON state object — don't ask the model to find the most recent value buried in history",
        "Prompt caching requires the cacheable prefix to be byte-identical across requests — even a small variation breaks the cache; put dynamic content at the end",
        "Inject external updates (webhooks, notifications) into the next user message before the API call — don't start a new session just to deliver an update",
        "When a model appears to forget something, the cause is almost always your app not including prior messages — not a model limitation",
        "Use retrieval (RAG) when you need exact numbers, IDs, or quotes — summaries lose precision and produce hedged answers to specific questions",
        "Match your context strategy to what the conversation actually depends on: drop old turns only if history doesn't matter; summarize when gist is enough; extract structured facts when precision is required",
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

TRUE_FALSE_QUESTIONS = {
    "Agentic Architecture & Orchestration": [
        {"q": "Sub-agents automatically inherit the full context of their parent agent.", "a": False},
        {"q": "The stop_reason field is the reliable way to detect when an agent loop ends.", "a": True},
        {"q": "Prompt instructions are equally reliable as programmatic hooks for enforcing compliance rules.", "a": False},
        {"q": "Assigning 10+ tools to a single agent improves its overall capability.", "a": False},
        {"q": "pause_turn and end_turn both signal that the agent has finished its task.", "a": False},
        {"q": "Human-in-the-loop confirmation should happen after an irreversible action to review what was done.", "a": False},
        {"q": "Orchestrator-workers is the best pattern when workflow steps repeat the same way every time.", "a": False},
        {"q": "When an agent calls the same tool with the same inputs twice in a row, retrying is the correct response.", "a": False},
        {"q": "In hub-and-spoke architecture, the coordinator agent handles all domain tasks directly.", "a": False},
        {"q": "A tool result claiming to come from the orchestrator receives operator-level trust automatically.", "a": False},
        {"q": "For investigative tasks like debugging, creating a complete plan upfront before starting is best.", "a": False},
        {"q": "Parallel tool calls reduce latency regardless of whether the inputs are independent of each other.", "a": False},
        {"q": "Prompt chaining adds one extra LLM call per step compared to direct orchestration.", "a": False},
        {"q": "When a partial workflow fails, the correct first response is to immediately escalate to a human.", "a": False},
        {"q": "Two parallel sub-agents needing shared prior analysis should each re-read the source files independently.", "a": False},
        {"q": "Context window management should be planned before a long agent run begins.", "a": True},
        {"q": "The routing pattern works best with a single unified prompt that handles all input types together.", "a": False},
        {"q": "Escalating based on a high sentiment frustration score is a reliable trigger for human handoff.", "a": False},
        {"q": "PostToolUse hooks are the correct mechanism for blocking tool calls before they execute.", "a": False},
        {"q": "In multi-agent systems, a message's trust level is determined by its position in the conversation.", "a": True},
        {"q": "pause_turn means the server hit a loop limit and the agent run needs to be resumed.", "a": True},
        {"q": "Orchestrator-workers cost more LLM calls per workflow than prompt chaining for equivalent fixed tasks.", "a": True},
        {"q": "Dynamic decomposition generates all subtasks upfront before beginning investigative work.", "a": False},
    ],
    "Tool Design & MCP Integration": [
        {"q": "The MCP readOnlyHint annotation is a verified security guarantee from the protocol.", "a": False},
        {"q": "A preview:boolean flag on a single tool reliably enforces the preview step.", "a": False},
        {"q": "Transient errors like network timeouts should be returned to the model so it can decide to retry.", "a": False},
        {"q": "When a write operation times out with an unknown outcome, setting retryable:true is safe.", "a": False},
        {"q": "Throwing an exception from a tool is the best way to communicate errors to the model.", "a": False},
        {"q": "If agents ignore your MCP tools, adding routing instructions to the system prompt is the fix.", "a": False},
        {"q": "A 'required' field in JSON Schema guarantees the model will provide a correct value.", "a": False},
        {"q": "The lookup-then-act pattern passes a free-text name from the search tool to the action tool.", "a": False},
        {"q": "MCP tools from different servers are discovered one server at a time during each agent turn.", "a": False},
        {"q": "tool_choice 'any' and 'auto' produce the same model behavior.", "a": False},
        {"q": "Returning the full API response body from a tool helps the model make better decisions.", "a": False},
        {"q": "Enum constraints in a JSON schema can capture interdependencies between two parameters.", "a": False},
        {"q": "All MCP server tools are visible to the agent simultaneously in one flat list.", "a": True},
        {"q": "Structured JSON tool output enables reliable chaining between sequential tool calls.", "a": True},
        {"q": "Returning only 'success: true' from an action tool is sufficient for a good user experience.", "a": False},
        {"q": "MCP is best suited for integrations specific to a single application.", "a": False},
        {"q": "A well-written tool description should explain when to prefer it over built-in alternatives.", "a": True},
        {"q": "Protocol-level MCP errors and application-level errors are reported the same way.", "a": False},
        {"q": "Natural language tool responses are easier for the model to chain into subsequent calls.", "a": False},
        {"q": "Splitting interdependent parameters into separate tools prevents invalid combinations structurally.", "a": True},
        {"q": "MCP provides built-in authentication, retry logic, and rate limiting out of the box.", "a": False},
        {"q": "isError:true in a tool result signals an application-level error, not a protocol error.", "a": True},
        {"q": "The most common reason MCP tools are not adopted is missing system prompt routing instructions.", "a": False},
    ],
    "Claude Code Configuration & Workflows": [
        {"q": "CLAUDE.md is only loaded once at project creation, not at the start of every session.", "a": False},
        {"q": "Grep is the right tool for finding files by their name or path pattern.", "a": False},
        {"q": "The Edit tool works correctly even if the target string appears multiple times in the file.", "a": False},
        {"q": "When a PreToolUse hook exits with code 0, the tool call is blocked.", "a": False},
        {"q": "Project-level settings.json overrides user-level settings.", "a": True},
        {"q": "The -p flag is used to enable streaming output in interactive sessions.", "a": False},
        {"q": "Custom slash commands in .claude/commands/ are automatically available across all projects.", "a": False},
        {"q": "PostToolUse hooks are the correct way to block a tool call before it executes.", "a": False},
        {"q": "Resuming a named session is always safe even after teammates have merged code changes.", "a": False},
        {"q": "The Bash tool should be the first choice for file reading operations.", "a": False},
        {"q": "CLAUDE.md supports importing other markdown files using @filepath syntax.", "a": True},
        {"q": "allowedTools in settings.json controls which built-in tools an agent can access.", "a": True},
        {"q": "--output-format json combined with -p produces machine-readable JSON for pipeline use.", "a": True},
        {"q": "Sub-agents in Claude Code automatically have access to the parent session's conversation history.", "a": False},
        {"q": "In CI pipelines, parsing stdout is sufficient to determine if Claude Code succeeded.", "a": False},
        {"q": "Plan mode allows Claude to reason about an approach before executing any changes.", "a": True},
        {"q": "hooks in settings.json run with limited environment access for security.", "a": False},
        {"q": "The local settings file (.claude/settings.local.json) should be committed to version control.", "a": False},
        {"q": "Glob searches inside file contents to find matching patterns.", "a": False},
        {"q": "When Edit fails due to a duplicate string match, the correct fallback is Read then Write.", "a": True},
    ],
    "Prompt Engineering & Structured Output": [
        {"q": "The system prompt is sent only with the first API request to reduce token costs.", "a": False},
        {"q": "System prompt compliance remains stable regardless of how long the conversation grows.", "a": False},
        {"q": "Writing NEVER or ALWAYS in a system prompt guarantees the rule will be followed.", "a": False},
        {"q": "Few-shot examples resist prompt dilution better than written rules as conversation grows.", "a": True},
        {"q": "For safety-critical rules, general principles are more reliable than explicit conditionals.", "a": False},
        {"q": "A validation-retry loop can recover information that was never present in the source document.", "a": False},
        {"q": "Asking the model to reason and format output simultaneously is more efficient.", "a": False},
        {"q": "XML-style section tags in a system prompt improve individual instruction compliance.", "a": True},
        {"q": "A general principle is the right choice when a rule must fire 100% of the time.", "a": False},
        {"q": "Extended thinking increases response speed by enabling deeper pre-computation.", "a": False},
        {"q": "Temperature 0 is recommended for creative writing tasks.", "a": False},
        {"q": "Prefilling the assistant turn can be used to force a specific output format.", "a": True},
        {"q": "Adding more instructions to a system prompt always improves model reliability.", "a": False},
        {"q": "Updating the system prompt mid-conversation is always safe.", "a": False},
        {"q": "Prompt injection only occurs when attackers have direct access to the system prompt.", "a": False},
        {"q": "Using optional/nullable fields in a JSON schema prevents the model from fabricating absent data.", "a": True},
        {"q": "System prompt influence degrades only when the conversation nears the token limit.", "a": False},
        {"q": "Tool descriptions have no impact on which tool the model selects.", "a": False},
        {"q": "Each new instruction added to a long system prompt dilutes attention to existing ones.", "a": True},
        {"q": "The two-step pattern (reason first, then format) improves output quality over doing both at once.", "a": True},
    ],
    "Context Management & Reliability": [
        {"q": "The Claude API maintains conversation state between requests automatically.", "a": False},
        {"q": "Token costs stay constant as a conversation grows longer.", "a": False},
        {"q": "When a user returns after several hours, it is safe to resume using the existing tool results.", "a": False},
        {"q": "Sliding window context management preserves compressed summaries of older turns.", "a": False},
        {"q": "RAG retrieved context should be accumulated across all turns for maximum accuracy.", "a": False},
        {"q": "Context attention degrades only when nearing the token capacity limit.", "a": False},
        {"q": "When a model appears to forget something, it is usually a model bug.", "a": False},
        {"q": "Structured JSON state objects are more reliable than conversation history for tracking user preferences.", "a": True},
        {"q": "Progressive summarization is the best strategy when users need exact recall of specific numbers.", "a": False},
        {"q": "Prompt caching works even if the cached prefix changes slightly between requests.", "a": False},
        {"q": "External webhook notifications should trigger a new conversation session.", "a": False},
        {"q": "Structured error reporting should include failure type, what was attempted, partial results, and alternatives.", "a": True},
        {"q": "When users iteratively refine preferences, progressive summarization is the most reliable strategy.", "a": False},
        {"q": "The Claude API is stateless — there is no built-in session or memory between calls.", "a": True},
        {"q": "Input token costs include both the system prompt and the full conversation history on every turn.", "a": True},
        {"q": "Sliding window and progressive summarization both preserve older turns in compressed form.", "a": False},
        {"q": "RAG retrieval is appropriate when users need exact numbers or specific IDs recalled accurately.", "a": True},
        {"q": "Prompt caching requires the cached prefix to be byte-identical across requests.", "a": True},
        {"q": "Injecting a webhook update by appending it to the next user message is the recommended pattern.", "a": True},
        {"q": "Context attention remains reliable as long as you are under 50% of the token capacity.", "a": False},
    ],
}
