# Web Data Lab Version

> This file is the single source of truth for the currently declared project version.
> Update it in every release. Do not publish a new release without updating this file.

## Current version

- **Version:** 0.1.0
- **Release stage:** Initial public version
- **Release date:** 2026-11-06
- **Frontend deployment:** GitHub Pages
- **Frontend URL:** https://ouyangxinwei.github.io/web-data-lab/
- **Deployment status:** Initial deployment reported successful
- **Source branch:** `main`
- **Application source commit:** `4a6bf028deb192acd5ebd0849fcc9ae6588bec4d`
- **Backend deployment:** Not deployed; the FastAPI backend currently requires a separate hosting service.

## Release update rules

For every subsequent release:

1. Update the version number in this file.
2. Update the release date and summarize the changes.
3. Record the source commit SHA after the release code is committed.
4. Record the frontend deployment URL and verify the GitHub Actions build and deploy jobs succeeded.
5. State the backend deployment status separately; GitHub Pages only hosts the frontend.
6. Keep this file consistent with `frontend/package.json` and the release notes.

## Release history

| Version | Date | Description | Deployment |
|---|---|---|---|
| 0.1.0 | 2026-11-06 | Initial public version: frontend shell, FastAPI backend foundation, health-check endpoint, and GitHub Pages workflow | Frontend deployment reported successful; backend not deployed |
