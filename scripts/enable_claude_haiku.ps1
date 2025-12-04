<#
PowerShell helper to enable a model for all clients via a generic admin REST API.
Use this script interactively; supply the admin token via an environment variable
or pass it as an argument (not recommended to put token on command line in prod).

Example:
  $env:ADMIN_TOKEN = Read-Host -AsSecureString | ConvertFrom-SecureString
  .\enable_claude_haiku.ps1 -ApiBase 'https://api.example.com' -ListEndpoint '/admin/clients' -EnableEndpointTemplate '/admin/clients/{0}/models' -Model 'claude-haiku-4.5' -DryRun

#>
param(
    [Parameter(Mandatory=$true)] [string] $ApiBase,
    [Parameter(Mandatory=$true)] [string] $ListEndpoint,
    [Parameter(Mandatory=$true)] [string] $EnableEndpointTemplate,
    [string] $IdField = 'id',
    [string] $TokenEnv = 'ADMIN_TOKEN',
    [string] $Token,
    [string] $Model = 'claude-haiku-4.5',
    [switch] $DryRun,
    [int] $WaitMs = 200
)

if (-not $Token) {
    $Token = $env:$TokenEnv
}
if (-not $Token) {
    Write-Error "No admin token provided. Set environment variable $TokenEnv or pass -Token"
    exit 2
}

$Headers = @{
    Authorization = "Bearer $Token"
    'Content-Type' = 'application/json'
    Accept = 'application/json'
}

$ListUrl = $ApiBase.TrimEnd('/') + $ListEndpoint
Write-Host "Fetching clients from $ListUrl"
$response = Invoke-RestMethod -Uri $ListUrl -Headers $Headers -Method Get -ErrorAction Stop

# try to extract list
if ($response -is [System.Array]) {
    $items = $response
} elseif ($response.PSObject.Properties.Name -contains 'items') {
    $items = $response.items
} else {
    $items = @()
    foreach ($prop in $response.PSObject.Properties) {
        if ($prop.Value -is [System.Array]) { $items = $prop.Value; break }
    }
}

if ($items.Count -eq 0) { Write-Error "No clients found or response format unexpected"; exit 1 }

Write-Host "Found $($items.Count) clients. Starting enable loop..."

$report = @()
foreach ($item in $items) {
    $clientId = $item.$IdField
    $endpoint = $EnableEndpointTemplate -f $clientId
    $url = $ApiBase.TrimEnd('/') + $endpoint
    $body = @{ model = $Model; enabled = $true } | ConvertTo-Json
    if ($DryRun) {
        Write-Host "DRY RUN: POST $url -> $body"
        $report += @{ client = $clientId; status = 'dry-run' }
    } else {
        try {
            $res = Invoke-RestMethod -Uri $url -Headers $Headers -Method Post -Body $body -ErrorAction Stop
            $report += @{ client = $clientId; status = 'ok'; response = $res }
        } catch {
            Write-Warning "Failed client $clientId: $_"
            $report += @{ client = $clientId; status = 'error'; error = $_.Exception.Message }
        }
    }
    Start-Sleep -Milliseconds $WaitMs
}

Write-Host "Done. Summary (first 10 entries):"
$report[0..([math]::Min(9, $report.Count-1))] | ConvertTo-Json -Depth 4
