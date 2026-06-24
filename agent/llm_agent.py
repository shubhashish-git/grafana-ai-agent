from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from config.settings import OPENROUTER_API_KEY, OPENROUTER_MODEL

SYSTEM_PROMPT = """You are an expert SRE assistant monitoring Grafana dashboards.
Given alert data or metric summaries, always respond with:

1. Root Cause Hypothesis — 1-2 sentences
2. Severity — P1 (critical) / P2 (high) / P3 (medium) / P4 (low) with reason
3. Recommended Action — specific and actionable, 1-2 sentences
4. Watch For — correlated metrics or cascading issues to monitor

Be concise, technical, and direct."""


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "Grafana AI Agent",
        },
        temperature=0.2,
        max_tokens=512,
    )


def analyze_alert(alert_name: str, labels: dict, metric_summary: str) -> str:
    llm = get_llm()
    user_msg = f"""Alert Name: {alert_name}
Labels: {labels}
Metric Data (last 30 min):
{metric_summary}

Provide your SRE assessment."""
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ])
    return response.content


def analyze_proactive(dashboard_name: str, metric_summary: str):
    """Returns analysis string if anomaly found, None if healthy."""
    llm = get_llm()
    user_msg = f"""Dashboard: {dashboard_name}
Metric Data (last 30 min):
{metric_summary}

Scan for anomalies or values approaching dangerous thresholds.
If everything looks HEALTHY, respond with exactly one word: HEALTHY
Otherwise provide your full SRE assessment."""
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ])
    content = response.content.strip()
    return None if content.upper() == "HEALTHY" else content