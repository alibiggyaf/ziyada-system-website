---
name: vercel-vite-env-guard
description: Fix and prevent Vite/Vercel environment variable issues (missing VITE_ prefix), enforce secure secret handling, and validate admin data connectivity after deploy.
---

# Vercel + Vite Env Guard

Use this skill when:
- Frontend deploy is green but admin panels show empty data.
- Browser code depends on `import.meta.env.VITE_*` and data/webhooks fail.
- Vercel env names are inconsistent (`SUPABASE_URL` vs `VITE_SUPABASE_URL`).
- User asks to secure `.env` and avoid secret exposure.

## Core Rules

1. Never hardcode secrets in source code or docs.
2. Browser-exposed vars must use `VITE_` prefix.
3. Private secrets (service-role/API tokens) must stay server-side only.
4. Keep `.env` local-only through `.gitignore` and pre-push checks.

## Standard Fix Flow

1. Confirm client expectations:
- Check files like `src/lib/supabase.js` and `src/api/siteApi.js` for `import.meta.env.VITE_*` usage.

2. Normalize Vercel variables:
- Required browser vars (example):
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_N8N_HOST`
  - `VITE_N8N_NEWSLETTER_WRITER_WEBHOOK`
- Use `vercel env add` or `vercel env rm` + `vercel env add` to enforce final names.

3. Deploy explicitly:
- Run `vercel deploy --prod --yes` after env changes.

4. Validate post-deploy:
- Confirm deployment status is Ready.
- Validate admin endpoints/entities load (Services, FAQs, Case Studies).
- Verify critical CTAs execute expected webhook/API calls.

## Local `.env` Security Checklist

- Ensure `.gitignore` contains: `.env`, `.env.*`, `.env*.local`, `*.local`, and token/credentials patterns.
- Keep examples only in `.env.example` with placeholders.
- Before push, run secret scan:

```bash
grep -r "sk-|eyJhbGci|pat-eu|GOCSPX|fc-|phx_" src/ projects/
```

- If matches appear: redact, rotate key if leaked, then commit.

## Output Requirement for Agent

Return:
- Which env vars were created/updated/removed.
- Deployment URL and readiness status.
- Validation results for admin data loading.
- Security confirmation that no secrets were added to source.
