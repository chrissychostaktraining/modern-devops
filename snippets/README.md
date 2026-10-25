# Companion Code & Snippets Guide — *Mastering Modern DevOps (Second Edition)*

This directory contains self-contained, print-safe (`<= 55` columns per line) companion code examples and verification scripts for **Mastering Modern DevOps: A Comprehensive Guide to Infrastructure, Automation, and Cloud-Native Technologies (Second Edition)** by **Christian Chostak**, alongside the topic-specific project directories (`01-cdk` through `12-serverless`) at the root of the repository.

## Summary of Companion Snippets

- **`ch01_cdk_multi_stack_app.py`**: Chapter 1 — AWS CDK v2 multi-stack KMS key rotation and encrypted SQS queue synthesizer.
- **`ch02_boto3_resilient_sqs_worker.py`**: Chapter 2 — AWS SDK for Python (`boto3`) resilient SQS batch processor with partial batch failure reporting and AWS X-Ray trace attribution.
- **`ch03_ansible_hardened_web_role.yaml`**: Chapter 3 — Idempotent Ansible playbook for provisioning and reloading a hardened NGINX web fleet.
- **`ch04_github_actions_ci_matrix.yaml`**: Chapter 4 — GitHub Actions CI workflow with matrix Python testing, dependency caching, and a blocking Trivy vulnerability gate.
- **`ch06_multistage_nonroot.dockerfile`**: Chapter 6 — Multi-stage production Dockerfile with non-root user execution (`10001:10001`) and built-in healthcheck.
- **`ch07_kubernetes_blue_green_rollout.yaml`**: Chapter 7 — Hardened Kubernetes `Deployment` and `Service` manifests for zero-downtime blue/green traffic switching.
- **`ch08_prometheus_alert_rules.yaml`**: Chapter 8 — Prometheus scrape configuration and golden-signal 5xx error-rate alerting rule.
- **`ch14_argocd_gitops_application.yaml`**: Chapter 14 — Declarative Argo CD `Application` manifest with automated pruning and continuous drift self-healing.
- **`ch19_crossplane_postgresql_xrd.yaml`**: Chapter 19 — Crossplane `CompositeResourceDefinition` (`XRD`) exposing a self-service `PostgreSQLInstance` claim API for Internal Developer Platforms.
- **`ch19_idp_claim_auditor.py`**: Chapter 19 — Python verification tool auditing IDP Crossplane claim readiness and Golden Path template version compliance.
- **`ch20_cilium_l7_zero_trust_policy.yaml`**: Chapter 20 — Cilium eBPF Layer-7 `CiliumNetworkPolicy` enforcing HTTP method/path rules and DNS-aware (`toFQDNs`) egress filtering.
- **`ch20_cilium_policy_validator.py`**: Chapter 20 — Python zero-trust audit script verifying Istio Ambient Mode enrollment, Cilium L7 policies, and Tetragon runtime enforcement across Kubernetes namespaces.
- **`ch21_otel_collector_tail_sampling.yaml`**: Chapter 21 — Production OpenTelemetry Collector Gateway configuration with memory protection, Kubernetes metadata enrichment, PII redaction, and tail-based sampling.
- **`ch21_slo_burn_correlator.py`**: Chapter 21 — AI-Augmented SRE Python engine calculating multi-window SLO error-budget burn rates (`14.4x` threshold) and ranking root-cause candidates by deployment recency.
- **`ch22_kyverno_slsa_cosign_policy.yaml`**: Chapter 22 — Kyverno `ClusterPolicy` enforcing keyless Sigstore Cosign OIDC image signatures, tag-to-digest mutation, and SLSA v1.0 provenance attestations in Kubernetes.
- **`ch22_slsa_sbom_verifier.py`**: Chapter 22 — Python verification gate validating SLSA build provenance, trusted OIDC builder identity, and CycloneDX SBOM vulnerability status.

## Running the Verification Scripts

All Python verification scripts run on standard Python 3.11+ with zero external paid API dependencies:

```bash
python3 snippets/ch01_cdk_multi_stack_app.py
python3 snippets/ch02_boto3_resilient_sqs_worker.py
python3 snippets/ch19_idp_claim_auditor.py
python3 snippets/ch20_cilium_policy_validator.py
python3 snippets/ch21_slo_burn_correlator.py
python3 snippets/ch22_slsa_sbom_verifier.py
```
