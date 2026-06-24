from apscheduler.schedulers.blocking import BlockingScheduler
from rich.console import Console
from agent.grafana_client import get_all_dashboards, query_prometheus, summarize_query_result
from agent.llm_agent import analyze_proactive
from agent.notifier import notify_proactive, notify_healthy
from config.settings import POLL_INTERVAL

console = Console()

# ── EDIT THIS: replace datasource UIDs and PromQL to match your setup ──────
# To find your datasource UID, run:
#   curl http://admin:admin@localhost:3000/api/datasources
# Look for the "uid" field in the response.
WATCH_QUERIES = [
    {
        "label": "CPU Usage %",
        "datasource_uid": "REPLACE_WITH_YOUR_DS_UID",
        "promql": '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
    },
    {
        "label": "Memory Usage %",
        "datasource_uid": "REPLACE_WITH_YOUR_DS_UID",
        "promql": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
    },
    {
        "label": "HTTP 5xx Error Rate",
        "datasource_uid": "REPLACE_WITH_YOUR_DS_UID",
        "promql": 'sum(rate(http_requests_total{status=~"5.."}[5m]))',
    },
]


def run_poll():
    console.print("\n[cyan]🔄 Running proactive poll...[/cyan]")

    try:
        dashboards    = get_all_dashboards()
        board_context = ", ".join(d.get("title", "?") for d in dashboards[:5])
        console.print(f"  Dashboards found: {board_context}")
    except Exception as e:
        console.print(f"[red]  Cannot reach Grafana: {e}[/red]")
        return

    metric_lines = []
    for wq in WATCH_QUERIES:
        try:
            result  = query_prometheus(wq["datasource_uid"], wq["promql"])
            summary = summarize_query_result(result)
            metric_lines.append(f"[{wq['label']}]\n{summary}")
            console.print(f"  ✓ {wq['label']}: {summary.split(chr(10))[0]}")
        except Exception as e:
            metric_lines.append(f"[{wq['label']}] ERROR: {e}")
            console.print(f"  [yellow]✗ {wq['label']}: {e}[/yellow]")

    if not metric_lines:
        console.print("[yellow]  No metrics collected. Check datasource UIDs in WATCH_QUERIES.[/yellow]")
        return

    full_summary = "\n\n".join(metric_lines)
    console.print("  🤖 Sending to LLM...")
    analysis = analyze_proactive(board_context, full_summary)

    if analysis:
        console.print("  [bold yellow]⚠ Anomaly detected[/bold yellow]")
        notify_proactive(board_context, analysis)
    else:
        notify_healthy(board_context)


def start_poller():
    console.print(f"[bold green]🚀 Proactive poller started — every {POLL_INTERVAL}s[/bold green]")
    run_poll()  # run immediately on start
    scheduler = BlockingScheduler()
    scheduler.add_job(run_poll, "interval", seconds=POLL_INTERVAL)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        console.print("[yellow]\nPoller stopped.[/yellow]")


if __name__ == "__main__":
    start_poller()