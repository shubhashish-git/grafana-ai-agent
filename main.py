import sys
from rich.console import Console

console = Console()


def print_usage():
    console.print("""
[bold cyan]Grafana AI Agent[/bold cyan]

Usage:
  python main.py webhook    -> Start webhook receiver on port 5001
  python main.py poll       -> Start proactive poller (scheduled)
  python main.py test       -> Smoke test LLM + notifier (no Grafana needed)
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "webhook":
        from agent.webhook_server import start_server
        start_server()

    elif mode == "poll":
        from agent.poller import start_poller
        start_poller()

    elif mode == "test":
        from agent.llm_agent import analyze_alert
        from agent.notifier import notify_alert
        console.print("[bold yellow]🧪 Running smoke test...[/bold yellow]")
        result = analyze_alert(
            "SmokeTest_HighMemory",
            {"instance": "localhost", "severity": "critical"},
            "Memory Usage: min=88.00, max=96.50, avg=92.10, last=96.50 (30 datapoints)"
        )
        notify_alert("SmokeTest_HighMemory", result)
        console.print("[bold green]✅ Done. Check logs/alerts.log[/bold green]")

    else:
        print_usage()