import os
from dotenv import load_dotenv

load_dotenv()

GRAFANA_URL        = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_TOKEN      = os.getenv("GRAFANA_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL   = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
SLACK_WEBHOOK_URL  = os.getenv("SLACK_WEBHOOK_URL", "")
POLL_INTERVAL      = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))

GRAFANA_HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
}