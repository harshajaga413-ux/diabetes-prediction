Enable Claude Haiku 4.5 - automation helper

Overview
- These scripts are generic automation helpers to enable a model (default: "claude-haiku-4.5") for all clients using an admin REST API.
- They do not assume any specific vendor API; you must supply endpoints and the admin token.

Files
- `enable_claude_haiku.py` - Python script (recommended) using `requests`.
- `enable_claude_haiku.ps1` - PowerShell helper.

Prerequisites
- Keep admin tokens secret. Do not commit tokens to source control.
- Python script: `pip install requests`

Usage examples

1) Generic (Python)

```powershell
$env:ADMIN_TOKEN = '<<paste-token-here>>'
python .\scripts\enable_claude_haiku.py `
  --api-base https://api.example.com `
  --list-endpoint /admin/clients `
  --id-field id `
  --enable-endpoint-template /admin/clients/{client_id}/models `
  --method POST `
  --token-env ADMIN_TOKEN `
  --model claude-haiku-4.5 `
  --dry-run
```

2) Generic (PowerShell)

```powershell
$env:ADMIN_TOKEN = '<<paste-token-here>>'
.\scripts\enable_claude_haiku.ps1 -ApiBase 'https://api.example.com' -ListEndpoint '/admin/clients' -EnableEndpointTemplate '/admin/clients/{0}/models' -Model 'claude-haiku-4.5' -DryRun
```

Tips
- If the list endpoint is paginated, either use a list endpoint that returns all clients or add pagination handling to the scripts.
- If the enable endpoint requires a different JSON shape, adjust `--body-template` (Python) or modify the PowerShell body.
- Test with `--dry-run` first to see requests without sending them.

Security
- Use environment variables, secret managers, or CI/CD secret stores to provide the admin token.
- Limit the admin token scope to only the actions required.

Next steps I can do for you
- Adapt the script to a specific provider (Anthropic/Okta/internal API) if you share the admin API docs or the exact endpoints.
- Add pagination support and concurrent requests with rate-limit handling.
- Create an idempotent check that only enables the model when currently disabled.
