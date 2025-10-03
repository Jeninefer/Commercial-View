# Deployment Guide

## Overview

This guide covers deployment options for the Commercial View Platform, from local development to production cloud deployment.

## Deployment Options

### 1. Local Development

**Best for:** Development, testing, demos

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard/app.py

# Run scheduler
python scheduler.py --now
```

**Pros:**
- Full control over environment
- Easy debugging
- No deployment costs

**Cons:**
- Not accessible remotely
- Requires local machine to be running
- No scalability

### 2. Docker Local

**Best for:** Testing containerization, consistent environment

```bash
# Build image
docker build -t commercial-view .

# Run dashboard only
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env commercial-view

# Or use docker-compose for full stack
docker-compose up -d
```

**Pros:**
- Consistent environment
- Easy to replicate
- Isolated from host system

**Cons:**
- Still requires local machine
- Resource overhead

### 3. Streamlit Community Cloud

**Best for:** Quick deployment, demos, small teams

#### Setup Steps:

1. **Prepare Repository:**
   ```bash
   # Ensure all files are committed
   git add .
   git commit -m "Prepare for Streamlit deployment"
   git push origin main
   ```

2. **Deploy:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Main file: `dashboard/app.py`
   - Click "Deploy"

3. **Configure Secrets:**
   - In app settings, click "Secrets"
   - Add your `.env` variables in TOML format:
   ```toml
   OPENAI_API_KEY = "sk-..."
   GOOGLE_DRIVE_FOLDER_URL = "https://..."
   HUBSPOT_API_KEY = "your-key"
   ```

**Pros:**
- ✅ Free for public repos
- ✅ Automatic HTTPS
- ✅ Easy to update (auto-deploy on push)
- ✅ Built-in authentication (if configured)

**Cons:**
- Limited resources (1GB RAM)
- Can't run background scheduler
- Public repositories only (for free tier)

### 4. Render

**Best for:** Production, scheduled jobs, full stack

#### Dashboard Deployment:

1. **Create Web Service:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect GitHub repository

2. **Configure:**
   ```
   Name: commercial-view-dashboard
   Environment: Python 3.11
   Build Command: pip install -r requirements.txt
   Start Command: streamlit run dashboard/app.py --server.port=$PORT --server.address=0.0.0.0
   ```

3. **Environment Variables:**
   - Add all variables from `.env`
   - Use Render's secret management

#### Scheduler Deployment:

1. **Create Background Worker:**
   - Click "New +" → "Background Worker"
   - Connect same repository

2. **Configure:**
   ```
   Name: commercial-view-scheduler
   Build Command: pip install -r requirements.txt
   Start Command: python scheduler.py
   ```

**Pros:**
- Free tier available
- Supports background workers
- Auto-deploy on push
- Custom domains
- Persistent disks

**Cons:**
- Free tier has limited resources
- Can spin down with inactivity

### 5. Google Cloud Run

**Best for:** Enterprise, scalability, GCP ecosystem

#### Prerequisites:
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init
```

#### Deploy:

1. **Build and push image:**
   ```bash
   # Enable required services
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   
   # Build with Cloud Build
   gcloud builds submit --tag gcr.io/PROJECT_ID/commercial-view
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy commercial-view \
     --image gcr.io/PROJECT_ID/commercial-view \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8501 \
     --memory 2Gi \
     --set-env-vars OPENAI_API_KEY=sk-...
   ```

3. **Deploy Scheduler:**
   ```bash
   # Create Cloud Scheduler job
   gcloud scheduler jobs create http daily-job \
     --schedule="0 8 * * *" \
     --uri="https://commercial-view-xxxxx.run.app/run-job" \
     --http-method=POST
   ```

**Pros:**
- Auto-scaling
- Pay per use
- Built-in load balancing
- Integrated with GCP services
- Support for secrets manager

**Cons:**
- Requires GCP account
- More complex setup
- Cost for high traffic

### 6. AWS (ECS/Fargate)

**Best for:** AWS ecosystem, enterprise deployments

#### Setup:

1. **Create ECR Repository:**
   ```bash
   aws ecr create-repository --repository-name commercial-view
   ```

