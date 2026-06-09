#!/usr/bin/env python3
"""Check GitHub Pages deployment."""
import json, urllib.request, os

# Read the .env file and extract token
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("GITHUB_TOKEN="):
            # Split on first =
            token = line.split("=", 1)[1].strip().strip("'\"").strip()
            break

if not token:
    print("ERROR: token not found")
    exit(1)

print(f"Token: {len(token)} chars")

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Hermes"
}

# Check pages config
req = urllib.request.Request(
    "https://api.github.com/repos/Alebrahim22/osoul-dashboard/pages",
    headers=headers
)
try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    print(f"Status: {data.get('status', 'null')}")
    print(f"URL: {data.get('html_url', '?')}")
except urllib.error.HTTPError as e:
    err = json.loads(e.read())
    print(f"Error: {err.get('message', 'unknown')}")
    exit(1)

# Check deployments
req2 = urllib.request.Request(
    "https://api.github.com/repos/Alebrahim22/osoul-dashboard/deployments",
    headers=headers
)
resp2 = urllib.request.urlopen(req2)
deploys = json.loads(resp2.read())
if deploys:
    d = deploys[0]
    print(f"Latest: ref={d.get('ref')}, sha={d.get('sha','?')[:8]}, created={d.get('created_at','?')}")
else:
    print("No deployments yet")
