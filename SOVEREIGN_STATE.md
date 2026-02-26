# Sovereign State Blueprint (Bret Taylor-Aligned)

## Core Philosophy: State Is Sovereign
The system is not a set of apps or dashboards. The system is the state. Agents mutate state; the chat interface is a notification and command stream for those mutations.

## 1. No-UI Back Office (Kill the Dashboard)
- The interface is the Manager agent, not a React dashboard.
- You query state conversationally: "Status of Fourth Plain?"
- The Manager reads state and returns the next action and blockers.
- The system avoids static dashboards in favor of live, context-aware queries.

## 2. Active State Over Passive Files
- The Shared Deal State evolves into a live, structured datastore.
- Agents do not talk to each other; they talk to the state.
- Research writes structured fields; analysis reads and updates; Manager reports.
- The Librarian converts unstructured sources into structured records.

## 3. Vibe Coding vs Mission-Critical Logic
- Vibe coding is allowed for qualitative work (profiling, summaries).
- Mission-critical calculations must be deterministic.
- The Underwriter is a runtime executive: it triggers scripts and writes results.
- LLMs manage I/O; hard-coded logic computes math.

## 4. Maintenance Layer Is Critical
- The Janitor/Coordinator is a state garbage collector.
- Dead deals are archived; sensitive data is scrubbed; lessons are logged.
- This prevents stale context from contaminating active work.

## 5. Refined Agent Swarm (Database Operators)

### Interface Layer
- Manager is the query router.
- Telegram (or similar) is the command surface.
- Responses are state snapshots, not narratives.

### Deterministic Core
- Underwriter does not compute math directly.
- It calls local scripts (e.g., `calc_strike_price.py`) and commits results.

### Research Layer (Sensors)
- City Planner fills zoning and constraints.
- Transcription Doctor extracts negotiation leverage and motivation.
- Librarian converts docs into structured records.

### Maintenance Layer
- Coordinator prunes dead or stalled deals.
- Archives and redacts sensitive material when required.

## 6. Event-Driven Workflow
1. Ingestion: Manager creates a new state record from a link or voice note.
2. Swarm activation: Research agents populate missing fields.
3. Analysis: Underwriter runs deterministic scripts and writes outputs.
4. Notification: Manager reports deltas and asks for next action.
5. Command: Principals issue next instruction; state updates.

## 7. Implementation Pivot
- Stop writing prompts; write schemas.
- Schema is the contract; agents are the executors.
- State integrity and validation are the primary product.
