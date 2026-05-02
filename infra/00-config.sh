#!/usr/bin/env bash
# Variables compartidas para todos los scripts de infraestructura.
# Editar segun el entorno antes de correr el resto.

export AWS_REGION="us-east-1"
export EXPEDIENTE="745741"

export RDS_INSTANCE_ID="examen2-db"
export RDS_DB_NAME="examen2"
export RDS_USER="postgres"
export RDS_PASSWORD="ChangeMe123!"

export SQS_QUEUE_NAME="examen2-notas"
export S3_BUCKET="${EXPEDIENTE}-esi3898k-examen2"
export SNS_TOPIC_NAME="examen2-notificaciones"
export SNS_EMAIL="cliente@example.com"

export VPC_ID=""        # llenar despues del cluster
export NODE_SG_ID=""    # security group de los nodos del cluster
