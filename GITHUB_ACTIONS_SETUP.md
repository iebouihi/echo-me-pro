# GitHub Actions Docker Build & Push Workflow Setup Guide

## Overview
This workflow automatically builds, scans, and pushes your Docker image to Docker Hub when a PR is merged with changes in the `releases/{version}` directory.

## Prerequisites

### 1. GitHub Secrets Configuration
Add the following secrets to your GitHub repository:
- **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Value | Description |
|---|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | Username for docker.io |
| `DOCKERHUB_TOKEN` | Docker Hub Personal Access Token | [Generate here](https://hub.docker.com/settings/security) |
| `SNYK_TOKEN` | Snyk API token (optional) | [Generate here](https://app.snyk.io/account/settings/api) for Snyk scanning |

### 2. Docker Hub Personal Access Token
1. Go to [Docker Hub Settings](https://hub.docker.com/settings/security)
2. Click **New Access Token**
3. Set token name: `github-action-echo-me-pro`
4. Copy the token and add it to GitHub Secrets as `DOCKERHUB_TOKEN`

### 3. Branch Naming Convention
Create release branches using the following pattern:
- `release/1.0.0` - Standard release (preferred)
- `releases/1.2.3` - Alternative naming
- `release/1.0.0-beta` - Pre-release versions supported

The workflow extracts the version from the branch name automatically.

## Workflow Triggers

### Automatic Trigger
The workflow runs automatically when:
- A **pull request** is created from a release branch to `main` or `master`
- Release branch must match: `release/X.Y.Z` or `releases/X.Y.Z`

### Manual Trigger
You can manually trigger the workflow from the Actions tab with optional explicit version:
- Go to **Actions** → **Build and Push Docker Image to Docker Hub** → **Run workflow**
- Optionally provide a version in the format `1.0.0` or `1.0.0-beta`

## Workflow Jobs

### Job 1: `extract-version`
**Purpose**: Extract and validate the release version from the `releases/{version}` directory

**Steps**:
1. Checkout code with full historybranch name or manual input

**Steps**:
1. Checkout code with full history
2. Extract version from branch name (e.g., `release/1.0.0` → `1.0.0`)
3. Or use manual input from `workflow_dispatch` if provided
4. Validate semantic versioning format (`v1.0.0`, `1.0.0`, or `1.0.0-beta`)
5 `release-version`: The extracted version (e.g., `1.2.0`)
- `image-tag`: Full image tag (e.g., `iebouihi/echo-me-pro:1.2.0`)

---

### Job 2: `build-and-scan`
**Purpose**: Build the Docker image and run comprehensive security checks

**Security Checks Included**:

1. **Trivy Vulnerability Scan**
   - Scans image for HIGH and CRITICAL vulnerabilities
   - Outputs SARIF report to GitHub Security tab
   - Fails workflow if critical vulnerabilities found
   - [Trivy Documentation](https://github.com/aquasecurity/trivy)

2. **Snyk Container Scan** (requires SNYK_TOKEN)
   - Additional vulnerability scanning
   - Checks for known CVEs
   - High severity threshold
   - [Snyk Documentation](https://snyk.io/)

3. **Hadolint Dockerfile Linting**
   - Validates Dockerfile best practices
   - Checks for security issues in Dockerfile
   - Improves layer efficiency
   - [Hadolint Rules](https://github.com/hadolint/hadolint/wiki/Rules)

**Output**:
- `image-digest`: SHA256 digest of built image (for provenance)

---

### Job 3: `push-to-registry`
**Purpose**: Push the validated image to Docker Hub with security features

**Steps**:

1. **Docker Buildx Setup**
   - Enables LayerCache for faster builds
   - Supports multi-platform builds

2. **Docker Hub Login**
   - Uses encrypted GitHub Secrets
   - Enables Content Trust for signature verification

3. **Build & Push**
   - Builds from Dockerfile
   - Pushes tags: `iebouihi/echo-me-pro:1.2.0` and `latest`
   - Generates SBOM (Software Bill of Materials)
   - Includes provenance metadata (SLSA compliance)

4. **Cosign Image Signing**
   - Signs pushed image for authenticity
   - Uses OIDC token for keyless signing
   - No manual key management needed
   - [Cosign Documentation](https://github.com/sigstore/cosign)

5. **Signature Verification**
   - Verifies image signature succeeded
   - Ensures image integrity

---

### Job 4: `post-push-validation`
**Purpose**: Validate pushed image and provide deployment summary

**Steps**:

1. **Image Pull Verification**
   - Pulls image from Docker Hub
   - Inspects image metadata
   - Confirms successful push

2. **Deployment Summary**
   - Displays Docker commands for running container
   - Shows image tag and version
   - Provides next steps for users

## Security Features

### 1. **Vulnerability Scanning**
- Trivy: Fast, comprehensive container scanning
- Snyk: Industry-standard with CVE database
- Hadolint: Dockerfile security and best practices

### 2. **Image Signing & Verification**
- Cosign with OIDC token (keyless signing)
- No private key management in GitHub
- Signature verification before deployment

### 3. **Software Supply Chain Security (SLSA)**
- Provenance metadata included in image
- SBOM (Software Bill of Materials) generated
- Enables supply chain transparency

### 4. **Non-Root User**
- Dockerfile runs as `appuser` (unprivileged)
- Reduces attack surface
- Follows container security best practices

### 5. **Minimal Base Image**
- `python:3.12-slim` base image
- Reduces attack surface vs full Python image
- Only necessary dependencies included

### 6. **Layer Caching**
- GitHub Actions cache for faster builds
- Reduces bandwidth and build time
- Improves developer experience

## Monitoring & Debugging

### View Workflow Runs
1. Go to **Actions** tab in GitHub
2. Select **Build and Push Docker Image to Docker Hub** workflow
3. Click on specific run to see details

### Check Security Scan Results
1. Go to **Security** tab → **Code scanning alerts**
2. Review Trivy vulnerability reports
3. Click on alerts to see details and remediation

### Troubleshooting

| Issue | Solution |
|---|---|
| **Workflow fails at extract-version** | Ensure `releases/version` directory exists in PR changes |
| **Invalid version format error** | Version must be `v1.0.0` or `1.0.0` format |
| **Docker Hub login fails** | Check `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets |
| **Trivy scan finds vulnerabilities** | Update base image or dependencies in `requirements.txt` |
| **Snyk scan fails** | Ensure `SNYK_TOKEN` is set (optional step) |
| **Cosign signing fails** | Check GitHub OIDC trust configuration |

## Example Usage
Option 1: Create Release via Pull Request (Recommended)
```bash
# Create release branch from main/master
git checkout -b release/1.2.0

# Make any release-specific changes (optional)
# e.g., update version numbers, changelog, etc.
git commit -m "Release 1.2.0" || true

# Push branch
git push origin release/1.2.0

# Create Pull Request on GitHub
# GitHub Actions workflow will:
# 1. Automatically trigger on PR creation
# 2. Build and scan image
# 3. Push to Docker Hub as iebouihi/echo-me-pro:1.2.0

# Merge PR to main when ready
```

### Option 2: Manual Trigger via GitHub Actions
```bash
# No branch needed - use GitHub Actions UI:
```
1. Go to **Actions** tab
2. Select **Build and Push Docker Image to Docker Hub**
3. Click **Run workflow**
4. Enter version: `1.2.0` (optional)
5. Click **Run workflow**

### Option 3: Command Line Push (Advanced)
```bash
# Create release branch
git checkout -b release/1.2.0

# Push and create PR
git push origin release/1.2.0

# Create PR using GitHub CLI
gh pr create --base main --head release/1.2.0 --title "Release 1.2.0"

# Monitor workflow
gh run list --workflow=docker-build-push.yml
```

### Monitor Workflow
- Go to GitHub **Actions** tab
- Select **Build and Push Docker Image to Docker Hub** workflow
- Watch workflow execution in real-time
- Check security scan results in **Security** tab

### Pull & Run Pushed Image
```bash
# Pull the pushed image
docker pull iebouihi/echo-me-pro:1.2.0

# Run the container
docker run -p 7860:7860 iebouihi/echo-me-pro:1.2.0

# Verify it's running
curl http://localhost:786
docker run -p 7860:7860 iebouihi/echo-me-pro:1.2.0
```

## Advanced Configuration

### Optional: Enable Docker Scout (Docker's vulnerability scanner)
Add to `build-and-scan` job:
```yaml
- name: Run Docker Scout scan
  uses: docker/scout-action@v1
  with:
    command: cves
    image: ${{ needs.extract-version.outputs.image-tag }}
    only-severities: critical,high
    exit-code: true
```

### Optional: Create GitHub Releases
Uncomment the "Create GitHub Release" step in `post-push-validation` job to automatically create release notes.

### Optional: Publish Layer Cache
Add to `push-to-registry` job for persistent build cache:
```yaml
cache-to: type=registry,ref=${{ needs.extract-version.outputs.image-tag }}-cache
```

## Clean Up Old Images

To manage Docker Hub storage, periodically delete old image tags:
```bash
# Delete specific tag
docker image rm iebouihi/echo-me-pro:1.0.0

# Or via Docker Hub UI: repository → tags → delete
```

## References

- [GitHub Actions Docker Build & Push](https://github.com/docker/build-push-action)
- [Trivy Vulnerability Scanner](https://github.com/aquasecurity/trivy)
- [Snyk Container Scanning](https://snyk.io/product/container-security/)
- [Cosign - Container Signing](https://github.com/sigstore/cosign)
- [Hadolint - Dockerfile Linter](https://github.com/hadolint/hadolint)
- [Docker Hub Personal Access Token](https://docs.docker.com/security/for-developers/access-tokens/)
- [SLSA Framework](https://slsa.dev/)
- [Software Bill of Materials (SBOM)](https://cyclonedx.org/)

## Support

For questions or issues:
1. Check GitHub Actions logs for detailed error messages
2. Review security scan results in GitHub Security tab
3. Consult tool documentation (Trivy, Snyk, Cosign)
4. Enable debug logging: add `ACTIONS_STEP_DEBUG=true` as repository secret
