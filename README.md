# grafana-ai-agent

An AI-powered agent that integrates with local Grafana dashboards for:
- **Reactive monitoring** — analyzes alerts via webhook as they fire
- **Proactive monitoring** — polls Prometheus metrics on a schedule and detects anomalies before alerts trigger

Powered by [OpenRouter](https://openrouter.ai) (Claude, GPT-4o, Mistral, etc.)

## Architecture
Grafana (localhost:3000)
├── Alert fires → Webhook → FastAPI Agent (port 5001) → LLM → Slack/Log
└── Schedule → Poller → Grafana API → LLM → Slack/Log


## Quick Start

\```bash
git clone https://github.com/YOUR_USERNAME/grafana-ai-agent
cd grafana-ai-agent
pip install -r requirements.txt
cp .env.example .env   # fill in your tokens
python main.py test    # smoke test (no Grafana needed)
\```

## Modes

| Command | What it does |
|---|---|
| `python main.py test` | Smoke test — LLM + notifier only |
| `python main.py webhook` | Start webhook server on port 5001 |
| `python main.py poll` | Start proactive poller (every 5 min) |

## Configuration

Edit `.env`:
- `GRAFANA_TOKEN` — Grafana service account token
- `OPENROUTER_API_KEY` — from [openrouter.ai/keys](https://openrouter.ai/keys)
- `OPENROUTER_MODEL` — e.g. `anthropic/claude-3.5-haiku`
- `SLACK_WEBHOOK_URL` — optional, leave blank to only log locally

For proactive polling, edit `agent/poller.py` → `WATCH_QUERIES` with your datasource UIDs.

## Get Grafana Service Token
\```bash
curl http://admin:admin@localhost:3000/api/datasources  # find datasource UIDs
\```
In Grafana UI: Administration → Service Accounts → Add token

## Stack
- FastAPI + Uvicorn (webhook server)
- APScheduler (polling)
- LangChain + OpenRouter (LLM)
- Rich (console output)