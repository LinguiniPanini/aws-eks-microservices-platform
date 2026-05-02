#!/usr/bin/env bash
set -e
source "$(dirname "$0")/00-config.sh"

echo "Creando cola SQS..."
QUEUE_URL=$(aws sqs create-queue \
  --queue-name "$SQS_QUEUE_NAME" \
  --attributes "VisibilityTimeout=120" \
  --region "$AWS_REGION" \
  --query 'QueueUrl' --output text)

echo "Cola creada: $QUEUE_URL"
