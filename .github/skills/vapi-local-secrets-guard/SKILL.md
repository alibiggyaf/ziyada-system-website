---
name: vapi-local-secrets-guard
description: Configure and secure VAPI credentials for voice creation in local projects. Use this whenever the user mentions VAPI, voice agents, voice creation, API keys, or asks for safety hardening in Ziyada Systems or any local workspace project.
---

# VAPI Local Secrets Guard

Use this skill when:
- User wants to add VAPI credentials for voice or assistant creation.
- User asks where to store VAPI keys safely.
- A project needs voice provisioning without exposing secrets to git.

## Security Standard

1. Keep real secrets in `.env.local` only.
2. Keep `.env` for safe defaults/placeholders only.
3. Never print full API keys in logs, docs, commit messages, or screenshots.
4. Ensure `.gitignore` blocks `.env`, `.env.*`, `.env*.local`, and credential files.
5. If any key was exposed, rotate it immediately and replace local values.

## Required VAPI Placeholders

Add these keys to local env files as placeholders if missing:

```dotenv
VAPI_API_KEY=
VAPI_PRIVATE_KEY=
VAPI_PUBLIC_KEY=
VAPI_ASSISTANT_ID=
VAPI_DEFAULT_VOICE_ID=
VAPI_PHONE_NUMBER_ID=
VAPI_BASE_URL=https://api.vapi.ai
WAPI_API_KEY=
WAPI_ASSISTANT_ID=
VITE_VOICE_PROVIDER=vapi
VITE_VAPI_PUBLIC_KEY=
VITE_VAPI_ASSISTANT_ID=
```

Notes:
- `VAPI_API_KEY`: primary server-side auth key.
- `VAPI_PRIVATE_KEY`: keep strictly private.
- `VAPI_PUBLIC_KEY`: allowed in client use only if your architecture requires it.
- `VAPI_ASSISTANT_ID` and `VAPI_DEFAULT_VOICE_ID`: IDs used for voice orchestration.
- `WAPI_*` aliases are naming-compatibility variables for projects/scripts that refer to WAPI instead of VAPI.

## Agent Execution Checklist

1. Add placeholders to `.env.local` in the active project (and workspace root if user uses root scripts).
2. Verify there are no malformed env lines (`KEY=value` format only).
3. Confirm env files are not tracked:
   - `git ls-files -- .env .env.local`
4. Confirm staged safety before commit:
   - `git diff --cached | grep -E "(VAPI_|OPENAI_|SUPABASE_|HUBSPOT_|N8N_API_KEY|GOCSPX|sk-|pat-)"`
5. If any secret is detected, stop and redact before commit.

## Ziyada Systems Convention

For Ziyada Systems projects, keep the same policy:
- Workspace root `.env.local` can serve shared local scripts.
- App-level `.env.local` holds app runtime secrets.
- Never move real keys into tracked markdown, JSON, TS, JS, or HTML files.

## Output Requirement for Agents

Return:
- Which files were updated.
- Which VAPI placeholders were added.
- Whether env files are untracked.
- A brief confirmation that secret handling follows local-only policy.
