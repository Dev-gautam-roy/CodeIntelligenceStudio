import re
import subprocess
import httpx
from typing import Optional, Tuple, Dict, Any
from app.core.config import settings
from app.core.exceptions import (
    GitHubAuthRequiredError,
    RepositoryNotFoundError,
    CodeIntelError,
)
from app.core.logging import logger

GITHUB_URL_PATTERN = re.compile(
    r"^https?://github\.com/(?P<owner>[a-zA-Z0-9_\-\.]+)/(?P<repo>[a-zA-Z0-9_\-\.]+?)(?:\.git)?/?$"
)


def get_active_github_token() -> Optional[str]:
    """Retrieves active GitHub token from settings or local authenticated gh CLI."""
    if settings.GITHUB_TOKEN:
        return settings.GITHUB_TOKEN.strip()
    try:
        # Check if gh CLI has a token cached in keyring
        res = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    return None


class GitHubService:
    @staticmethod
    def parse_github_url(url: str) -> Tuple[str, str]:
        """Parses and validates a GitHub URL into (owner, repo)."""
        match = GITHUB_URL_PATTERN.match(url.strip())
        if not match:
            raise CodeIntelError(
                error_code="INVALID_GITHUB_URL",
                message=f"'{url}' is not a valid GitHub repository URL format.",
                suggested_resolution="Expected format: https://github.com/owner/repository",
            )
        return match.group("owner"), match.group("repo")

    @classmethod
    async def validate_repository(cls, url: str) -> Dict[str, Any]:
        """Validates a repository by calling the official GitHub REST API."""
        owner, repo = cls.parse_github_url(url)
        token = get_active_github_token()

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeIntelligenceStudio/0.1.0",
        }
        if token:
            headers["Authorization"] = f"token {token}"

        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(api_url, headers=headers)
            except httpx.RequestError as exc:
                raise CodeIntelError(
                    error_code="GITHUB_API_UNREACHABLE",
                    message=f"Network error contacting GitHub API: {str(exc)}",
                    retryable=True,
                )

        if response.status_code == 404:
            if not token:
                raise RepositoryNotFoundError(
                    repo_url=url,
                    details={"hint": "Repository may be private. Authenticate to access private repositories."},
                )
            raise RepositoryNotFoundError(repo_url=url)
        elif response.status_code == 401:
            raise GitHubAuthRequiredError(
                message="GitHub token was rejected (401 Unauthorized)."
            )
        elif response.status_code != 200:
            raise CodeIntelError(
                error_code=f"GITHUB_ERROR_{response.status_code}",
                message=f"GitHub API returned HTTP {response.status_code}: {response.text}",
                retryable=response.status_code >= 500,
            )

        data = response.json()
        return {
            "valid": True,
            "owner": data.get("owner", {}).get("login", owner),
            "repo": data.get("name", repo),
            "default_branch": data.get("default_branch", "main"),
            "is_private": data.get("private", False),
            "description": data.get("description"),
            "stars": data.get("stargazers_count", 0),
            "forks_count": data.get("forks_count", 0),
            "message": f"Successfully verified repository {owner}/{repo}.",
        }

    @classmethod
    async def fork_repository(cls, url: str, organization: Optional[str] = None) -> Dict[str, Any]:
        """Triggers a repository fork using the official GitHub REST API."""
        owner, repo = cls.parse_github_url(url)
        token = get_active_github_token()
        if not token:
            raise GitHubAuthRequiredError("Forking requires an authenticated GitHub token with 'repo' scope.")

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}",
            "User-Agent": "CodeIntelligenceStudio/0.1.0",
        }
        api_url = f"https://api.github.com/repos/{owner}/{repo}/forks"
        payload = {}
        if organization:
            payload["organization"] = organization

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)

        if response.status_code in (200, 202):
            data = response.json()
            return {
                "forked": True,
                "fork_url": data.get("html_url", ""),
                "owner": data.get("owner", {}).get("login", ""),
                "repo": data.get("name", repo),
                "message": f"Successfully initiated fork of {owner}/{repo} to {data.get('html_url')}.",
            }
        elif response.status_code == 403:
            raise CodeIntelError(
                error_code="GITHUB_PERMISSION_DENIED",
                message=f"GitHub denied fork request: {response.text}",
                suggested_resolution="Ensure your GitHub token has write access and permission to fork repositories.",
            )
        else:
            raise CodeIntelError(
                error_code=f"GITHUB_FORK_ERROR_{response.status_code}",
                message=f"GitHub fork API failed with HTTP {response.status_code}: {response.text}",
            )
