import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from app.core.config import settings
from app.core.exceptions import (
    CloneFailedError,
    PathTraversalError,
    SecurityViolationError,
)
from app.core.logging import logger
from app.services.github_service import get_active_github_token, GitHubService


class WorkspaceService:
    @staticmethod
    def get_workspace_root() -> Path:
        root = settings.WORKSPACE_ROOT.resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root

    @classmethod
    def validate_safe_path(cls, base_dir: Path, relative_path: str) -> Path:
        """Enforces filesystem jail, rejecting traversal attempts (..) or absolute escapes."""
        base_dir_resolved = base_dir.resolve()
        target = (base_dir / relative_path).resolve()
        try:
            target.relative_to(base_dir_resolved)
        except ValueError:
            raise PathTraversalError(path=str(relative_path))
        return target

    @classmethod
    def clone_repository(
        cls,
        repo_url: str,
        project_id: str,
        branch: Optional[str] = None,
    ) -> Tuple[Path, str]:
        """Clones a GitHub repository into an isolated workspace directory."""
        owner, repo = GitHubService.parse_github_url(repo_url)
        dest_dir = cls.get_workspace_root() / project_id / f"{owner}_{repo}"

        if dest_dir.exists():
            # If already cloned, verify integrity and pull head SHA
            try:
                res = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=dest_dir,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5,
                )
                head_sha = res.stdout.strip()
                logger.info(f"Using existing repository clone at {dest_dir} (SHA: {head_sha})")
                return dest_dir, head_sha
            except Exception:
                shutil.rmtree(dest_dir, ignore_errors=True)

        dest_dir.parent.mkdir(parents=True, exist_ok=True)

        # Build authenticated clone URL if token is present
        token = get_active_github_token()
        clone_url = repo_url
        if token:
            clone_url = f"https://x-access-token:{token}@github.com/{owner}/{repo}.git"

        cmd = ["git", "clone", "--depth", "1"]
        if branch:
            cmd.extend(["--branch", branch])
        cmd.extend([clone_url, str(dest_dir)])

        logger.info(f"Cloning repository {owner}/{repo} into workspace {dest_dir}...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                # Sanitize token from error outputs
                err_msg = result.stderr.replace(token, "***") if token else result.stderr
                raise CloneFailedError(reason=err_msg.strip())

            # Read HEAD commit SHA
            sha_res = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=dest_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            head_sha = sha_res.stdout.strip()
            logger.info(f"Successfully cloned {owner}/{repo} (HEAD: {head_sha})")
            return dest_dir, head_sha

        except subprocess.TimeoutExpired:
            raise CloneFailedError(reason="Git clone operation timed out after 120 seconds.")
        except Exception as exc:
            if not isinstance(exc, CloneFailedError):
                raise CloneFailedError(reason=str(exc))
            raise exc
