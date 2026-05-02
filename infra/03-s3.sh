#!/usr/bin/env bash
set -e
source "$(dirname "$0")/00-config.sh"

echo "Creando bucket S3 $S3_BUCKET..."
if [ "$AWS_REGION" = "us-east-1" ]; then
  aws s3api create-bucket \
    --bucket "$S3_BUCKET" \
    --region "$AWS_REGION"
else
  aws s3api create-bucket \
    --bucket "$S3_BUCKET" \
    --region "$AWS_REGION" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION"
fi

echo "Bucket listo: $S3_BUCKET"
