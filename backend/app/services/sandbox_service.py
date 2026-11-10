import subprocess
import shlex
import time
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import settings
from app.core.exceptions import (
    SandboxUnavailableError,
    SecurityViolationError,
)
from app.core.logging import logger

COMMAND_ALLOWLIST = {
    "pytest",
    "python",
    "git",
    "npm",
    "node",
    "cargo",
    "go",
    "mvn",
    "gradle",
    "dotnet",
}


class SandboxService:
    @classmethod
    def execute_command(
        cls,
        command: str,
        working_dir: Path,
        timeout_seconds: int = 30,
        env_vars: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Safely executes a command in a sandboxed working directory with timeout and allowlist."""
        # Validate that working_dir is within workspaces or artifacts
        resolved_dir = working_dir.resolve()
        if not (
            resolved_dir.is_relative_to(settings.WORKSPACE_ROOT.resolve())
            or resolved_dir.is_relative_to(settings.ARTIFACTS_ROOT.resolve())
            or resolved_dir.is_relative_to(settings.BASE_DIR.resolve())
        ):
            raise SecurityViolationError("Command execution outside authorized workspace roots is strictly forbidden.")

        # Parse command tokens
        parts = shlex.split(command, posix=False)
        if not parts:
            raise SecurityViolationError("Empty command string provided.")

        binary = Path(parts[0]).name.lower().replace(".exe", "")
        if binary not in COMMAND_ALLOWLIST:
            raise SecurityViolationError(
                f"Binary '{binary}' is not in the execution allowlist: {sorted(list(COMMAND_ALLOWLIST))}"
            )

        # Basic forbidden argument scanning
        forbidden_tokens = [";", "&&", "||", "|", "`", "$", "\n", "\r", ">", "<"]
        for token in forbidden_tokens:
            if token in command:
                raise SecurityViolationError(f"Shell redirection or chaining token '{token}' is blocked.")

        start_time = time.time()
        logger.info(f"Sandbox executing: '{command}' in '{resolved_dir}'")

        try:
            res = subprocess.run(
                parts,
                cwd=resolved_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Sanitize any accidental token leaks from output
            stdout = res.stdout
            stderr = res.stderr
            if settings.GITHUB_TOKEN:
                stdout = stdout.replace(settings.GITHUB_TOKEN, "***")
                stderr = stderr.replace(settings.GITHUB_TOKEN, "***")

            return {
                "exit_code": res.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "duration_ms": duration_ms,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                "duration_ms": int((time.time() - start_time) * 1000),
                "timed_out": True,
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Sandbox execution error: {str(e)}",
                "duration_ms": int((time.time() - start_time) * 1000),
                "timed_out": False,
            }
