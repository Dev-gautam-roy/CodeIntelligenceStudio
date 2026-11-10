# Contributing to Code Intelligence Studio

Thank you for your interest in contributing to Code Intelligence Studio! This document outlines our engineering standards, contribution lifecycle, and testing requirements.

---

## 1. Non-Negotiable Engineering Principles
- **No Mock Paths in Production**: Every feature must connect to real integrations (GitHub APIs, real AST parsers, real vector collections).
- **Zero Host Exploitation**: All untrusted repository commands must run through the execution sandbox adapter.
- **Strict Typing**: All Python code must satisfy type checking (Pydantic / type annotations). All TypeScript code must pass strict mode compilation.
- **Human Approval Integrity**: No agent or automation may push commits or publish pull requests without explicit human sign-off via the approval gate.

---

## 2. Development Setup

### Prerequisites
- Windows 11 (or modern Linux/macOS)
- Python 3.11+ (Python 3.13 tested)
- Node.js 20+ (Node v22 LTS tested)
- Git 2.40+
- GitHub CLI (`gh`) for authenticated workflows

### Local Initialization
1. Clone the repository:
   ```powershell
   git clone https://github.com/Dev-gautam-roy/CodeIntelligenceStudio.git
   cd CodeIntelligenceStudio
   ```
2. Run automated setup:
   ```powershell
   .\scripts\setup.ps1
   ```
3. Start the application services:
   ```powershell
   .\scripts\start.ps1
   ```

---

## 3. Contribution Workflow
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Run test suites:
   ```powershell
   .\scripts\test.ps1
   ```
3. Verify linting and formatting.
4. Submit pull request with detailed rationale, linked issue, and verification evidence.
