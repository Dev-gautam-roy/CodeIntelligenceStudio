---
name: deployment
description: Audits deployment configurations, verifies Docker/K8s manifests, checks environment variables, and executes approved releases.
when_to_use: Use when validating container configurations, performing pre-flight deployment audits, or rolling out approved builds.
user-invocable: true
effort: high
allowed-tools:
  - run_command
  - read_file
---

# Deployment Skill

## Purpose
Inspect and validate deployment configurations, Dockerfiles, Kubernetes manifests, and environment variables, ensuring zero secrets are exposed and health checks are configured.

## Execution Procedure
1. Parse and validate deployment manifests (`Dockerfile`, `docker-compose.yml`, Helm/K8s manifests).
2. Verify readiness and liveness probe configurations.
3. Audit required runtime environment variables and secret injection paths.
4. Halt and request human approval prior to initiating production deployment.
5. Probe live health endpoints and report rollout status.
