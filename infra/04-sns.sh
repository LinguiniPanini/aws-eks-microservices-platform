#!/usr/bin/env bash
set -e
source "$(dirname "$0")/00-config.sh"

echo "Creando topic SNS..."
TOPIC_ARN=$(aws sns create-topic \
  --name "$SNS_TOPIC_NAME" \
  --region "$AWS_REGION" \
  --query 'TopicArn' --output text)

echo "Suscribiendo email $SNS_EMAIL..."
aws sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol email \
  --notification-endpoint "$SNS_EMAIL" \
  --region "$AWS_REGION"

echo "Topic ARN: $TOPIC_ARN"
echo "IMPORTANTE: confirmar la suscripcion desde el correo $SNS_EMAIL"
