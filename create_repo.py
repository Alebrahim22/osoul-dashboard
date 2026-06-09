#!/usr/bin/env python3
import os, json, urllib.request, re

# Read token from .env
with open(os.path.expanduser("~/.hermes/.env")) as f:
    for line in f:
        if line.startswith("GITHUB_TOKEN="):
            token = line.split("=", 1)[1].strip().strip("'\"").strip()
            break

print(f"Token: {len(token)} chars, starts with: {token[:4]}...")

# Create repo
data = json.dumps({
    "name": "osoul-dashboard",
    "description": "Osoul Paper Trading Dashboard - نظام التداول الورقي",
    "private": False,
    "auto_init": True
}).encode()

req = urllib.request.Request("https://api.github.com/user/repos", data=data, method="POST")
req.add_header("Authorization", f"token {token}")
req.add_header("Content-Type", "application/json")
req.add_header("User-Agent", "Hermes")

try:
    resp = urllib.request.urlopen(req)
    repo = json.loads(resp.read())
    print(f"✅ Created: {repo['full_name']}")
    print(f"   URL: {repo['html_url']}")
except urllib.error.HTTPError as e:
    err = json.loads(e.read())
    print(f"❌ {err.get('message')}")
    if 'errors' in err:
        for er in err['errors']:
            print(f"   - {er.get('message')}")
    print(f"   HTTP: {e.code}")
