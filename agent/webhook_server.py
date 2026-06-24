import uvicorn
from fastapi import FastAPI, Request
from rich.console import Console
from agent.llm_agent import analyze_alert
from agent.notifier import notify_alert

console = Console()
app = FastAPI(title="Grafana AI Agent")


@app.get("/health")
def health():
    return {"status": "ok", "service": "grafana-ai-agent"}


@app.post("/alert")
async def receive_alert(request: Request):
    payload = await request.json()
    alerts  = payload.get("alerts", [])
    if not alerts:
        return {"status": "ignored", "reason": "empty alerts array"}

    console.print(f"\n[bold red]🔔 Webhook received — {len(alerts)} alert(s)[/bold red]")
    processed = 0
    for alert in alerts:
        name        = alert.get("labels", {}).get("alertname", "UnknownAlert")
        status      = alert.get("status", "unknown")
        labels      = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        values      = alert.get("values", {})

        console.print(f"  → {name} | status={status}")

        if status == "resolved":
            console.print("  [green]✅ Resolved — skipping LLM call[/green]")
            continue

        parts = []
        if values:
            parts.append(f"Current metric values: {values}")
        if annotations.get("summary"):
            parts.append(f"Summary: {annotations['summary']}")
        if annotations.get("description"):
            parts.append(f"Description: {annotations['description']}")
        metric_summary = "\n".join(parts) or "No numeric data in payload."

        console.print("  🤖 Analyzing...")
        analysis = analyze_alert(name, labels, metric_summary)
        notify_alert(name, analysis)
        processed += 1

    return {"status": "processed", "analyzed": processed, "total": len(alerts)}


@app.post("/test")
async def test_pipeline():
    """Test the full pipeline without needing a real Grafana alert.
    Run: curl -X POST http://localhost:5001/test
    """
    console.print("\n[bold yellow]🧪 Test alert triggered[/bold yellow]")
    name    = "HighCPUUsage_TEST"
    labels  = {"instance": "localhost:9090", "job": "node_exporter", "severity": "critical"}
    summary = (
        "Current metric values: {'cpu_usage_pct': 94.2}\n"
        "Summary: CPU usage above 90% threshold for 10 minutes\n"
        "Description: avg=91.8%, max=94.2% over last 30 min on localhost."
    )
    analysis = analyze_alert(name, labels, summary)
    notify_alert(name, analysis)
    return {"status": "ok", "alert": name, "analysis": analysis}


def start_server():
    console.print("[bold green]🚀 Webhook server on http://localhost:5001[/bold green]")
    console.print("  Grafana Contact Point → http://localhost:5001/alert")
    console.print("  Test: curl -X POST http://localhost:5001/test\n")
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="warning")


if __name__ == "__main__":
    start_server()