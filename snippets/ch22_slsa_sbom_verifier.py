#!/usr/bin/env python3
"""Ch 22: SLSA Provenance & CycloneDX SBOM Verifier."""
import json
from dataclasses import dataclass
from typing import List


@dataclass
class ArtifactAttestationBundle:
    image_digest: str
    builder_id: str
    source_repo: str
    workflow_ref: str
    sbom_components: int
    unmitigated_critical_cves: List[str]


TRUSTED_BUILDER_PREFIX = (
    "https://github.com/actions/runner"
)
TRUSTED_REPO_PREFIX = "https://github.com/acme/"


def verify_supply_chain_bundle(
    bundle: ArtifactAttestationBundle,
) -> dict:
    violations = []
    if not bundle.image_digest.startswith("sha256:"):
        violations.append(
            "Artifact must be pinned by sha256 digest"
        )
    if not bundle.builder_id.startswith(
        TRUSTED_BUILDER_PREFIX
    ):
        violations.append(
            f"Untrusted SLSA builder: {bundle.builder_id}"
        )
    if not bundle.source_repo.startswith(
        TRUSTED_REPO_PREFIX
    ):
        violations.append(
            f"Untrusted source repo: {bundle.source_repo}"
        )
    if bundle.sbom_components <= 0:
        violations.append(
            "Missing or empty CycloneDX SBOM inventory"
        )
    if bundle.unmitigated_critical_cves:
        cves = ", ".join(
            bundle.unmitigated_critical_cves
        )
        violations.append(
            f"Unmitigated critical CVEs: {cves}"
        )
    return {
        "image_digest": bundle.image_digest,
        "verified": len(violations) == 0,
        "slsa_level_compliant": len(violations) == 0,
        "violations": violations,
    }


if __name__ == "__main__":
    sample = ArtifactAttestationBundle(
        image_digest="sha256:8f4e2b9a1c3d...",
        builder_id=(
            "https://github.com/actions/runner/v2"
        ),
        source_repo=(
            "https://github.com/acme/checkout-service"
        ),
        workflow_ref="refs/tags/v2.4.0",
        sbom_components=64,
        unmitigated_critical_cves=[],
    )
    print(
        json.dumps(
            verify_supply_chain_bundle(sample),
            indent=2,
        )
    )
