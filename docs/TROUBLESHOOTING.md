# Troubleshooting Guide — Code Intelligence Studio

## Common Issues & Resolutions

### 1. Backend Service Offline (Connection Refused on Port 8000)
- **Symptom**: `codeintel doctor` reports Backend API Service `OFFLINE`.
- **Cause**: Backend process was stopped or failed to bind to port 8000.
- **Resolution**:
  1. Check if another process is occupying port 8000:
     ```powershell
     Get-NetTCPConnection -LocalPort 8000
     ```
  2. Launch services using `.\scripts\start.ps1`.
  3. Inspect `logs/app.log` for runtime exceptions.

### 2. GitHub API Rate Limits or 401 Unauthorized
- **Symptom**: `GITHUB_API_UNREACHABLE` or `GITHUB_AUTH_REQUIRED`.
- **Resolution**:
  - For public repositories, unauthenticated rate limits apply (60 req/hr).
  - Authenticate using GitHub CLI:
    ```powershell
    gh auth login
    ```
  - Or export a Personal Access Token:
    ```powershell
    $env:GITHUB_TOKEN = "ghp_your_token_here"
    ```

### 3. Path Traversal Block (`PATH_TRAVERSAL_DETECTED`)
- **Symptom**: Security exception raised when indexing or running tests.
- **Cause**: A repository path attempted to reference files outside `workspaces/:project_id/` using `..` or absolute paths.
- **Resolution**: This is an intentional security safeguard protecting your workstation. Verify repository symlinks and relative path configurations.

### 4. Sandbox Command Denied
- **Symptom**: `Binary 'xyz' is not in the execution allowlist`.
- **Resolution**: To prevent host compromise, only standard developer tools are permitted (`pytest`, `python`, `git`, `npm`, `cargo`, `go`).
