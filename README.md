# Email Triage Agent — CrewAI

Part 1/3 of a small CrewAI portfolio series, each one adding more of the
framework's core concepts on top of the same email-assistant idea.

| # | Repo | What it adds |
|---|------|--------------|
| 1 | **crewai-portfolio-01-email-triage-agent** (this repo) | Single Agent, MCP tool calling, structured output |
| 2 | [crewai-portfolio-02-email-rag-crew](https://github.com/YanivBohbot/crewai-portfolio-02-email-rag-crew) | Crew, Knowledge (RAG), Memory, Guardrails |
| 3 | [crewai-portfolio-03-email-production-flow](https://github.com/YanivBohbot/crewai-portfolio-03-email-production-flow) | Full Flow, multi-MCP, human-in-the-loop, persistence |

## What this does

A single CrewAI `Agent`, wrapped in a minimal `Flow`, connects to a **mock
Gmail MCP server** over stdio, lists the inbox, reads each message, and
classifies them by priority (`urgent` / `normal` / `spam`) with a structured
output. Read-only: no tool exists to send or delete anything.

Deliberately kept to a single agent — the point of this first repo is to show
MCP wiring and tool calling cleanly, before adding a Crew, Knowledge or Memory
in the next two repos.

## CrewAI concepts used

- **Agent** — role/goal/backstory, no Crew needed (`Agent.kickoff()`)
- **Flow** — `@start()` step, Pydantic-typed state
- **MCP** — `MCPServerStdio` connecting to a local mock server
- **Structured output** — `response_format=TriageReport` (Pydantic)
- **Tool calling** — the agent decides when to call `list_recent_emails` /
  `get_email`, discovered dynamically from the MCP server

## Tech stack

- [crewai](https://docs.crewai.com) 1.15.x
- Python 3.10–3.13, [uv](https://docs.astral.sh/uv/) for dependency management
- [mcp](https://modelcontextprotocol.io) (`FastMCP`) for the mock Gmail server
- OpenAI (`openai/gpt-4.1-mini` by default — any provider string `LLM` accepts works)

## Project structure

```
src/email_triage/
├── main.py                        # Flow: @start() triage_inbox
└── mcp_servers/
    └── gmail_mock_server.py       # Mock MCP server: list_recent_emails, get_email
```

`gmail_mock_server.py` simulates a Gmail inbox (6 fake emails) behind the same
two read-only tools a real Gmail MCP server would expose. Swap this one file
for an OAuth-backed server later — nothing in `main.py` needs to change.

## Setup & run

```bash
crewai install            # or: uv sync
```

Add your key to `.env`:

```
OPENAI_API_KEY=sk-...
MODEL=openai/gpt-4.1-mini
```

Run:

```bash
uv run kickoff
# or
crewai run
```

Expected output: a triage report for the 6 mock emails, printed to the
terminal, classified by priority with a one-line summary each.

## Notes

- No real email account is touched — the MCP server is 100% local mock data.
- Debug with `crewai traces enable` before adding `print()` statements if the
  agent's tool calls look wrong.
