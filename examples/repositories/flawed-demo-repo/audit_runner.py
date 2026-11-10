import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, r"C:\Users\devga\OneDrive\Desktop\CodeIntelligenceStudio\backend")

from app.services.analysis_service import AnalysisService
from app.services.security_service import SecurityService

ws = Path(__file__).resolve().parent

print("====================================================")
print(" 1. ARCHITECTURAL ROT & CIRCULAR DEPENDENCY SCAN")
print("====================================================")
arch = AnalysisService.analyze_architecture(ws)
print(f"Languages: {arch['languages']}")
print(f"Circular Import Cycles Found: {len(arch['circular_dependencies'])}")
for cycle in arch["circular_dependencies"]:
    print(f" -> Cycle Detected: {' <---> '.join(cycle)}")
print(f"Summary: {arch['summary']}\n")

print("====================================================")
print(" 2. PROMPT INJECTION DEFENSE SCAN (README.md)")
print("====================================================")
readme = (ws / "README.md").read_text(encoding="utf-8")
is_safe, risk, patterns, sanitized = SecurityService.scan_for_prompt_injection(readme)
print(f"Is Safe: {is_safe}")
print(f"Risk Level: {risk}")
print(f"Detected Attack Signatures: {patterns}")
print(f"Sanitized Prompt Output:\n{sanitized.strip()}\n")

print("====================================================")
print(" 3. LEAKED SECRET & CREDENTIAL SCAN (config.py)")
print("====================================================")
config_text = (ws / "config.py").read_text(encoding="utf-8")
findings = SecurityService.scan_content_for_secrets("config.py", config_text)
print(f"Total Security Violations: {len(findings)}")
for f in findings:
    print(f" [{f.severity}] {f.type} at line {f.line_number}: {f.description}")
    print(f"    Snippet: {f.snippet}")
