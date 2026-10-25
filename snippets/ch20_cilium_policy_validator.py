#!/usr/bin/env python3
"""Ch 20: Cilium L7 & Ambient Service Mesh Auditor."""
import json
from dataclasses import dataclass
from typing import List


@dataclass
class NamespaceMeshAudit:
    namespace: str
    ambient_enabled: bool
    has_l7_cilium_policy: bool
    allows_wildcard_egress: bool
    tetragon_enforced: bool


def audit_zero_trust_posture(
    namespaces: List[NamespaceMeshAudit],
) -> dict:
    findings = []
    passed = 0
    for ns in namespaces:
        issues = []
        if not ns.ambient_enabled:
            issues.append(
                "Missing istio.io/dataplane-mode=ambient"
            )
        if not ns.has_l7_cilium_policy:
            issues.append(
                "Missing L7 CiliumNetworkPolicy"
            )
        if ns.allows_wildcard_egress:
            issues.append(
                "Unrestricted 0.0.0.0/0 egress allowed"
            )
        if not ns.tetragon_enforced:
            issues.append(
                "Missing Tetragon TracingPolicy"
            )
        if issues:
            findings.append(
                {
                    "namespace": ns.namespace,
                    "violations": issues,
                }
            )
        else:
            passed += 1
    return {
        "audited_namespaces": len(namespaces),
        "compliant_namespaces": passed,
        "non_compliant_findings": findings,
    }


if __name__ == "__main__":
    sample = [
        NamespaceMeshAudit(
            "team-payments", True, True, False, True
        ),
        NamespaceMeshAudit(
            "legacy-reporting",
            False,
            False,
            True,
            False,
        ),
    ]
    print(
        json.dumps(
            audit_zero_trust_posture(sample), indent=2
        )
    )
