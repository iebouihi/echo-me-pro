# Docker Hub Configuration Guide

This guide shows how to use Docker Hub instead of Azure Container Registry (ACR) for AKS deployments.

## Required GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

### 1. DOCKERHUB_USERNAME
- Your Docker Hub username
- Example: `johndoe`

### 2. DOCKERHUB_TOKEN
- Docker Hub access token (NOT your password)
- How to create:
  1. Login to Docker Hub (https://hub.docker.com)
  2. Go to Account Settings → Security
  3. Click "New Access Token"
  4. Give it a name (e.g., "github-actions")
  5. Copy the token (you won't see it again!)
  6. Add to GitHub secrets

### 3. Azure Secrets (still needed for AKS)
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

See [SECRETS.md](SECRETS.md) for Azure setup details.

## Kubernetes Deployment Changes

### Update deployment.yaml

Add `imagePullSecrets` to your deployment:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: dockerhub-secret  # Add this line
      containers:
      - name: echo-me-pro
        image: <YOUR_DOCKERHUB_USERNAME>/echo-me-pro:latest
```

### Update Helm values.yaml

```yaml
image:
  registry: docker.io
  repository: <YOUR_DOCKERHUB_USERNAME>/echo-me-pro
  pullPolicy: Always
  tag: "latest"

imagePullSecrets:
  - name: dockerhub-secret
```

## Manual Deployment Steps

### 1. Build and Push to Docker Hub

```bash
# Login to Docker Hub
docker login -u <your-username>

# Build the image
docker build -t <your-username>/echo-me-pro:latest .

# Push to Docker Hub
docker push <your-username>/echo-me-pro:latest
```

### 2. Create Image Pull Secret in Kubernetes

```bash
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=<your-username> \
  --docker-password=<your-token> \
  --namespace=echo-me-pro
```

### 3. Update Kubernetes Manifests

Edit `k8s/deployment.yaml` to use Docker Hub image:

```yaml
containers:
- name: echo-me-pro
  image: <your-username>/echo-me-pro:latest
```

And add imagePullSecrets:

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
      - name: dockerhub-secret
```

## Using the Docker Hub Workflow

1. Rename or copy `.github/workflows/deploy-aks-dockerhub.yml` to `.github/workflows/deploy-aks.yml`

2. Update environment variables in the workflow:
   ```yaml
   env:
     DOCKER_USERNAME: your-dockerhub-username
     RESOURCE_GROUP: <YOUR_RESOURCE_GROUP>
     CLUSTER_NAME: <YOUR_AKS_CLUSTER_NAME>
   ```

3. Add GitHub secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`

4. Push to main branch to trigger deployment

## Rate Limiting Considerations

Docker Hub has pull rate limits:
- **Anonymous**: 100 pulls per 6 hours
- **Free account**: 200 pulls per 6 hours per user
- **Pro account**: No limits

For production workloads with multiple pods and frequent deployments, consider:
- Using a Docker Hub Pro account
- Using ACR instead
- Using GitHub Container Registry (ghcr.io) - also free with unlimited private images

## Alternative: GitHub Container Registry

GitHub Container Registry is free and has no rate limits. To use it:

```yaml
# Login
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

# Build and push
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: ghcr.io/${{ github.repository_owner }}/echo-me-pro:latest
```

No additional secrets needed - `GITHUB_TOKEN` is automatically available!

## Comparison Table

| Feature | Docker Hub (Free) | ACR (Basic) | GHCR |
|---------|------------------|-------------|------|
| Private Images | Yes | Yes | Yes |
| Rate Limiting | 200/6hrs | None | None |
| Cost | Free | ~$5/month | Free |
| Azure Integration | Manual | Native | Manual |
| Speed in Azure | Slower | Fastest | Medium |
| Setup Complexity | Low | Medium | Lowest |

## Recommendation

- **Development/Testing**: Docker Hub or GHCR
- **Production on Azure**: ACR (better performance & integration)
- **Production (other clouds)**: GHCR or Docker Hub Pro

## Troubleshooting

### ImagePullBackOff Error

If pods fail with `ImagePullBackOff`:

```bash
# Check if secret exists
kubectl get secret dockerhub-secret -n echo-me-pro

# Describe the pod to see the error
kubectl describe pod <pod-name> -n echo-me-pro

# Recreate the secret
kubectl delete secret dockerhub-secret -n echo-me-pro
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=<your-username> \
  --docker-password=<your-token> \
  --namespace=echo-me-pro
```

### Rate Limit Exceeded

If you hit rate limits:
1. Login to Docker Hub in your workflow (already done)
2. Upgrade to Docker Hub Pro
3. Switch to ACR or GHCR
4. Use image caching to reduce pulls
