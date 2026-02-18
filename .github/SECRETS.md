# GitHub Actions Secrets Configuration Guide

This document lists all the secrets and variables you need to configure in your GitHub repository for the AKS deployment workflow.

## Required GitHub Secrets

Navigate to your repository → Settings → Secrets and variables → Actions → New repository secret

### Azure Authentication (OIDC - Recommended)

1. **AZURE_CLIENT_ID**
   - The client ID of your Azure AD application/service principal
   - Used for OpenID Connect authentication

2. **AZURE_TENANT_ID**
   - Your Azure Active Directory tenant ID
   - Found in Azure Portal → Azure Active Directory → Overview

3. **AZURE_SUBSCRIPTION_ID**
   - Your Azure subscription ID
   - Found in Azure Portal → Subscriptions

## Setting Up Azure OIDC Authentication

### Step 1: Create a Service Principal

```bash
# Login to Azure
az login

# Set variables
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="your-resource-group"
APP_NAME="echo-me-pro-github-actions"

# Create service principal
az ad sp create-for-rbac \
  --name $APP_NAME \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

### Step 2: Configure Federated Credentials

```bash
# Get the application ID
APP_ID=$(az ad app list --display-name $APP_NAME --query [0].appId -o tsv)

# Create federated credential for main branch
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "echo-me-pro-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_GITHUB_ORG/YOUR_REPO_NAME:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Create federated credential for develop branch
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "echo-me-pro-develop",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:YOUR_GITHUB_ORG/YOUR_REPO_NAME:ref:refs/heads/develop",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

Replace `YOUR_GITHUB_ORG/YOUR_REPO_NAME` with your actual GitHub organization and repository name.

### Step 3: Grant AKS Permissions

```bash
# Get AKS resource ID
AKS_ID=$(az aks show --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME --query id -o tsv)

# Assign AKS cluster admin role
az role assignment create \
  --assignee $APP_ID \
  --role "Azure Kubernetes Service Cluster User Role" \
  --scope $AKS_ID

# Assign ACR push/pull permissions
ACR_ID=$(az acr show --name $ACR_NAME --query id -o tsv)
az role assignment create \
  --assignee $APP_ID \
  --role "AcrPush" \
  --scope $ACR_ID
```

## GitHub Environments

Create two environments in your repository:
- Settings → Environments → New environment

### 1. staging
- Deployment branch: `develop`
- (Optional) Add protection rules and reviewers

### 2. production
- Deployment branch: `main`
- ✅ Enable "Required reviewers" (recommended)
- Add approvers who must review production deployments

## Repository Variables

Navigate to Settings → Secrets and variables → Actions → Variables tab → New repository variable

These are defined in the workflow file but can be overridden:

1. **AZURE_CONTAINER_REGISTRY**
   - Your ACR name (without .azurecr.io)
   - Example: `myacrname`

2. **RESOURCE_GROUP**
   - Azure resource group containing your AKS cluster

3. **CLUSTER_NAME**
   - Name of your AKS cluster

## Kubernetes Secrets

The application secrets should be stored in Azure Key Vault and synced to AKS, or created manually:

```bash
# Create secrets in Kubernetes (one-time setup)
kubectl create secret generic echo-me-pro-secrets \
  --from-literal=OPENAI_API_KEY='your-key' \
  --from-literal=PUSHOVER_TOKEN='your-token' \
  --from-literal=PUSHOVER_USER='your-user' \
  --from-literal=SENDGRID_API_KEY='your-key' \
  --from-literal=SENDER_EMAIL='your-email' \
  --from-literal=SENDER_NAME='Your Name' \
  -n echo-me-pro
```

## Verification

Test your setup:

```bash
# Verify service principal permissions
az role assignment list --assignee $APP_ID --output table

# Verify federated credentials
az ad app federated-credential list --id $APP_ID
```

## Security Best Practices

1. ✅ Use OIDC instead of long-lived secrets
2. ✅ Follow principle of least privilege
3. ✅ Use separate service principals for staging and production
4. ✅ Enable deployment protection rules
5. ✅ Rotate credentials regularly
6. ✅ Use Azure Key Vault for sensitive data
7. ✅ Enable audit logging
