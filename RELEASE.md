# Release & Deployment Process for Ziyada System Website

## Versioning
- Update the `version` field in `package.json` for each release.
- Document changes in `CHANGELOG.md`.

## Deployment (Vercel)
- The website is deployed via Vercel.
- Any push to the main branch triggers an automatic deployment on Vercel.
- To release a new version:
  1. Update `package.json` version.
  2. Update `CHANGELOG.md`.
  3. Commit and push changes to the main branch.
  4. Vercel will build and deploy the latest version automatically.
- To verify deployment:
  - Visit the Vercel dashboard or the live site URL.
  - Optionally, display the version in the website footer or about page for confirmation.

## Rollback
- Use the Vercel dashboard to roll back to a previous deployment if needed.

---

For advanced workflows, consider integrating GitHub Actions or Vercel's preview deployments for staging/testing.