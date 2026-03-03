# Pushing built images from CI to registries

This project optionally supports pushing Docker images built by CI to container registries.

Supported registries and required secrets

- GitHub Container Registry (GHCR)
  - You can use the built-in `GITHUB_TOKEN` for repository-scoped pushes if your repo is configured to allow it. Our workflow uses `username: ${{ github.actor }}` and `password: ${{ secrets.GITHUB_TOKEN }}`.
  - If you prefer, create a personal access token (PAT) with `write:packages` scope and store it as `GHCR_TOKEN` and update the workflow to use it.

- Docker Hub (optional)
  - Create a Docker Hub access token and add the following repository secrets:
    - `DOCKERHUB_USERNAME` — your Docker Hub username
    - `DOCKERHUB_TOKEN` — your Docker Hub token/password

How to enable pushing

1. In the repository, go to Settings → Secrets and variables → Actions → New repository secret.
2. Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` if you want Docker Hub support.
3. Set the environment variable `PUSH_IMAGES` to `true` for the workflow run (you can set it in repository secrets or pass it as an input when dispatching the workflow).

Manual run via Actions UI

- You can trigger the workflow manually via **Actions → Build Vite Docker images → Run workflow** and set the **push_images** input to `true` in the UI to push images for that run. This is an alternative to setting repository-level environment variables for one-off runs.

Example CLI run (gh):

- You can also trigger a manual run from the command line using the GitHub CLI:

  gh workflow run "Build Vite Docker images" --repo <owner>/<repo> --field push_images=true

PR comment with built image tags

- When a PR triggers the workflow, the workflow will post a comment to the PR listing the built image tags (e.g., `ghcr.io/<owner>/dashboard:<sha>`). This helps reviewers pull or test the images built for the PR without digging through workflow logs.

Status check (Check Run)

- The workflow also creates a Check Run named **Docker images** that summarizes the build and includes the image tags. This appears in the Checks area and gives an at-a-glance verification that images were built and smoke-tested.


Notes

- By default the workflow builds images and runs smoke tests; it does not push images unless `PUSH_IMAGES` is set.
- Pushing using `GITHUB_TOKEN` may require repository settings to allow package write; use a PAT if you get permissions errors.
- When pushing to Docker Hub, ensure the repository name matches your Docker Hub account (the workflow tags images as `docker.io/<DOCKERHUB_USERNAME>/...`).