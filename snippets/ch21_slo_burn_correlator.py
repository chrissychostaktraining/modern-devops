#!/usr/bin/env python3
"""Ch 21: AI-SRE Multi-Window SLO Burn Correlator."""
import json
from dataclasses import dataclass
from typing import List


@dataclass
class SpanWindowTelemetry:
    service: str
    version: str
    total_requests: int
    error_requests: int
    p99_ms: float
    deployed_minutes_ago: int


def analyze_slo_burn(
    windows: List[SpanWindowTelemetry],
    slo_target: float = 0.999,
) -> dict:
    error_budget = 1.0 - slo_target
    suspects = []
    for w in windows:
        err_rate = w.error_requests / max(
            w.total_requests, 1
        )
        burn_rate = round(err_rate / error_budget, 2)
        if burn_rate >= 14.4:
            score = burn_rate * (
                2.0
                if w.deployed_minutes_ago <= 30
                else 1.0
            )
            suspects.append(
                {
                    "service": w.service,
                    "version": w.version,
                    "burn_rate": burn_rate,
                    "p99_ms": w.p99_ms,
                    "recent_deploy": (
                        w.deployed_minutes_ago <= 30
                    ),
                    "rca_priority_score": round(
                        score, 2
                    ),
                }
            )
    suspects.sort(
        key=lambda x: x["rca_priority_score"],
        reverse=True,
    )
    return {
        "slo_target": slo_target,
        "page_oncall": len(suspects) > 0,
        "ranked_root_cause_candidates": suspects,
    }


if __name__ == "__main__":
    telemetry = [
        SpanWindowTelemetry(
            "api-gateway",
            "v1.4.0",
            10000,
            180,
            920.0,
            420,
        ),
        SpanWindowTelemetry(
            "payment-authorizer",
            "v2.8.1-rc3",
            2500,
            175,
            890.0,
            12,
        ),
    ]
    print(json.dumps(analyze_slo_burn(telemetry), indent=2))
