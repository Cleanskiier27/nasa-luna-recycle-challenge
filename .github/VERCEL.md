# Vercel deployment

This repo includes optional Vercel deployment for the `dashboard` and `challengerepo/real-time-overlay` projects.

Steps to enable deployment

1. Create a Vercel account and set up projects for each package (or a single monorepo project with routes).
2. In the repo **Settings → Secrets → Actions**, add:
   - `VERCEL_TOKEN` — a Vercel token (from Vercel account settings)
   - Optionally: `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` for each project (if you want to target specific projects)
3. The workflow `.github/workflows/deploy-vercel.yml` will run on `push` to `main` and can be triggered manually from the Actions UI. Use the `environment` input to deploy to `preview` (default) or `production` (`production` sets `--prod`).

Notes

- The workflow uses `amondnet/vercel-action` which requires `VERCEL_TOKEN` to be set.
- You can also set up Vercel with Git integration (connect your repository in the Vercel dashboard) and skip CI deploys.
