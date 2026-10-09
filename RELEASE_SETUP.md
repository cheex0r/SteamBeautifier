# GitHub Releases Setup Guide

This guide explains how to set up automated releases for SteamBeautifier.

## Prerequisites

1. **GitHub Personal Access Token (PAT)**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Create a token with `repos` scope (full control of private repositories)
   - Save the token somewhere secure

2. **Add Token as Repository Secret**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `GITHUB_TOKEN`
   - Value: (your PAT)

## Manual Release Workflow

1. **Update the version number** in `src/version.py`:
   ```python
   __version__ = "1.2.3"
   ```

2. **Push your changes** to the `main` branch

3. **Trigger the Release workflow**:
   - Go to GitHub → Actions → Release → Run workflow
   - Enter the version number (e.g., `1.2.3`)
   - Click "Run workflow"

4. **GitHub will**:
   - Build the Linux executables
   - Create a GitHub Release
   - Upload the executables

## Automated Version Bumping (Optional)

For fully automated versioning based on commit messages, you can use `semantic-release`:

1. Install semantic-release:
   ```bash
   npm install -g semantic-release @semantic-release/github
   ```

2. Use commit messages that trigger version bumps:
   - `release: x.y.z` - Creates release with version x.y.z
   - `feat: ` - Increments minor version
   - `fix: ` - Increments patch version

## Current Setup

The current workflow uses `workflow_dispatch` which allows manual triggering with a version parameter. This gives you full control over when releases happen and what version number to use.

## Release Assets

Releases include:
- `steam_beautifier` - Main executable (35MB)
- `steam_beautifier_config` - Config utility (35MB)

## Notes

- Linux executables are built on Ubuntu x86_64 (compatible with Steam Deck)
- Executables include all dependencies (Python runtime, libraries)
- Release tags follow semver format: `v1.2.3`
