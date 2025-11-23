#!/bin/bash

# Stop on error
set -e

PROJECT_ID="my-mvp-backend" # Update this if your project ID is different
SERVICE_NAME="mathiter-backend"
REGION="us-central1"

echo "🚀 Deploying Backend to Google Cloud Run..."

# 1. Enable necessary services (if not already enabled)
# echo "🔌 Enabling Cloud Build and Cloud Run APIs..."
# gcloud services enable cloudbuild.googleapis.com run.googleapis.com --project $PROJECT_ID

# 2. Deploy using source (requires gcloud beta or Cloud Build setup)
# We will use 'gcloud run deploy --source .' which builds the container automatically via Cloud Build
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --project $PROJECT_ID \
  --port 5001 \
  --set-env-vars PROJECT_ID=$PROJECT_ID,AI_LOCATION=$REGION,FLASK_ENV=production \
  --quiet

echo "✨ Backend deployment initiated!"
