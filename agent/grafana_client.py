import httpx
from config.settings import GRAFANA_URL, GRAFANA_HEADERS


def get_all_dashboards() -> list:
    with httpx.Client(timeout=10) as c:
        r = c.get(f"{GRAFANA_URL}/api/search?type=dash-db", headers=GRAFANA_HEADERS)
        r.raise_for_status()
        return r.json()


def get_datasources() -> list:
    """Use this to find your datasource UIDs for poller.py"""
    with httpx.Client(timeout=10) as c:
        r = c.get(f"{GRAFANA_URL}/api/datasources", headers=GRAFANA_HEADERS)
        r.raise_for_status()
        return r.json()


def query_prometheus(datasource_uid: str, promql: str, time_range: str = "now-30m") -> dict:
    payload = {
        "queries": [{
            "refId": "A",
            "datasource": {"uid": datasource_uid, "type": "prometheus"},
            "expr": promql,
            "instant": False,
            "range": True,
            "intervalMs": 60000,
            "maxDataPoints": 30,
        }],
        "from": time_range,
        "to": "now",
    }
    with httpx.Client(timeout=15) as c:
        r = c.post(f"{GRAFANA_URL}/api/ds/query", headers=GRAFANA_HEADERS, json=payload)
        r.raise_for_status()
        return r.json()


def summarize_query_result(result: dict) -> str:
    lines = []
    for frame_data in result.get("results", {}).values():
        for series in frame_data.get("frames", []):
            name   = series.get("schema", {}).get("name", "metric")
            fields = series.get("data", {}).get("values", [])
            if len(fields) >= 2:
                values = [v for v in fields[1] if v is not None]
                if values:
                    lines.append(
                        f"{name}: min={min(values):.2f}, max={max(values):.2f}, "
                        f"avg={sum(values)/len(values):.2f}, last={values[-1]:.2f} "
                        f"({len(values)} datapoints)"
                    )
    return "\n".join(lines) if lines else "No metric data returned."