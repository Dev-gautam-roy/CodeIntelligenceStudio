import math
import re
from typing import List, Dict, Any, Tuple
from app.schemas.analysis import SecurityFinding

SECRET_PATTERNS = [
    ("AWS_ACCESS_KEY", re.compile(r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}")),
    ("GITHUB_PAT", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,255}")),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA|DSA|EC|OPENSSH|PRIVATE) KEY-----")),
    ("SLACK_TOKEN", re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}")),
    ("OPENAI_KEY", re.compile(r"sk-[a-zA-Z0-9]{48}")),
    ("GENERIC_SECRET", re.compile(r'(?i)(?:api_key|apikey|secret|password|passwd|auth_token)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{16,})["\']')),
]

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions"),
    re.compile(r"(?i)system:\s*you\s+are\s+now"),
    re.compile(r"(?i)bypass\s+(?:security|approval|gate)"),
    re.compile(r"(?i)execute\s+(?:arbitrary|root|host)\s+command"),
    re.compile(r"(?i)upload\s+(?:environment|env|secret|credentials)"),
    re.compile(r"(?i)send\s+(?:keys?|tokens?)\s+to\s+https?://"),
]


def shannon_entropy(data: str) -> float:
    """Calculates Shannon entropy to detect high-randomness cryptographic secrets."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy += - p_x * math.log2(p_x)
    return entropy


class SecurityService:
    @classmethod
    def scan_content_for_secrets(cls, file_path: str, content: str) -> List[SecurityFinding]:
        """Scans code content for leaked credentials, private keys, and high-entropy secrets."""
        findings: List[SecurityFinding] = []
        lines = content.splitlines()

        for idx, line in enumerate(lines, start=1):
            for sec_type, pattern in SECRET_PATTERNS:
                match = pattern.search(line)
                if match:
                    findings.append(
                        SecurityFinding(
                            severity="CRITICAL",
                            type="SECRET_LEAK",
                            file_path=file_path,
                            line_number=idx,
                            description=f"Potential {sec_type} detected.",
                            snippet=line[:80].strip(),
                            recommendation="Remove the secret immediately, revoke the credential, and add to .gitignore.",
                        )
                    )

            # Shannon entropy check on long tokens
            words = re.findall(r"[a-zA-Z0-9+/=_\-]{24,}", line)
            for w in words:
                if shannon_entropy(w) > 4.5:
                    findings.append(
                        SecurityFinding(
                            severity="HIGH",
                            type="HIGH_ENTROPY_SECRET",
                            file_path=file_path,
                            line_number=idx,
                            description="High Shannon-entropy string detected (possible credential/hash).",
                            snippet=f"{w[:6]}...{w[-4:]}",
                            recommendation="Ensure this value is not an active secret or encrypt it at rest.",
                        )
                    )
        return findings

    @classmethod
    def scan_for_prompt_injection(cls, text: str) -> Tuple[bool, str, List[str], str]:
        """Scans untrusted repository text (e.g. README, issue bodies) for prompt injection directives."""
        detected = []
        sanitized = text

        for pattern in INJECTION_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                detected.extend(matches)
                sanitized = pattern.sub("[REDACTED_INJECTION_DIRECTIVE]", sanitized)

        if not detected:
            return True, "LOW", [], text

        risk_level = "CRITICAL" if len(detected) >= 2 else "HIGH"
        return False, risk_level, detected, sanitized

    @classmethod
    def verify_prompt(cls, prompt_text: str, token_budget: int = 4000) -> Dict[str, Any]:
        """Audits an engineering prompt for structure, missing bounds, contradictions, and budget."""
        missing = []
        contradictions = []
        security_concerns = []

        # Token estimation (~4 chars per token)
        est_tokens = len(prompt_text) // 4
        if est_tokens > token_budget:
            contradictions.append(f"Prompt length ({est_tokens} tokens) exceeds allocated budget ({token_budget} tokens).")

        # Check required architectural sections
        lower = prompt_text.lower()
        if "role" not in lower and "you are" not in lower:
            missing.append("Missing explicit Role definition.")
        if "input" not in lower and "schema" not in lower:
            missing.append("Missing explicit Input Schema specification.")
        if "output" not in lower and "format" not in lower:
            missing.append("Missing explicit Output Format or Completion Criteria.")

        # Check safety directives
        if "approval" not in lower and ("write" in lower or "push" in lower or "deploy" in lower):
            security_concerns.append("Modifying actions detected without mandatory human approval gate directive.")

        score = max(0.0, 10.0 - (len(missing) * 2.0 + len(contradictions) * 3.0 + len(security_concerns) * 2.5))
        valid = len(contradictions) == 0 and len(security_concerns) == 0 and score >= 6.0

        report = (
            f"Prompt Verification Audit (Score: {score:.1f}/10.0)\n"
            f"Estimated Tokens: {est_tokens} / {token_budget}\n"
            f"Status: {'VALID' if valid else 'REVISION REQUIRED'}\n"
        )
        if missing:
            report += f"Missing elements: {', '.join(missing)}\n"
        if contradictions:
            report += f"Contradictions: {', '.join(contradictions)}\n"
        if security_concerns:
            report += f"Security concerns: {', '.join(security_concerns)}\n"

        return {
            "valid": valid,
            "score": score,
            "token_count": est_tokens,
            "missing_elements": missing,
            "contradictions": contradictions,
            "security_concerns": security_concerns,
            "report": report,
        }
