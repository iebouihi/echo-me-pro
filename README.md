---
title: Imad_Eddine_BOUIHI_AI_Echo
app_file: app.py
sdk: gradio
sdk_version: 6.5.1
---

# Echo Me Pro

An AI-powered personal assistant chat interface that answers questions about your career, background, skills, and experience. The application uses OpenAI's GPT-4 to engage professionally with potential clients and employers, while automatically recording contact information and unknown questions via push notifications.

## Features

- **AI-Powered Chat**: Uses OpenAI GPT-4o-mini to respond in your voice
- **Context-Aware**: Leverages your LinkedIn profile and personal summary for accurate responses
- **Lead Capture**: Automatically records user contact details when they express interest
- **Email with CV**: Sends personalized emails with your CV attached via SendGrid
- **Question Tracking**: Logs questions that couldn't be answered for future improvement
- **Push Notifications**: Sends real-time alerts via Pushover for user interactions
- **Error Handling**: Comprehensive logging and error handling for HTTP requests
- **Web Interface**: Clean Gradio-based chat interface

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- SendGrid API key (for email functionality)
- Pushover account (for notifications)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd echo-me-pro
   ```

2. **Set up environment variables**:
   Create a `.env` file in the project root with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   PUSHOVER_TOKEN=your_pushover_app_token
   PUSHOVER_USER=your_pushover_user_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDER_EMAIL=your@email.com
   SENDER_NAME=Your Name
   ```

3. **Add required personal files**:
   
   **IMPORTANT**: Before running the app, you must create these files in the `me/` directory:
   
   - **`me/summary.txt`**: A text file containing your personal summary, background, and key information
   - **`me/linkedin.pdf`**: Export your LinkedIn profile as PDF and place it here
   - **`me/myCV.pdf`**: Your CV/Resume in PDF format (used when sending emails to prospects)
   
   Create the directory if it doesn't exist:
   ```bash
   mkdir me
   ```
   
   Then add your files:
   - Save your personal summary as `me/summary.txt`
   - Export your LinkedIn profile to PDF and save as `me/linkedin.pdf`
   - Save your CV/Resume as `me/myCV.pdf`

4. **Install dependencies**:
   Using uv (recommended):
   ```bash
   uv pip install -r requirements.txt
   ```

   Or using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Using uv (recommended)
```bash
uv run app.py
```

### Using Python directly
```bash
python app.py
```

The application will start a local web server (typically at `http://localhost:7860`) and open in your default browser.

## Project Structure

```
echo-me-pro/
├── app.py                              # Main application file
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Python project configuration
├── .env                               # Environment variables (not in repo)
├── Dockerfile                         # Multi-stage container build
├── .dockerignore                      # Docker build exclusions
├── README.md                          # This file
├── me/                                # Personal data directory
│   ├── summary.txt                    # Personal summary
│   ├── linkedin.pdf                   # LinkedIn profile PDF
│   └── myCV.pdf                       # Your CV/Resume PDF
├── .github/                           # GitHub Actions workflows
│   ├── workflows/
│   │   └── deploy-aks.yml            # AKS deployment pipeline
│   └── SECRETS.md                     # GitHub secrets setup guide
├── k8s/                               # Kubernetes manifests
│   ├── namespace.yaml                 # Namespace definition
│   ├── configmap.yaml                 # Configuration data
│   ├── secrets.yaml                   # Secret management
│   ├── deployment.yaml                # Application deployment
│   ├── service.yaml                   # Service definition
│   ├── ingress.yaml                   # Ingress configuration
│   ├── hpa.yaml                       # Horizontal Pod Autoscaler
│   └── pdb.yaml                       # Pod Disruption Budget
└── helm/                              # Helm charts
    └── echo-me-pro/
        ├── Chart.yaml                 # Helm chart metadata
        ├── values.yaml                # Default values
        ├── values-staging.yaml        # Staging overrides
        ├── values-production.yaml     # Production overrides
        └── templates/                 # Kubernetes templates
            ├── deployment.yaml
            ├── service.yaml
            ├── ingress.yaml
            ├── configmap.yaml
            ├── secret.yaml
            ├── hpa.yaml
            ├── pdb.yaml
            ├── serviceaccount.yaml
            └── _helpers.tpl
```

## How It Works

1. **Initialization**: Loads personal data (summary and LinkedIn profile)
2. **Chat Interface**: User interacts through Gradio chat interface
3. **AI Processing**: Messages are sent to OpenAI with context and tools
4. **Tool Calling**: AI can invoke tools to:
   - Record user contact details
   - Send personalized emails with CV attachment via SendGrid
   - Log unknown questions
   - Stop disruptive conversations
5. **Notifications**: Push notifications sent for important interactions
6. **Logging**: All operations logged with timestamps and error details

## Deployment

### Local/Development Deployment

The app can be deployed to Gradio Spaces:

