#!/usr/bin/env python3
"""Ch 19: IDP Golden Path & Crossplane Claim Auditor."""
import json
from dataclasses import dataclass
from typing import List


@dataclass
class PlatformClaimStatus:
    name: str
    namespace: str
    kind: str
    synced: bool
    ready: bool
    golden_path_version: str


def evaluate_idp_fleet(
    claims: List[PlatformClaimStatus],
    min_version: str = "v2.1",
) -> dict:
    total = len(claims)
    healthy = sum(
        1 for c in claims if c.synced and c.ready
    )
    compliant = sum(
        1
        for c in claims
        if c.golden_path_version >= min_version
    )
    drift_alerts = [
        f"{c.namespace}/{c.name}"
        for c in claims
        if not (c.synced and c.ready)
    ]
    return {
        "total_claims": total,
        "ready_ratio": round(
            healthy / max(total, 1), 3
        ),
        "golden_path_compliance": round(
            compliant / max(total, 1), 3
        ),
        "degraded_claims": drift_alerts,
    }


if __name__ == "__main__":
    sample = [
        PlatformClaimStatus(
            "checkout-db",
            "team-payments",
            "PostgreSQLInstance",
            True,
            True,
            "v2.2",
        ),
        PlatformClaimStatus(
            "legacy-cache",
            "team-catalog",
            "RedisCluster",
            True,
            False,
            "v1.9",
        ),
    ]
    print(json.dumps(evaluate_idp_fleet(sample), indent=2))