2. **Build and Push:**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   
   # Build and tag
   docker build -t commercial-view .
   docker tag commercial-view:latest \
     ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/commercial-view:latest
   
   # Push
   docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/commercial-view:latest
   ```

3. **Create ECS Task Definition:**
   ```json
   {
     "family": "commercial-view",
     "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskRole",
     "containerDefinitions": [{
       "name": "dashboard",
       "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/commercial-view:latest",
       "portMappings": [{"containerPort": 8501}],
       "environment": [
         {"name": "OPENAI_API_KEY", "value": "sk-..."}
       ],
       "memory": 2048,
       "cpu": 1024
     }]
   }
   ```

4. **Create Service:**
   ```bash
   aws ecs create-service \
     --cluster default \
     --service-name commercial-view \
     --task-definition commercial-view \
     --desired-count 1 \
     --launch-type FARGATE
   ```

**Pros:**
- Full AWS integration
- Advanced networking options
- Auto-scaling
- Load balancing

**Cons:**
- Complex setup
- Higher cost
- Requires AWS expertise

## Production Checklist

### Security

- [ ] Use secrets manager (not .env in production)
- [ ] Enable HTTPS/SSL
- [ ] Implement authentication
- [ ] Configure CORS appropriately
- [ ] Regular security audits
- [ ] Rotate API keys periodically

### Performance

- [ ] Configure caching
- [ ] Optimize database queries
- [ ] Set up CDN for static assets
- [ ] Monitor resource usage
- [ ] Configure auto-scaling
- [ ] Implement rate limiting

### Monitoring

- [ ] Set up logging (Datadog, CloudWatch, etc.)
- [ ] Configure alerts
- [ ] Monitor uptime
- [ ] Track error rates
- [ ] Monitor API quotas
- [ ] Set up dashboards

### Backup & Recovery

- [ ] Regular data backups
- [ ] Database snapshots
- [ ] Disaster recovery plan
- [ ] Document rollback procedures

### CI/CD

- [ ] Automated testing pipeline
- [ ] Automated deployments
- [ ] Staging environment
- [ ] Blue-green deployment
- [ ] Rollback capability

## Environment-Specific Configuration

### Development
```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_MOCK_DATA=true
```

### Staging
```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
ENABLE_MOCK_DATA=false
API_RATE_LIMIT=100
```

### Production
```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
ENABLE_MOCK_DATA=false
API_RATE_LIMIT=1000
ENABLE_MONITORING=true
```

## Scaling Considerations

### Horizontal Scaling

For high traffic:

1. **Load Balancer:**
   - Use Cloud Load Balancer (GCP)
   - Or Application Load Balancer (AWS)
   - Or NGINX reverse proxy

2. **Multiple Instances:**
   ```bash
   # Docker Compose with scaling
   docker-compose up -d --scale dashboard=3
   ```

3. **Session Management:**
   - Use Redis for shared sessions
   - Implement sticky sessions

### Vertical Scaling

Increase resources:

```yaml
# docker-compose.yml
services:
  dashboard:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Monitoring & Observability

### Health Checks

Add health check endpoint:

```python
# dashboard/app.py
@st.cache_resource
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### Logging

Configure structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)
logger.info(json.dumps({
    "event": "disbursement_optimization",
    "status": "success",
    "cash_available": 1000000,
    "loans_approved": 15
}))
```

### Metrics

Track key metrics:

- Request rate
- Response time
- Error rate
- CPU/Memory usage
- API quota usage

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port
lsof -i :8501
# Kill process
kill -9 PID
```

**Memory Issues:**
```bash
# Increase memory limit
docker run -m 4g commercial-view
```

**Environment Variables Not Loading:**
```bash
# Verify .env exists
ls -la .env
# Check Docker volume
docker run -it commercial-view env | grep OPENAI
```

## Cost Optimization

### Free Tier Options
1. Streamlit Community Cloud (limited)
2. Render free tier
3. Google Cloud free credits
4. AWS free tier (12 months)

### Cost Reduction Tips
- Use spot instances (AWS)
- Preemptible VMs (GCP)
- Scale down during off-hours
- Optimize image size
- Cache API responses
- Use connection pooling

## Support Resources

- [Streamlit Deployment Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Render Documentation](https://render.com/docs)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
