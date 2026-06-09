#!/usr/bin/env python3
"""Enable GitHub Pages for the osoul-dashboard repo."""
import os, json, urllib.request, re

# Read token from .env
env_path = os.path.expanduser("~/.hermes/.env")
with open(env_path) as f:
    content = f.read()

# Find GITHUB_TOKEN line
match = re.search(r'^GITHUB_TOKEN=***"", content, re.MULTILINE)
if not match:
    print("GITHUB_TOKEN not found in .env")
    exit(1)

token = match.group(1).strip().strip("'")
print(f"Token: {len(token)} chars, prefix: {token[:4]}...")

# Enable GitHub Pages on master branch
data = json.dumps({
    "source": {
        "branch": "master",
        "path": "/"
    }
}).encode()

url = "https://api.github.com/repos/Alebrahim22/osoul-dashboard/pages"
headers = {
    "Authorization": f"token {token}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Hermes"
}

# Try POST first, fallback to PUT
for method in ["POST", "PUT"]:
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        page = json.loads(resp.read())
        print("GitHub Pages enabled!")
        print("URL: https://alebrahim22.github.io/osoul-dashboard/")
        print("Wait 1-2 minutes for first deploy")
        break
    except urllib.error.HTTPError as e:
        if e.code == 404 and "pages" in e.read().decode().lower():
            # Need to create a gh-pages branch first
            print("Creating gh-pages branch...")
            # Get the master branch SHA
            req_get = urllib.request.Request(
                "https://api.github.com/repos/Alebrahim22/osoul-dashboard/git/refs/heads/master",
                headers=headers
            )
            resp_get = urllib.request.urlopen(req_get)
            ref_data = json.loads(resp_get.read())
            sha = ref_data["object"]["sha"]
            
            # Create gh-pages branch from master
            branch_data = json.dumps({
                "ref": "refs/heads/gh-pages",
                "sha": sha
            }).encode()
            req_branch = urllib.request.Request(
                "https://api.github.com/repos/Alebrahim22/osoul-dashboard/git/refs",
                data=branch_data, method="POST", headers=headers
            )
            try:
                urllib.request.urlopen(req_branch)
                print("gh-pages branch created")
            except urllib.error.HTTPError as be:
                err = json.loads(be.read().decode())
                print(f"Branch error: {err.get('message')}")
            
            # Now try pages with gh-pages
            data_pages = json.dumps({
                "source": {"branch": "gh-pages", "path": "/"}
            }).encode()
            req_pages = urllib.request.Request(url, data=data_pages, method="POST", headers=headers)
            try:
                resp_pages = urllib.request.urlopen(req_pages)
                print("GitHub Pages enabled on gh-pages!")
                print("URL: https://alebrahim22.github.io/osoul-dashboard/")
            except urllib.error.HTTPError as pe:
                err = json.loads(pe.read().decode())
                print(f"Pages error: {err.get('message')}")
            break
        elif e.code == 409:
            # Already configured - might work already
            print("Already configured! Try: https://alebrahim22.github.io/osoul-dashboard/")
            break
        else:
            err_body = e.read().decode()
            print(f"Error ({method}): {err_body[:300]}")
