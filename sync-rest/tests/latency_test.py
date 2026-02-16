import os
import statistics
import time
from dataclasses import dataclass
from typing import Dict, List

import requests

ORDER_URL = os.getenv("ORDER_URL", "http://localhost:5003/order")


@dataclass
class LatencySummary:
    name: str
    count: int
    min_ms: float
    max_ms: float
    avg_ms: float
    p95_ms: float


def _run_once(payload: Dict[str, str]) -> float:
    start = time.perf_counter()
    response = requests.post(ORDER_URL, json=payload, timeout=5)
    response.raise_for_status()
    return time.perf_counter() - start


def run_latency_test(iterations: int, name: str) -> LatencySummary:
    durations: List[float] = []
    for i in range(iterations):
        payload = {
            "order_id": f"o-{name}-{i}",
            "item_id": "coffee",
            "quantity": 1,
            "user_email": "student@sjsu.edu",
        }
        durations.append(_run_once(payload))

    return LatencySummary(
        name=name,
        count=iterations,
        min_ms=min(durations) * 1000,
        max_ms=max(durations) * 1000,
        avg_ms=statistics.mean(durations) * 1000,
        p95_ms=statistics.quantiles(durations, n=20)[-1] * 1000,
    )


def render_markdown_table(summaries: List[LatencySummary]) -> str:
    lines = [
        "| scenario | count | min (ms) | max (ms) | avg (ms) | p95 (ms) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for summary in summaries:
        lines.append(
            "| {name} | {count} | {min:.2f} | {max:.2f} | {avg:.2f} | {p95:.2f} |".format(
                name=summary.name,
                count=summary.count,
                min=summary.min_ms,
                max=summary.max_ms,
                avg=summary.avg_ms,
                p95=summary.p95_ms,
            )
        )
    return "\n".join(lines)


if __name__ == "__main__":
    iterations = int(os.getenv("ITERATIONS", "10"))
    scenario = os.getenv("LATENCY_SCENARIO", "baseline")
    summary = run_latency_test(iterations=iterations, name=scenario)
    print(render_markdown_table([summary]))
