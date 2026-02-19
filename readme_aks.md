# AKS + ArgoCD + GitOps Setup Guide (WSL / Linux)

This guide documents the complete setup of:

- Azure Kubernetes Service (AKS)
- ArgoCD (GitOps)
- Docker Registry (public)
- Azure Key Vault integration
- WSL/Linux environment configuration
- Troubleshooting issues encountered

We assume:

- You only have an Azure subscription
- You are working from Linux (WSL or native Linux)
- You are using a public GitHub repo and public Docker registry

---

# 1. Environment Setup (WSL / Linux Only)

⚠️ IMPORTANT: Do NOT mix Windows Azure CLI with Linux kubectl.

## 1.1 Install Azure CLI (Linux)

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Verify:

```bash
which az
```

Expected:

```
/usr/bin/az
```

---

## 1.2 Install kubectl

```bash
az aks install-cli
```

Verify:

```bash
which kubectl
```

Expected:

```
/usr/bin/kubectl
```

---

## 1.3 Login to Azure

```bash
az login
```

Verify current subscription:

```bash
az account show -o table
```

Change subscription if needed:

```bash
az account set --subscription <SUBSCRIPTION_NAME>
```

---

# 2. Connect kubectl to AKS

## 2.1 Create kube directory

```bash
mkdir -p ~/.kube
```

## 2.2 Get AKS credentials

```bash
az aks get-credentials \
  --resource-group <RESOURCE_GROUP> \
  --name <CLUSTER_NAME> \
  --overwrite-existing
```

Verify:

```bash
kubectl config get-contexts
kubectl get nodes
```

If nodes appear → connection is correct.

---

# 3. Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f \
https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verify:

```bash
kubectl get pods -n argocd
```

---

# 4. GitOps Application Structure

Repository structure:

```
k8s/
 ├── namespace.yaml
 ├── deployment.yaml
 ├── service.yaml
 ├── configmap.yaml
 ├── secret-provider-class.yaml
 └── application.yaml
```

---

# 5. Deploy Using ArgoCD

Only apply the Application resource manually:

```bash
kubectl apply -f k8s/application.yaml
```

After that:

```bash
git add .
git commit -m "update"
git push
```

ArgoCD will automatically sync.

Verify:

```bash
kubectl get applications -n argocd
kubectl get all -n echo-me-ai
```

---

# 6. Service Exposure

If using:

```yaml
type: LoadBalancer
```

Azure will:

- Create Public IP
- Create Azure Load Balancer
- Route traffic to AKS nodes

Check external IP:

```bash
kubectl get svc -n echo-me-ai
```

Note:
- API server IP is separate from your app public IP.

---

# 7. Azure Key Vault Integration

## 7.1 Create Key Vault

```bash
az keyvault create \
  --name echo-me-ai-kv \
  --resource-group <RESOURCE_GROUP> \
  --location canadacentral
```

## 7.2 RBAC Mode Note

If you see:

```
ForbiddenByRbac
```

It means the vault uses RBAC authorization.

Confirm:

```bash
az keyvault show --name echo-me-ai-kv --query properties.enableRbacAuthorization
```

If true → use role assignment (NOT set-policy).

## 7.3 Assign Secret Permissions

Get your object ID:

```bash
az ad signed-in-user show --query id -o tsv
```

Assign role:

```bash
az role assignment create \
  --assignee <OBJECT_ID> \
  --role "Key Vault Secrets Officer" \
  --scope $(az keyvault show --name echo-me-ai-kv --query id -o tsv)
```

Wait 60 seconds for propagation.

---

## 7.4 Add Secrets

```bash
az keyvault secret set --vault-name echo-me-ai-kv --name OPENAI_API_KEY --value "xxx"
```

---

# 8. Enable Key Vault CSI Driver

```bash
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name <CLUSTER_NAME> \
  --resource-group <RESOURCE_GROUP>
```

---

## 8.1 Grant AKS Access to Vault

Get AKS identity:

```bash
az aks show \
  --name <CLUSTER_NAME> \
  --resource-group <RESOURCE_GROUP> \
  --query identity.principalId -o tsv
```

Assign read permission:

```bash
az role assignment create \
  --assignee <AKS_PRINCIPAL_ID> \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show --name echo-me-ai-kv --query id -o tsv)
```

---

# 9. SecretProviderClass Sync to Kubernetes Secret

The SecretProviderClass must include:

```yaml
secretObjects:
  - secretName: echo-me-ai-secrets
```

Important:

The Kubernetes Secret name is independent from the Key Vault name.

Vault → CSI → K8s Secret → Pod

---

# 10. Deployment Configuration

Inside container:

```yaml
envFrom:
  - secretRef:
      name: echo-me-ai-secrets
```

Volume required to trigger sync:

```yaml
volumes:
  - name: secrets-store-inline
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "echo-me-ai-kv-provider"
```

---

# 11. Troubleshooting We Encountered

## 11.1 kubectl connecting to localhost

Cause:
- kubeconfig empty

Fix:

```bash
az aks get-credentials --overwrite-existing
```

---

## 11.2 az writing to Windows kubeconfig

Cause:
- Using Windows Azure CLI inside WSL

Fix:
- Install Azure CLI inside Linux
- Ensure `which az` returns `/usr/bin/az`

---

## 11.3 ForbiddenByRbac when creating secrets

Cause:
- Vault in RBAC mode

Fix:
- Assign role `Key Vault Secrets Officer`

---

## 11.4 Secrets not syncing

Check:

```bash
kubectl get secret -n echo-me-ai
kubectl describe pod <pod> -n echo-me-ai
```

Ensure:
- CSI addon enabled
- AKS identity has Key Vault Secrets User role
- Volume mount exists

---

# 12. Recommended Best Practices

- Never mix Windows and WSL CLI tools
- Do not store secrets in Git
- Use immutable image tags
- Use dedicated namespace per application
- Avoid deploying to `default` namespace
- Prefer Ingress over multiple LoadBalancers in production

---

# 13. Final Architecture

Git → ArgoCD → AKS

Azure Key Vault → CSI Driver → Kubernetes Secret → Pod env

Azure LoadBalancer → Public IP → Service → Pod

---

# End of Guide

You now have a complete AKS + GitOps + KeyVault secure setup fully running from Linux.

