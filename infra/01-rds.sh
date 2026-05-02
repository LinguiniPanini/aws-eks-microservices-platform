#!/usr/bin/env bash
set -e
source "$(dirname "$0")/00-config.sh"

echo "Creando security group para RDS..."
SG_NAME="examen2-rds-sg"
RDS_SG_ID=$(aws ec2 create-security-group \
  --group-name "$SG_NAME" \
  --description "Acceso a Postgres desde nodos del cluster" \
  --vpc-id "$VPC_ID" \
  --region "$AWS_REGION" \
  --query 'GroupId' --output text)

aws ec2 authorize-security-group-ingress \
  --group-id "$RDS_SG_ID" \
  --protocol tcp --port 5432 \
  --source-group "$NODE_SG_ID" \
  --region "$AWS_REGION"

echo "Creando instancia RDS PostgreSQL..."
aws rds create-db-instance \
  --db-instance-identifier "$RDS_INSTANCE_ID" \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username "$RDS_USER" \
  --master-user-password "$RDS_PASSWORD" \
  --allocated-storage 20 \
  --db-name "$RDS_DB_NAME" \
  --vpc-security-group-ids "$RDS_SG_ID" \
  --region "$AWS_REGION" \
  --no-publicly-accessible

echo "Esperando a que la instancia este disponible..."
aws rds wait db-instance-available \
  --db-instance-identifier "$RDS_INSTANCE_ID" \
  --region "$AWS_REGION"

ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier "$RDS_INSTANCE_ID" \
  --region "$AWS_REGION" \
  --query 'DBInstances[0].Endpoint.Address' --output text)

echo "RDS listo en: $ENDPOINT"
echo "Cargar el schema con:"
echo "  PGPASSWORD=$RDS_PASSWORD psql -h $ENDPOINT -U $RDS_USER -d $RDS_DB_NAME -f ../sql/iniciador.sql"
