---
name: security-audit
description: Secret scanning, prompt injection defense analysis, and vulnerable dependency detection.
when_to_use: Use before committing code, prior to running untrusted workflows, or during scheduled security reviews.
user-invocable: true
effort: high
allowed-tools:
  - run_command
  - read_file
---

# Security Audit Skill

## Purpose
Scan code, documentation, and repository metadata for exposed API tokens, private keys, Shannon-entropy credentials, and indirect prompt injection attempts.

## Execution Procedure
1. Execute regex and entropy scanners across workspace source files.
2. Scan `README.md`, issues, and documentation files for prompt hijacking directives.
3. Check dependency manifests for known CVEs or vulnerable packages.
4. Verify that no private keys or tokens reside in git history or unignored files.
5. Produce a categorized security report with remediation advice.
