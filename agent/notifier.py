import httpx
from datetime import datetime
from pathlib import Path
from rich.console import Console
from config.settings import SLACK_WEBHOOK_URL

console = Console()
LOG_FILE = Path(__file__).parent.parent / "logs" / "alerts.log"
LOG_FILE.parent.mkdir(exist_ok=True)


def _log_to_file(level: str, title: str, body: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {title}\n{body}\n{'─' * 60}\n"
    with LOG_FILE.open("a") as f:
        f.write(line)


def _print_console(level: str, title: str, body: str):
    icons  = {"ALERT": "🔴", "PROACTIVE": "⚠️ ", "HEALTHY": "✅"}
    colors = {"ALERT": "bold red", "PROACTIVE": "bold yellow", "HEALTHY": "bold green"}
    icon  = icons.get(level, "ℹ️")
    color = colors.get(level, "white")
    console.print(f"\n[{color}]{icon}  [{level}] {title}[/{color}]")
    console.print(f"{body}\n")


def _send_slack(title: str, body: str, color: str = "#FF4444"):
    if not SLACK_WEBHOOK_URL:
        return
    try:
        httpx.post(SLACK_WEBHOOK_URL, json={
            "attachments": [{
                "color": color,
                "title": f"🤖 Grafana AI Agent — {title}",
                "text": body,
                "footer": "grafana-ai-agent | localhost",
                "ts": int(datetime.now().timestamp()),
            }]
        }, timeout=5)
    except Exception as e:
        console.print(f"[red]Slack failed: {e}[/red]")


def notify_alert(alert_name: str, analysis: str):
    _print_console("ALERT", alert_name, analysis)
    _log_to_file("ALERT", alert_name, analysis)
    _send_slack(alert_name, analysis, "#FF4444")


def notify_proactive(dashboard: str, analysis: str):
    _print_console("PROACTIVE", f"Proactive — {dashboard}", analysis)
    _log_to_file("PROACTIVE", f"Proactive — {dashboard}", analysis)
    _send_slack(f"Proactive: {dashboard}", analysis, "#FFA500")


def notify_healthy(dashboard: str):
    _print_console("HEALTHY", dashboard, "All metrics within normal range.")
    _log_to_file("HEALTHY", dashboard, "All metrics within normal range.")