```bash
gradio deploy
```

### Production Deployment to Azure Kubernetes Service (AKS)

This project includes comprehensive deployment automation for Azure Kubernetes Service using GitHub Actions, Helm charts, and Kubernetes manifests.

#### Prerequisites for AKS Deployment

- Azure subscription with AKS cluster
- Azure Container Registry (ACR)
- kubectl CLI installed
- Helm 3.x installed
- GitHub repository with Actions enabled

#### Quick Start: Deploy to AKS

1. **Set up Azure Resources**:
   ```bash
   # Create resource group
   az group create --name echo-me-pro-rg --location eastus
   
   # Create Azure Container Registry
   az acr create --resource-group echo-me-pro-rg --name echomepro --sku Standard
   
   # Create AKS cluster
   az aks create \
     --resource-group echo-me-pro-rg \
     --name echo-me-pro-aks \
     --node-count 3 \
     --enable-managed-identity \
     --attach-acr echomepro \
     --generate-ssh-keys
   
   # Get credentials
   az aks get-credentials --resource-group echo-me-pro-rg --name echo-me-pro-aks
   ```

2. **Configure GitHub Secrets**:
   
   Set up Azure authentication using OIDC (recommended) - see [.github/SECRETS.md](.github/SECRETS.md) for detailed instructions.
   
   Required secrets:
   - `AZURE_CLIENT_ID` - Service principal client ID
   - `AZURE_TENANT_ID` - Azure AD tenant ID
   - `AZURE_SUBSCRIPTION_ID` - Azure subscription ID

3. **Create Kubernetes Secrets**:
   ```bash
   kubectl create namespace echo-me-pro
   
   kubectl create secret generic echo-me-pro-secrets \
     --from-literal=OPENAI_API_KEY='your-openai-key' \
     --from-literal=PUSHOVER_TOKEN='your-pushover-token' \
     --from-literal=PUSHOVER_USER='your-pushover-user' \
     --from-literal=SENDGRID_API_KEY='your-sendgrid-key' \
     --from-literal=SENDER_EMAIL='your-email@example.com' \
     --from-literal=SENDER_NAME='Your Name' \
     -n echo-me-pro
   ```

4. **Deploy Using Helm** (Recommended):
   ```bash
   # Install/upgrade with Helm
   helm upgrade --install echo-me-pro ./helm/echo-me-pro \
     --namespace echo-me-pro \
     --create-namespace \
     --values ./helm/echo-me-pro/values-production.yaml \
     --set image.registry=echomepro.azurecr.io \
     --set image.tag=latest \
     --set ingress.hosts[0].host=yourdomain.com \
     --set-string secrets.existingSecret=echo-me-pro-secrets
   ```

5. **Or Deploy Using kubectl**:
   ```bash
   # Apply Kubernetes manifests
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/secrets.yaml
   kubectl apply -f k8s/configmap.yaml
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   kubectl apply -f k8s/hpa.yaml
   kubectl apply -f k8s/pdb.yaml
   ```

6. **Push to GitHub for CI/CD**:
   ```bash
   git add .
   git commit -m "Add AKS deployment configuration"
   git push origin main
   ```
   
   GitHub Actions will automatically:
   - Build and test the application
   - Build and push Docker image to ACR
   - Scan for vulnerabilities with Trivy
   - Deploy to AKS production environment

#### Deployment Architecture

- **Multi-stage Docker build** optimizes image size and security
- **Rolling updates** ensure zero-downtime deployments
- **Horizontal Pod Autoscaling (HPA)** scales based on CPU/memory
- **Pod Disruption Budgets** maintain availability during updates
- **Health checks** ensure only healthy pods receive traffic
- **Anti-affinity rules** spread pods across nodes
- **Resource limits** prevent resource exhaustion

#### Monitoring and Troubleshooting

```bash
# Check deployment status
kubectl get pods -n echo-me-pro
kubectl get svc -n echo-me-pro
kubectl get ingress -n echo-me-pro

# View logs
kubectl logs -n echo-me-pro deployment/echo-me-pro --tail=100 -f

# Describe pod issues
kubectl describe pod -n echo-me-pro <pod-name>

# Check HPA status
kubectl get hpa -n echo-me-pro

# View events
kubectl get events -n echo-me-pro --sort-by='.lastTimestamp'
```

#### Security Best Practices

✅ **Implemented in this deployment**:
- Multi-stage Docker builds with minimal base images
- Non-root container execution
- Read-only root filesystem where possible
- Security context constraints
- Network policies preparation
- OIDC authentication for GitHub Actions
- Container image vulnerability scanning
- Azure Key Vault integration ready
- TLS/HTTPS ingress with cert-manager

#### Scaling and Performance

