"""
Generic automation to enable a model for all clients via an admin REST API.

This script is intentionally generic: you must supply the API base URL, the
endpoint to list clients, and an endpoint template to enable the model for a
single client. The script will iterate over clients and call the enable endpoint
for each client.

Note: Do NOT store your admin token in source control. Run locally and pass the
token via an environment variable or pipeline secret.

Requirements:
    pip install requests

Example usage:
    python enable_claude_haiku.py \
      --api-base https://api.example.com \
      --list-endpoint /admin/clients \
      --id-field id \
      --enable-endpoint-template /admin/clients/{client_id}/models \
      --method POST \
      --token-env ADMIN_TOKEN \
      --model claude-haiku-4.5 \
      --dry-run

If your enable endpoint requires a different request body, use `--body-template`
(e.g. '{"model":"{model}","enabled":true}').
"""

import argparse
import os
import sys
import json
import time
from typing import List

import requests
from requests.adapters import HTTPAdapter, Retry


def build_session(token: str):
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def fetch_clients(session: requests.Session, api_base: str, list_endpoint: str, id_field: str) -> List[dict]:
    url = api_base.rstrip("/") + list_endpoint
    resp = session.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    # If the response is paginated or nested, offer simple handling:
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
    elif isinstance(data, list):
        items = data
    else:
        # Try to find a list inside
        items = None
        for v in data.values() if isinstance(data, dict) else []:
            if isinstance(v, list):
                items = v
                break
        if items is None:
            raise ValueError("Could not find client list in response; adjust arguments or inspect response JSON")
    # Normalize to list of dicts
    clients = []
    for item in items:
        if isinstance(item, dict) and id_field in item:
            clients.append(item)
    return clients


def enable_for_client(session: requests.Session, api_base: str, endpoint_template: str, client_id: str,
                      method: str, body_template: str, model: str, dry_run: bool):
    endpoint = endpoint_template.format(client_id=client_id)
    url = api_base.rstrip("/") + endpoint
    body = body_template.format(client_id=client_id, model=model)
    if dry_run:
        print(f"DRY RUN: {method} {url} -> {body}")
        return {"status": "dry-run"}
    if method.upper() == "POST":
        resp = session.post(url, data=body, timeout=20)
    elif method.upper() == "PATCH":
        resp = session.patch(url, data=body, timeout=20)
    elif method.upper() == "PUT":
        resp = session.put(url, data=body, timeout=20)
    else:
        raise ValueError("Unsupported method: " + method)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print(f"ERROR enabling client {client_id}: {e} - {resp.text}")
        return {"status": "error", "code": resp.status_code, "text": resp.text}
    try:
        return resp.json()
    except Exception:
        return {"status": "ok", "code": resp.status_code}


def main(argv=None):
    p = argparse.ArgumentParser(description="Enable model for all clients via admin API")
    p.add_argument("--api-base", required=True, help="API base URL, e.g. https://api.example.com")
    p.add_argument("--list-endpoint", required=True, help="Endpoint to list clients (path starting with /)")
    p.add_argument("--id-field", default="id", help="Field name in client object to use as client id")
    p.add_argument("--enable-endpoint-template", required=True,
                   help="Endpoint template to enable model for a client, use {client_id} placeholder, e.g. /admin/clients/{client_id}/models")
    p.add_argument("--method", default="POST", help="HTTP method to call for enabling (POST/PATCH/PUT)")
    p.add_argument("--body-template", default='{"model":"{model}","enabled":true}',
                   help="Body template (JSON) for enable request; supports {model} and {client_id}")
    p.add_argument("--token-env", default="ADMIN_TOKEN", help="Environment variable that contains admin API token")
    p.add_argument("--token", help="(Optional) Provide token directly (not recommended) - overrides token-env")
    p.add_argument("--model", default="claude-haiku-4.5", help="Model name to enable")
    p.add_argument("--dry-run", action="store_true", help="Show what would be done without sending requests")
    p.add_argument("--wait", type=float, default=0.2, help="Seconds to wait between requests (avoid rate limits)")
    args = p.parse_args(argv)

    token = args.token or os.environ.get(args.token_env)
    if not token:
        print(f"Admin token not provided. Set environment variable {args.token_env} or pass --token.")
        sys.exit(2)

    session = build_session(token)
    print("Fetching clients...")
    clients = fetch_clients(session, args.api_base, args.list_endpoint, args.id_field)
    print(f"Found {len(clients)} clients (showing up to 10):")
    for c in clients[:10]:
        print(" -", c.get(args.id_field))

    results = []
    for c in clients:
        cid = str(c[args.id_field])
        r = enable_for_client(session, args.api_base, args.enable_endpoint_template, cid,
                              args.method, args.body_template, args.model, args.dry_run)
        results.append({"client_id": cid, "result": r})
        time.sleep(args.wait)

    # Write a small report
    summary = {"total_clients": len(clients), "results_sample": results[:10]}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
