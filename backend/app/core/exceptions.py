from datetime import datetime, timezone
from typing import Any, Dict, Optional


class CodeIntelError(Exception):
    """Base exception for all Code Intelligence Studio operations."""

    def __init__(
        self,
        error_code: str,
        message: str,
        operation: str = "UNKNOWN",
        execution_id: Optional[str] = None,
        suggested_resolution: Optional[str] = None,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.operation = operation
        self.execution_id = execution_id
        self.suggested_resolution = suggested_resolution
        self.retryable = retryable
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "operation": self.operation,
            "execution_id": self.execution_id,
            "suggested_resolution": self.suggested_resolution,
            "retryable": self.retryable,
            "details": self.details,
            "timestamp": self.timestamp,
        }


# Specialized Subsystem Exceptions
class GitHubAuthRequiredError(CodeIntelError):
    def __init__(self, message: str = "GitHub authentication token is required or expired.", **kwargs):
        super().__init__(
            error_code="GITHUB_AUTH_REQUIRED",
            message=message,
            suggested_resolution="Set GITHUB_TOKEN in your environment or authenticate via 'gh auth login'.",
            retryable=False,
            **kwargs,
        )


class RepositoryNotFoundError(CodeIntelError):
    def __init__(self, repo_url: str, **kwargs):
        super().__init__(
            error_code="REPOSITORY_NOT_FOUND",
            message=f"Repository could not be found at {repo_url}.",
            suggested_resolution="Verify the URL syntax, owner/repo names, and repository visibility permissions.",
            retryable=False,
            details={"repo_url": repo_url},
            **kwargs,
        )


class CloneFailedError(CodeIntelError):
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            error_code="CLONE_FAILED",
            message=f"Git clone operation failed: {reason}",
            suggested_resolution="Check disk space, network connectivity, and repository read permissions.",
            retryable=True,
            **kwargs,
        )


class SandboxUnavailableError(CodeIntelError):
    def __init__(self, reason: str = "Execution sandbox adapter is offline or unsupported.", **kwargs):
        super().__init__(
            error_code="SANDBOX_UNAVAILABLE",
            message=reason,
            suggested_resolution="Start Docker Desktop or allow process isolation sandbox in settings.",
            retryable=False,
            **kwargs,
        )


class ModelProviderUnavailableError(CodeIntelError):
    def __init__(self, provider: str, reason: str, **kwargs):
        super().__init__(
            error_code="MODEL_PROVIDER_UNAVAILABLE",
            message=f"Model provider '{provider}' is currently unavailable: {reason}",
            suggested_resolution="Check your API keys or switch to another configured provider.",
            retryable=True,
            details={"provider": provider},
            **kwargs,
        )


class ApprovalRequiredError(CodeIntelError):
    def __init__(self, action: str, approval_id: str, **kwargs):
        super().__init__(
            error_code="APPROVAL_REQUIRED",
            message=f"Operation '{action}' requires explicit human approval before execution.",
            suggested_resolution="Review the pending action in the Approvals Center or via 'codeintel approval approve'.",
            retryable=True,
            details={"action": action, "approval_id": approval_id},
            **kwargs,
        )


class SecurityViolationError(CodeIntelError):
    def __init__(self, reason: str, **kwargs):
        super().__init__(
            error_code="SECURITY_VIOLATION",
            message=f"Security policy violation: {reason}",
            suggested_resolution="Operation was blocked to prevent host compromise or data leakage.",
            retryable=False,
            **kwargs,
        )


class PathTraversalError(SecurityViolationError):
    def __init__(self, path: str, **kwargs):
        super().__init__(
            reason=f"Path traversal escape attempt detected for '{path}'.",
            details={"path": path},
            **kwargs,
        )