```bash
# Manual scaling
kubectl scale deployment echo-me-pro --replicas=5 -n echo-me-pro

# Check autoscaler behavior
kubectl describe hpa echo-me-pro -n echo-me-pro

# Update resource limits
kubectl set resources deployment echo-me-pro \
  --limits=cpu=2000m,memory=2Gi \
  --requests=cpu=500m,memory=1Gi \
  -n echo-me-pro
```

#### Deployment Files Structure

```
echo-me-pro/
├── Dockerfile                          # Multi-stage container build
├── .dockerignore                       # Files to exclude from image
├── .github/
│   ├── workflows/
│   │   └── deploy-aks.yml             # CI/CD pipeline
│   └── SECRETS.md                      # Setup guide for GitHub secrets
├── k8s/                                # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   └── pdb.yaml
└── helm/                               # Helm chart
    └── echo-me-pro/
        ├── Chart.yaml
        ├── values.yaml
        ├── values-staging.yaml
        ├── values-production.yaml
        └── templates/
            ├── deployment.yaml
            ├── service.yaml
            ├── ingress.yaml
            ├── configmap.yaml
            ├── secret.yaml
            ├── hpa.yaml
            ├── pdb.yaml
            ├── serviceaccount.yaml
            └── _helpers.tpl
```

#### Environment Management

The deployment supports multiple environments:

- **Staging** (develop branch): 
  - Namespace: `echo-me-pro-staging`
  - Auto-deploy on push to `develop`
  - Lower resource limits
  - Debug logging enabled

- **Production** (main branch):
  - Namespace: `echo-me-pro`
  - Requires manual approval
  - Higher replica count
  - Production-grade resources
  - Warning-level logging

#### Cost Optimization

- **Node pools**: Use appropriate VM sizes (Standard_D2s_v3 for testing)
- **Cluster autoscaler**: Enable for dynamic node scaling
- **Spot instances**: Consider for non-critical workloads
- **Resource requests**: Right-sized based on actual usage
- **HPA**: Automatically scale pods based on demand

#### Advanced Configuration

**Using Azure Key Vault for Secrets**:
```bash
# Enable the Azure Key Vault provider for Secrets Store CSI driver
az aks enable-addons --addons azure-keyvault-secrets-provider \
  --name echo-me-pro-aks \
  --resource-group echo-me-pro-rg
```

Then uncomment the SecretProviderClass section in [k8s/secrets.yaml](k8s/secrets.yaml).

**Application Gateway Ingress Controller**:
For production workloads, consider using Azure Application Gateway instead of nginx:
```bash
az aks enable-addons \
  --resource-group echo-me-pro-rg \
  --name echo-me-pro-aks \
  --addons ingress-appgw \
  --appgw-subnet-cidr "10.2.0.0/16"
```

#### Rollback Procedures

```bash
# View rollout history
kubectl rollout history deployment/echo-me-pro -n echo-me-pro

# Rollback to previous version
kubectl rollout undo deployment/echo-me-pro -n echo-me-pro

# Rollback to specific revision
kubectl rollout undo deployment/echo-me-pro --to-revision=2 -n echo-me-pro

# Using Helm
helm rollback echo-me-pro -n echo-me-pro
```

## Dependencies

- `gradio` - Web interface
- `openai` - OpenAI API client
- `openai-agents` - Agent framework
- `pypdf` - PDF parsing for LinkedIn profile
- `requests` - HTTP requests for push notifications
- `sendgrid` - Email service for sending personalized emails with CV
- `python-dotenv` - Environment variable management

## Configuration

Customize the experience by modifying:
- `me/summary.txt` - Personal summary text
- `me/linkedin.pdf` - LinkedIn profile PDF
- System prompt in `Me.system_prompt()` method
- OpenAI model in `me.chat()` method (default: `gpt-4o-mini`)

## Troubleshooting

**Missing files error**: If you get `FileNotFoundError` when running the app, ensure you have:
- Created the `me/` directory
- Added `me/summary.txt` with your personal summary
- Added `me/linkedin.pdf` with your LinkedIn profile export

**Missing CV file**: If email sending fails with "CV file not found", ensure:
- You have created `me/myCV.pdf` with your CV/Resume

**SendGrid configuration error**: If emails fail to send, check:
- `SENDGRID_API_KEY` is set in your `.env` file
- `SENDER_EMAIL` is set in your `.env` file
- The email address is a verified sender in your SendGrid account

**Gradio version error**: If you get `TypeError: ChatInterface.__init__() got an unexpected keyword argument 'type'`, ensure you're using Gradio 5.0+ or remove the `type` parameter.

**Missing environment variables**: Ensure your `.env` file contains all required API keys:
- `OPENAI_API_KEY`
- `PUSHOVER_TOKEN` and `PUSHOVER_USER`
- `SENDGRID_API_KEY`, `SENDER_EMAIL`, and `SENDER_NAME`

**Push notification failures**: Check Pushover credentials and review logs for specific HTTP errors.

## License

[Add your license here]

## Author

Imad Eddine BOUIHI
