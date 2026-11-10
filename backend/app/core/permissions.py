from enum import Enum
from typing import List


class Role(str, Enum):
    ADMIN = "admin"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Permission(str, Enum):
    REPO_READ = "repo:read"
    REPO_CLONE = "repo:clone"
    REPO_FORK = "repo:fork"
    CODE_EXECUTE = "code:execute"
    WORKFLOW_RUN = "workflow:run"
    APPROVAL_GRANT = "approval:grant"
    DEPLOY_PUBLISH = "deploy:publish"


ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],
    Role.ARCHITECT: [
        Permission.REPO_READ,
        Permission.REPO_CLONE,
        Permission.CODE_EXECUTE,
        Permission.WORKFLOW_RUN,
        Permission.APPROVAL_GRANT,
    ],
    Role.DEVELOPER: [
        Permission.REPO_READ,
        Permission.REPO_CLONE,
        Permission.CODE_EXECUTE,
        Permission.WORKFLOW_RUN,
    ],
    Role.VIEWER: [
        Permission.REPO_READ,
    ],
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
