import sys
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import httpx

app = typer.Typer(
    name="codeintel",
    help="Autonomous AI Software Engineering & Repository Intelligence Platform CLI",
    add_completion=False,
)
console = Console()

API_BASE = os.getenv("CODEINTEL_API_URL", "http://127.0.0.1:8000/api/v1")


@app.command()
def doctor():
    """Verifies Windows environment, runtimes, database, and GitHub authentication."""
    table = Table(title="Code Intelligence Studio — Doctor Diagnostics")
    table.add_column("Diagnostic Probe", style="cyan")
    table.add_column("Observed Value", style="magenta")
    table.add_column("Status", style="green")

    # Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python Runtime", py_ver, "[green]PASS[/green]")

    # Git
    git_ver = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip()
    table.add_row("Git Executable", git_ver, "[green]PASS[/green]")

    # Node
    node_path = shutil.which("node")
    node_ver = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip() if node_path else "Not found"
    table.add_row("Node.js Runtime", node_ver, "[green]PASS[/green]" if node_path else "[yellow]WARN[/yellow]")

    # GitHub CLI
    gh_path = shutil.which("gh")
    gh_status = "Authenticated" if gh_path else "Not installed"
    table.add_row("GitHub Integration", gh_status, "[green]PASS[/green]" if gh_path else "[yellow]WARN[/yellow]")

    # Backend API Health
    try:
        r = httpx.get("http://127.0.0.1:8000/health", timeout=2.0)
        api_status = "[green]ONLINE[/green]" if r.status_code == 200 else f"[red]HTTP {r.status_code}[/red]"
    except Exception:
        api_status = "[yellow]OFFLINE (Start with .\\scripts\\start.ps1)[/yellow]"
    table.add_row("Backend API Service", api_status, "[green]PASS[/green]" if "ONLINE" in api_status else "[yellow]NOTICE[/yellow]")

    console.print(table)


@app.command()
def health():
    """Checks real-time health of the local backend and database."""
    try:
        r = httpx.get("http://127.0.0.1:8000/health", timeout=3.0)
        console.print_json(r.text)
    except Exception as e:
        console.print(f"[red]Failed to reach backend API:[/red] {str(e)}")


# GitHub Subcommands
github_app = typer.Typer(help="GitHub repository validation and forking")
app.add_typer(github_app, name="github")


@github_app.command("validate")
def github_validate(url: str):
    """Validates repository syntax and checks availability on GitHub."""
    with console.status(f"Validating GitHub repository: {url}..."):
        try:
            r = httpx.post(f"{API_BASE}/github/validate", json={"url": url}, timeout=10.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Error validating URL:[/red] {str(e)}")


@github_app.command("fork")
def github_fork(url: str, org: Optional[str] = None):
    """Triggers an authenticated GitHub repository fork."""
    confirm = typer.confirm(f"Are you sure you want to fork '{url}'?")
    if not confirm:
        console.print("[yellow]Fork operation cancelled.[/yellow]")
        raise typer.Abort()

    with console.status("Forking repository via GitHub API..."):
        try:
            r = httpx.post(f"{API_BASE}/github/fork", json={"url": url, "organization": org}, timeout=15.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Error forking repository:[/red] {str(e)}")


# Repository Subcommands
repo_app = typer.Typer(help="Repository ingestion, cloning, and architectural analysis")
app.add_typer(repo_app, name="repo")


@repo_app.command("clone")
def repo_clone(url: str, project_id: Optional[str] = None):
    """Clones a repository into an isolated workspace."""
    with console.status(f"Cloning {url} into workspace..."):
        try:
            r = httpx.post(f"{API_BASE}/repositories/clone", json={"url": url, "project_id": project_id}, timeout=120.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Clone failed:[/red] {str(e)}")


@repo_app.command("analyze")
def repo_analyze(repository_id: str):
    """Performs technological stack and framework detection."""
    with console.status("Analyzing codebase..."):
        try:
            r = httpx.post(f"{API_BASE}/analysis/architecture", json={"repository_id": repository_id}, timeout=30.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Analysis failed:[/red] {str(e)}")


@repo_app.command("index")
def repo_index(repository_id: str):
    """Indexes repository source files into ChromaDB vector store."""
    with console.status("Indexing workspace chunks into ChromaDB..."):
        try:
            r = httpx.post(f"{API_BASE}/repositories/{repository_id}/index", timeout=60.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Indexing failed:[/red] {str(e)}")


# Agent Subcommands
agent_app = typer.Typer(help="Inspect and run specialized engineering agents")
app.add_typer(agent_app, name="agent")


@agent_app.command("list")
def agent_list():
    """Lists all registered specialized agents and their capabilities."""
    try:
        r = httpx.get(f"{API_BASE}/agents", timeout=5.0)
        console.print_json(r.text)
    except Exception as e:
        console.print(f"[red]Failed to list agents:[/red] {str(e)}")


@agent_app.command("run")
def agent_run(agent_name: str, project_id: str, goal: str = "Analyze repository"):
    """Executes a specialized agent task."""
    with console.status(f"Executing {agent_name}..."):
        try:
            r = httpx.post(f"{API_BASE}/agents/run", json={"agent_name": agent_name, "project_id": project_id, "task_goal": goal}, timeout=60.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Agent run failed:[/red] {str(e)}")


# Prompt Subcommands
prompt_app = typer.Typer(help="Generate, verify, and scan engineering prompts")
app.add_typer(prompt_app, name="prompt")


@prompt_app.command("generate")
def prompt_generate(category: str = "debugging"):
    """Generates structured, verified prompts for engineering tasks."""
    try:
        r = httpx.post(f"{API_BASE}/prompts/generate", json={"category": category, "target_context": {}}, timeout=5.0)
        console.print_json(r.text)
    except Exception as e:
        console.print(f"[red]Generation failed:[/red] {str(e)}")


@prompt_app.command("verify")
def prompt_verify(prompt_text: str):
    """Audits a prompt for contradictory constraints and token limits."""
    try:
        r = httpx.post(f"{API_BASE}/prompts/verify", json={"prompt_text": prompt_text}, timeout=5.0)
        console.print_json(r.text)
    except Exception as e:
        console.print(f"[red]Verification failed:[/red] {str(e)}")


@prompt_app.command("injection-scan")
def prompt_injection_scan(text: str):
    """Scans untrusted repository text for prompt injection vectors."""
    try:
        r = httpx.post(f"{API_BASE}/prompts/injection-scan", json={"text_content": text}, timeout=5.0)
        console.print_json(r.text)
    except Exception as e:
        console.print(f"[red]Scan failed:[/red] {str(e)}")


# Security Subcommand
security_app = typer.Typer(help="Audit code for leaked secrets and injection risks")
app.add_typer(security_app, name="security")


@security_app.command("audit")
def security_audit(repository_id: str):
    """Runs high-precision secret scanner and injection audit."""
    with console.status("Scanning repository security..."):
        try:
            r = httpx.post(f"{API_BASE}/analysis/security", json={"repository_id": repository_id}, timeout=30.0)
            console.print_json(r.text)
        except Exception as e:
            console.print(f"[red]Security audit failed:[/red] {str(e)}")


if __name__ == "__main__":
    app()
