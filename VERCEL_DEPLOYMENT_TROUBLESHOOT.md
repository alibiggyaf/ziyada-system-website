# Vercel Production Deployment Troubleshooting Checklist

## 1. Build Output Directory
- [ ] Go to **Project Settings → Build & Deployment** in Vercel.
- [ ] Ensure **Output Directory** is set to `dist` (for Vite projects).
- [ ] If not, set it to `dist` and click **Save**.

## 2. Build Command
- [ ] Confirm the build command is `vite build` or `npm run build`.
- [ ] If using a custom script, make sure it outputs to `dist`.

## 3. Environment Variables
- [ ] Go to **Settings → Environment Variables** in Vercel.
- [ ] Ensure all required variables (Supabase, n8n, etc.) are present and correct.
- [ ] Update any missing or incorrect variables and redeploy.

## 4. Remove and Re-Add Domains
- [ ] Go to **Domains** in Vercel.
- [ ] Remove `ziyadasystem.com` and `www.ziyadasystem.com`.
- [ ] Re-add both domains and assign them to the current production deployment.
- [ ] Redeploy after re-adding domains.

## 5. Hard Redeploy
- [ ] Make a trivial commit (e.g., add a comment) and push to `main`.
- [ ] This will force a new build and deployment from scratch.

## 6. Test Both .vercel.app and Main Domain
- [ ] After redeploy, test both the `.vercel.app` preview and `ziyadasystem.com`.
- [ ] If `.vercel.app` is broken, the issue is in your code, build, or env vars.
- [ ] If `.vercel.app` works but the main domain doesn’t, it’s a domain/CDN issue.

## 7. If Still Broken
- [ ] Create a new Vercel project from the same repo, set up domains, and redeploy. This resets all Vercel state.

---

**Tip:** After each step, always redeploy and test. If you need to debug further, check the build logs for errors and verify your environment variables.

---

**If you complete this checklist and the site is still not updating, let me know and I’ll guide you through a full Vercel project reset.**
