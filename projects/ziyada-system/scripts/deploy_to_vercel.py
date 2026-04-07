#!/usr/bin/env python3
"""
Deploy Ziyada System to Vercel + Configure Domain
---------------------------------------------------
This script:
1. Creates a Vercel project linked to the GitHub repo
2. Sets all environment variables
3. Triggers a deployment
4. Adds the ziyadasystem.com domain

Usage:
  python deploy_to_vercel.py

You need a Vercel token. Get it from:
  https://vercel.com/account/tokens → Create Token

Requirements: pip install requests
"""

import os
import json
import sys
import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN", "").strip()

GITHUB_REPO  = "alibiggyaf/ziyada-system-website"
PROJECT_NAME = "ziyada-system-website"
DOMAIN       = "ziyadasystem.com"
WWW_DOMAIN   = "www.ziyadasystem.com"

# Production environment variables (non-secret values safe to embed here)
# IMPORTANT: The Supabase anon key is a public key - safe to include
ENV_VARS = [
    ("VITE_SUPABASE_URL",          "https://nuyscajjlhxviuyrxzyq.supabase.co"),
    ("VITE_SUPABASE_ANON_KEY",     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51eXNjYWpqbGh4dml1eXJ4enlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzNjk0MzAsImV4cCI6MjA5MDk0NTQzMH0.8pMN29L6WYRBB64LyhnH1hCDr0ZnBwhImmm4ubhwSp8"),
    ("VITE_CHATBOT_WEBHOOK",        "/n8n/webhook/3c9f6cb1-a3ce-4302-8260-6748f093520d/chat"),
    ("VITE_CHATBOT_ENABLED",        "true"),
    ("VITE_N8N_NSI_WEBHOOK",        "/n8n/webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat"),
    ("VITE_N8N_YOUTUBE_WEBHOOK",    "/n8n/webhook/ff9622a4-a6ec-4396-b9de-c95bd834c23c/chat"),
    ("VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK",  "/n8n/webhook/trigger-scrape"),
    ("VITE_N8N_COMPETITOR_GENERATE_WEBHOOK", "/n8n/webhook/competitor-generate"),
    ("VITE_N8N_BLOG_PUBLISHER_WEBHOOK",      "/n8n/webhook/publish-blog-draft"),
    ("VITE_HOTJAR_ID",             "867a324ef296e"),
]

HEADERS = {
    "Authorization": f"Bearer {VERCEL_TOKEN}",
    "Content-Type": "application/json",
}

# ── HELPERS ───────────────────────────────────────────────────────────────────

def api(method, path, **kwargs):
    url = f"https://api.vercel.com{path}"
    resp = requests.request(method, url, headers=HEADERS, timeout=30, **kwargs)
    return resp

def check_token():
    r = api("GET", "/v2/user")
    if r.status_code == 200:
        u = r.json().get("user", {})
        print(f"  ✓ Logged in as: {u.get('name','?')} ({u.get('email','?')})")
        return True
    print(f"  ✗ Token invalid: {r.status_code} {r.text[:100]}")
    return False

def get_or_create_project():
    # Check if project exists
    r = api("GET", f"/v9/projects/{PROJECT_NAME}")
    if r.status_code == 200:
        proj = r.json()
        print(f"  ✓ Project exists: {proj['name']} (id={proj['id']})")
        return proj["id"]

    # Create project linked to GitHub
    print("  Creating new Vercel project...")
    payload = {
        "name": PROJECT_NAME,
        "framework": "vite",
        "gitRepository": {
            "type": "github",
            "repo": GITHUB_REPO,
        },
        "buildCommand": "npm run build",
        "outputDirectory": "dist",
        "installCommand": "npm install",
    }
    r = api("POST", "/v10/projects", json=payload)
    if r.status_code in (200, 201):
        proj = r.json()
        print(f"  ✓ Created project: {proj['name']} (id={proj['id']})")
        return proj["id"]
    print(f"  ✗ Failed to create project: {r.status_code} {r.text[:300]}")
    return None

def set_env_vars(project_id):
    print(f"  Setting {len(ENV_VARS)} environment variables...")
    env_payload = []
    for key, value in ENV_VARS:
        env_payload.append({
            "key": key,
            "value": value,
            "type": "plain",
            "target": ["production", "preview", "development"],
        })

    r = api("POST", f"/v10/projects/{project_id}/env", json=env_payload)
    if r.status_code in (200, 201):
        created = r.json()
        count = len(created) if isinstance(created, list) else 1
        print(f"  ✓ Set {count} environment variables")
        return True
    elif r.status_code == 409:
        # Some vars already exist — update each one
        print("  Some vars exist, updating individually...")
        for key, value in ENV_VARS:
            # Get existing
            r2 = api("GET", f"/v10/projects/{project_id}/env")
            if r2.status_code == 200:
                existing = {e["key"]: e["id"] for e in r2.json().get("envs", [])}
                if key in existing:
                    env_id = existing[key]
                    api("PATCH", f"/v10/projects/{project_id}/env/{env_id}",
                        json={"value": value, "target": ["production","preview","development"]})
                else:
                    api("POST", f"/v10/projects/{project_id}/env",
                        json=[{"key": key, "value": value, "type": "plain",
                               "target": ["production","preview","development"]}])
        print("  ✓ Environment variables updated")
        return True
    print(f"  ✗ Failed to set env vars: {r.status_code} {r.text[:300]}")
    return False

def trigger_deployment(project_id):
    # Get the latest deployment to redeploy, or trigger fresh
    r = api("POST", f"/v13/deployments",
        json={
            "name": PROJECT_NAME,
            "gitSource": {
                "type": "github",
                "repoId": None,  # Will be auto-resolved
                "ref": "main",
            },
            "project": project_id,
            "target": "production",
        })
    if r.status_code in (200, 201):
        dep = r.json()
        dep_url = dep.get("url") or dep.get("deploymentId", "")
        print(f"  ✓ Deployment triggered: https://{dep_url}")
        return True
    # Fallback: push-based deployments happen automatically via GitHub integration
    print(f"  ⚠ Direct deploy returned {r.status_code} — deployment will auto-trigger on next GitHub push")
    return False

def add_domain(project_id):
    for domain in [DOMAIN, WWW_DOMAIN]:
        r = api("POST", f"/v10/projects/{project_id}/domains",
                json={"name": domain})
        if r.status_code in (200, 201):
            d = r.json()
            verified = d.get("verified", False)
            status = "verified" if verified else "pending DNS"
            print(f"  ✓ Added domain: {domain} ({status})")
            if not verified:
                # Show DNS records needed
                verification = d.get("verification", [])
                for v in verification:
                    print(f"    DNS needed: {v.get('type')} {v.get('domain')} → {v.get('value')}")
        elif r.status_code == 409:
            print(f"  ✓ Domain already added: {domain}")
        else:
            print(f"  ⚠ {domain}: {r.status_code} {r.text[:150]}")

def get_dns_records(project_id):
    """Print the DNS records needed in Cloudflare."""
    r = api("GET", f"/v10/projects/{project_id}/domains")
    if r.status_code != 200:
        return
    domains = r.json().get("domains", [])
    print("\n  DNS records to add in Cloudflare:")
    print("  ────────────────────────────────────────────────────────")
    print("  Type  Name   Value                     Notes")
    print("  ────────────────────────────────────────────────────────")
    print("  A     @      76.76.21.21               Root domain (DNS Only - grey cloud)")
    print("  CNAME www    cname.vercel-dns.com       www subdomain (DNS Only - grey cloud)")
    print("  ────────────────────────────────────────────────────────")
    print("  ⚠ IMPORTANT: Set Cloudflare proxy to DNS Only (grey cloud) NOT orange/proxied")

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    global VERCEL_TOKEN, HEADERS

    print("\n=== Ziyada System → Vercel Deployment ===\n")

    # Get token
    if not VERCEL_TOKEN:
        print("Enter your Vercel token (get from https://vercel.com/account/tokens):")
        VERCEL_TOKEN = input("Token: ").strip()
        if not VERCEL_TOKEN:
            print("No token provided. Exiting.")
            sys.exit(1)
        HEADERS["Authorization"] = f"Bearer {VERCEL_TOKEN}"

    # 1. Check auth
    print("1. Checking Vercel authentication...")
    if not check_token():
        sys.exit(1)

    # 2. Get or create project
    print("\n2. Setting up Vercel project...")
    project_id = get_or_create_project()
    if not project_id:
        sys.exit(1)

    # 3. Set environment variables
    print("\n3. Configuring environment variables...")
    set_env_vars(project_id)

    # 4. Add domain
    print("\n4. Adding domain ziyadasystem.com...")
    add_domain(project_id)

    # 5. Show DNS records
    get_dns_records(project_id)

    # 6. Summary
    print("\n=== DONE ===\n")
    print(f"  Vercel Project: https://vercel.com/{PROJECT_NAME}")
    print(f"  Website will be live at: https://{DOMAIN}")
    print()
    print("  Remaining manual steps:")
    print("  1. Add DNS records in Cloudflare (see above) — set to DNS Only (grey cloud)")
    print("  2. Wait 1-5 min → Vercel auto-provisions SSL")
    print("  3. Add Supabase service_role key to N8N (see DEPLOYMENT_CHECKLIST.md Step 5)")
    print("  4. Set up HubSpot Private App (see DEPLOYMENT_CHECKLIST.md Step 6)")
    print()
    print("  Test: curl https://ziyadasystem.com")
    print()

if __name__ == "__main__":
    main()
