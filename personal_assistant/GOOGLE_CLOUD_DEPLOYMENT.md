# Google Cloud Deployment Guide - Personal Assistant

## Prerequisites

### 1. Google Cloud Account Setup
- Google Cloud account with billing enabled
- A Google Cloud project created

### 2. Local Tools Installation
```bash
# Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Verify installation
gcloud --version
```

### 3. Docker Setup (if not already done)
```bash
# Install Docker Desktop
# Visit: https://www.docker.com/products/docker-desktop
```

## Initial Setup

### 1. Authenticate with Google Cloud
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Configure Docker for Google Cloud
```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker
```

## 🔧 Environment Setup

### 1. Create Production Environment File
Create `.env.production` in your personal_assistant directory:

```env
# Google AI API Key
GOOGLE_API_KEY=your-google-api-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_API_KEY=your-supabase-anon-key

# JWT Secret for Authentication
JWT_SECRET=your-super-secure-jwt-secret-for-production

# Default User (for backward compatibility)
USER_ID=default_user

# Environment
NODE_ENV=production
```

### 2. Get Your Environment Variables

#### Google AI API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy the key

#### Supabase Configuration:
1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to Settings → API
4. Copy URL and anon/public key

## Deployment Methods

Choose one of these deployment methods:


## Method 1: Deploy from Source (Recommended)

### 1. Deploy to Cloud Run
```bash
# Navigate to your project directory
cd personal_assistant

# Deploy from source (Cloud Build will build the image)
gcloud run deploy personal-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --env-vars-file .env.production
```

### 2. Set Environment Variables (Alternative)
If you prefer to set environment variables individually:
```bash
gcloud run deploy personal-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --set-env-vars \
    GOOGLE_API_KEY="your-api-key",\
    SUPABASE_URL="your-supabase-url",\
    SUPABASE_API_KEY="your-supabase-key",\
    JWT_SECRET="your-jwt-secret"
```


## Method 2: Build and Push Docker Image

### 1. Build and Push to Container Registry
```bash
# Set your project ID
PROJECT_ID="your-project-id"

# Build and tag the image
docker build -t gcr.io/$PROJECT_ID/personal-assistant .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/personal-assistant
```

### 2. Deploy from Registry
```bash
gcloud run deploy personal-assistant \
  --image gcr.io/$PROJECT_ID/personal-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --env-vars-file .env.production
```

## Verify Deployment

### 1. Get Service URL
```bash
# Get the deployed service URL
gcloud run services describe personal-assistant \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

### 2. Test Health Check
```bash
# Replace with your actual service URL
SERVICE_URL="https://personal-assistant-xyz-uc.a.run.app"

# Test health endpoint
curl $SERVICE_URL/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Personal Assistant API",
  "version": "1.0.0",
  "authentication": "session-based"
}
```

### 3. Test Expense Query
```bash
# Test expense endpoint
curl -X POST $SERVICE_URL/expense/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show my expenses"}'
```

## Security Configuration

### 1. Restrict Access (Optional)
If you want to restrict access to authenticated users only:
```bash
gcloud run services update personal-assistant \
  --region us-central1 \
  --no-allow-unauthenticated
```

### 2. Custom Domain (Optional)
```bash
# Map custom domain
gcloud run domain-mappings create \
  --service personal-assistant \
  --domain your-domain.com \
  --region us-central1
```

## Monitoring and Logs

### 1. View Logs
```bash
# View recent logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=personal-assistant" \
  --limit 50

# Follow logs in real-time
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=personal-assistant"
```

### 2. Monitor Performance
```bash
# Open Cloud Console monitoring
echo "Visit: https://console.cloud.google.com/run/detail/us-central1/personal-assistant"
```

## Updates and Maintenance

### 1. Update Environment Variables
```bash
# Update a single environment variable
gcloud run services update personal-assistant \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY="new-api-key"

# Update from file
gcloud run services update personal-assistant \
  --region us-central1 \
  --env-vars-file .env.production
```

### 2. Deploy New Version
```bash
# Simply re-run the deploy command
gcloud run deploy personal-assistant \
  --source . \
  --platform managed \
  --region us-central1
```

### 3. Rollback (if needed)
```bash
# List revisions
gcloud run revisions list --service personal-assistant --region us-central1

# Rollback to previous revision
gcloud run services update-traffic personal-assistant \
  --region us-central1 \
  --to-revisions REVISION_NAME=100
```

## Cost Optimization

### 1. Configure Auto-scaling
```bash
gcloud run services update personal-assistant \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 5 \
  --concurrency 80
```

### 2. Monitor Costs
- Visit [Google Cloud Billing](https://console.cloud.google.com/billing)
- Set up billing alerts
- Monitor Cloud Run usage

## Troubleshooting

### Common Issues:

#### 1. Build Failures
```bash
# Check build logs
gcloud builds log [BUILD_ID]

# Common fix: increase timeout
gcloud config set builds/timeout 1200
```

#### 2. Memory Issues
```bash
# Increase memory allocation
gcloud run services update personal-assistant \
  --region us-central1 \
  --memory 2Gi
```

#### 3. Environment Variable Issues
```bash
# Check current environment variables
gcloud run services describe personal-assistant \
  --region us-central1 \
  --format='value(spec.template.spec.template.spec.containers[0].env[].name,spec.template.spec.template.spec.containers[0].env[].value)'
```

#### 4. Connection Issues
```bash
# Check service status
gcloud run services list

# Check logs for errors
gcloud logs read "resource.type=cloud_run_revision" --limit 100
```

## 📱 Frontend Integration

Once deployed, update your React frontend to use the Cloud Run URL:

```javascript
// In your React app
const API_BASE_URL = 'https://your-service-url.run.app';

// Update axios configuration
axios.defaults.baseURL = API_BASE_URL;
```
