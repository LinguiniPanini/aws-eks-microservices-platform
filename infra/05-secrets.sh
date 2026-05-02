#!/usr/bin/env bash
set -e
source "$(dirname "$0")/00-config.sh"

# Este script crea las entradas en Secrets Manager con los valores
# de los recursos creados por los scripts anteriores.
# Pasar los valores como variables de entorno o editarlas aqui antes de correr.

: "${RDS_HOST:?RDS_HOST requerido (host del RDS, ej. examen2-db.xxx.rds.amazonaws.com)}"
: "${SQS_QUEUE_URL:?SQS_QUEUE_URL requerido}"
: "${SNS_TOPIC_ARN:?SNS_TOPIC_ARN requerido}"

echo "Creando secreto examen2/rds..."
aws secretsmanager create-secret \
  --name examen2/rds \
  --secret-string "{\"host\":\"$RDS_HOST\",\"port\":5432,\"dbname\":\"$RDS_DB_NAME\",\"user\":\"$RDS_USER\",\"password\":\"$RDS_PASSWORD\"}" \
  --region "$AWS_REGION"

echo "Creando secreto examen2/sqs..."
aws secretsmanager create-secret \
  --name examen2/sqs \
  --secret-string "{\"queue_url\":\"$SQS_QUEUE_URL\"}" \
  --region "$AWS_REGION"

echo "Creando secreto examen2/s3..."
aws secretsmanager create-secret \
  --name examen2/s3 \
  --secret-string "{\"bucket\":\"$S3_BUCKET\"}" \
  --region "$AWS_REGION"

echo "Creando secreto examen2/sns..."
aws secretsmanager create-secret \
  --name examen2/sns \
  --secret-string "{\"topic_arn\":\"$SNS_TOPIC_ARN\"}" \
  --region "$AWS_REGION"

echo "Listo. Secrets Manager configurado."
