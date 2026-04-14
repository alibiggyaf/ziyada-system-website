# Vercel Deployment & Security/Funnel Best Practices

## 1. Add and Commit All Changes
- [ ] Add all code changes, including:
  - Vite build/output fixes
  - Any style or content updates
  - Security patches
  - Funnel optimizations (chat widget, forms, CTAs, etc.)
- [ ] Use clear commit messages (e.g., `fix: update Vite output and styles`)

## 2. Security & Funnel Best Practices
- [ ] **Never commit secrets or sensitive data**—always use Vercel environment variables for API keys and credentials.
- [ ] Keep all dependencies up to date (run `npm update` or `pnpm update`).
- [ ] Use HTTPS everywhere (Vercel enforces this by default).
- [ ] Test your funnel after deployment:
  - Chat widget loads and responds
  - All forms submit and validate
  - CTAs and links work as expected
- [ ] Abort any risky rebase or merge if you’re unsure—better to be safe.

## 3. Commit, Push, and Redeploy
- [ ] Commit and push all changes to the `main` branch.
- [ ] Let Vercel automatically redeploy the latest code.

## 4. Post-Deployment Testing
- [ ] Test your live site on both the `.vercel.app` preview and your main domain.
- [ ] Check for:
  - Security (no secrets exposed, HTTPS, no console errors)
  - Funnel functionality (chat, forms, CTAs, analytics)
- [ ] If anything is broken, fix locally and repeat the process.

---

**Tip:** Always use environment variables for sensitive data, and test your funnel after every deployment to ensure conversions and security are never compromised.

---

*Keep this checklist in your repo for every major deployment or update!*
