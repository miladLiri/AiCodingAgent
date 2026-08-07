<!--
SYNC IMPACT REPORT
==================
Version change: (unversioned template) → 1.0.0  [INITIAL RATIFICATION]
Bump rationale: First concrete ratification. All template placeholders replaced
  with project-specific governance derived from the codebase and author intent.

Principles defined (replacing template placeholders):
  - [PRINCIPLE_1] → I. Four-Pillar Harness Architecture
  - [PRINCIPLE_2] → II. Single Composition Root
  - [PRINCIPLE_3] → III. LangChain as the Core Framework
      (NOTE: default template's "Test-First (NON-NEGOTIABLE)" was intentionally
       NOT adopted — see Principle V and Development Workflow test policy)
  - [PRINCIPLE_4] → IV. Abstraction-Driven Extensibility
      (NOTE: default template's "Integration Testing" was intentionally NOT adopted)
  - [PRINCIPLE_5] → V. Guarded, Fail-Soft Tool Execution

Sections defined:
  - [SECTION_2] → Technology & Configuration Constraints
  - [SECTION_3] → Development Workflow & Quality Gates

Removed sections: none (all template slots filled).

Deferred TODOs: none. RATIFICATION_DATE set to first adoption date (2026-08-08).

Consistency check with dependent templates:
  - .specify/templates/plan-template.md — no constitution-specific tokens require change.
  - .specify/templates/spec-template.md — spec is the sole authorized origin for any
    test/eval work (per Development Workflow); no change needed.
  - .specify/templates/tasks-template.md — tasks MUST NOT introduce tests/evals absent
    a spec that requires them; reviewers enforce at compliance review.
-->

# AI Agent Harness Constitution

## Core Principles

### I. Four-Pillar Harness Architecture

The harness is composed of exactly four pillars — **LLM**, **Memory**, **Tools**, and
**Loop** — and each pillar lives in its own top-level package under `src/`
(`src/llms/`, `src/memory/`, `src/tools/`, `src/loops/`). Every new capability MUST
belong to exactly one pillar. Cross-pillar interaction MUST happen only through a
pillar's public classes; a pillar MUST NOT reach into another pillar's internals or
duplicate another pillar's responsibility.

Rationale: The four pillars are the mental model of the whole system. Keeping them
physically separated and single-purpose makes each one independently understandable
and replaceable without disturbing the others.

### II. Single Composition Root

All pillars are instantiated and wired together in exactly one place: `src/harness.py`
(`Harness.__init__`). Components MUST receive their collaborators via constructor
injection and MUST NOT construct their own dependencies internally. The entry point
(`main.py`) MUST do nothing beyond building a `Harness` and calling `run()`.

Rationale: A single wiring point makes the system's structure legible at a glance and
lets any pillar or strategy be swapped by editing one file. Constructor injection keeps
pillars decoupled and substitutable.

### III. LangChain as the Core Framework

LangChain is the single core framework and its primitives are non-negotiable. All
conversation state MUST use LangChain message types (`BaseMessage`, `HumanMessage`,
`AIMessage`, `ToolMessage`). All tools MUST be LangChain `BaseTool` instances (normally
via the `@tool` decorator). All model access MUST go through LangChain chat clients
(e.g. `ChatOpenAI`). Parallel or ad-hoc message/tool/model abstractions MUST NOT be
introduced.

Rationale: One shared vocabulary of primitives is what lets the four pillars
interoperate cleanly. Competing abstractions would force adapter code at every seam and
erode the harness's coherence.

### IV. Abstraction-Driven Extensibility

Pluggable behavior MUST extend the system behind stable seams, never by editing
consumers. New memory-compression strategies MUST subclass `BaseMemoryCompressor`; new
tools MUST be added through `ToolRegistry`; new loops and LLM wrappers MUST honor the
existing class contracts. Consumers MUST depend on the abstraction (base class or
registry), not on concrete implementations.

Rationale: The harness is meant to grow — more tools, more strategies, more models.
Extending behind interfaces lets it grow additively, without ripple edits to code that
is already working.

### V. Guarded, Fail-Soft Tool Execution

Tools MUST execute only through the loop's execution path via the `ToolExecutionGuard`.
Any tool registered as dangerous MUST require explicit human confirmation before it
runs. Tools MUST report failures by returning an error string, not by raising, so the
tool-calling loop stays alive and the model can observe and react to the failure.

Rationale: A human stays in control of risky actions, and a single misbehaving tool can
never crash the agent — the loop degrades gracefully instead of terminating.

## Technology & Configuration Constraints

- **Language & framework**: Python with LangChain (`langchain`, `langchain-openai`) as
  the core framework. Model access is OpenAI-compatible via `ChatOpenAI` with a
  configurable `base_url` and model name.
- **Configuration & secrets**: All configuration and secrets MUST be read from
  environment variables surfaced through `src/config.py` (loaded from `.env`). Secrets
  MUST NOT be hardcoded in source or committed to the repository.
- **Dependencies**: Runtime dependencies MUST be declared in `requirements.txt`. New
  third-party dependencies SHOULD be justified against the LangChain-first principle
  before adoption.

## Development Workflow & Quality Gates

- **Testing & eval policy (explicit)**: This project ships **no** automated tests or
  evals by default. Test code, eval harnesses, and test/CI gates MUST NOT be introduced
  speculatively. They are added ONLY when a specific, approved spec explicitly requires
  them; absent such a spec, changes are validated manually by running the harness
  (`python main.py`). This is a deliberate scope decision, not an oversight.
- **Change origination**: New features SHOULD flow through the Spec Kit lifecycle
  (`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`).
- **Structural invariants**: Every change MUST preserve the four-pillar boundaries
  (Principle I) and route all wiring through the single composition root (Principle II).
  Functional changes belong inside a pillar; assembly changes belong in `src/harness.py`.

## Governance

This constitution supersedes other conventions and ad-hoc practices. When a proposed
change conflicts with a principle here, the principle wins unless the constitution is
first amended.

- **Amendments**: Changes to this document MUST be made deliberately, versioned under
  the policy below, and reflected in the version line and Sync Impact Report.
- **Versioning policy** (semantic versioning): **MAJOR** for backward-incompatible
  governance changes (removing or redefining a principle); **MINOR** for a new principle
  or materially expanded section; **PATCH** for clarifications and non-semantic edits.
- **Test/eval authorization**: Any requirement to add tests or evals MUST originate from
  an approved spec (per the Development Workflow policy). Reviews MUST reject test/eval
  code that lacks such a spec.
- **Compliance review**: Reviews and PRs MUST verify pillar boundaries (I), the single
  composition root and dependency injection (II), LangChain-only primitives (III),
  extension behind abstractions (IV), and guarded fail-soft tool execution (V). Any
  deviation MUST be justified in the relevant spec or plan.

**Version**: 1.0.0 | **Ratified**: 2026-08-08 | **Last Amended**: 2026-08-08
