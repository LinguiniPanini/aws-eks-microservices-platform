# Examen 2 - Desarrollo en la Nube

API de ventas desplegada como 4 pods en Kubernetes (EKS) sobre AWS.

## Estructura

```
api/              codigo del pod api (Flask)
pdf-generator/    codigo del pod pdf-generator (Flask)
notifier/         codigo del pod notifier (Flask)
receipt-worker/   codigo del pod receipt-worker (consumidor SQS)
k8s/              manifiestos de Kubernetes
infra/            scripts bash para crear recursos AWS
cluster/          cluster.yaml + script para crear el EKS
sql/              schema PostgreSQL
```

## Despliegue

### 1. Cluster EKS

```bash
cd cluster/
# editar ACCOUNT_ID en cluster.yaml
./crear-cluster.sh
```

### 2. Recursos AWS

Editar `infra/00-config.sh` con valores propios (expediente, password, email).

```bash
cd infra/
./02-sqs.sh
./03-s3.sh
./04-sns.sh    # confirmar suscripcion en el correo
# RDS necesita VPC_ID y NODE_SG_ID del cluster
./01-rds.sh

# cargar schema
PGPASSWORD=... psql -h <ENDPOINT> -U postgres -d examen2 -f ../sql/iniciador.sql

# crear secretos con los outputs anteriores
RDS_HOST=... SQS_QUEUE_URL=... SNS_TOPIC_ARN=... ./05-secrets.sh
```

### 3. Imagenes Docker

```bash
for s in api pdf-generator notifier receipt-worker; do
  docker build -t USUARIO/examen2-$s ./$s
  docker push USUARIO/examen2-$s
done
```

Reemplazar `DOCKERHUB_USER` en `k8s/*.yaml` con el usuario de Docker Hub.

### 4. Kubernetes

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pdf-generator.yaml
kubectl apply -f k8s/notifier.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/receipt-worker.yaml

# obtener DNS del LoadBalancer del api
kubectl get svc api

# actualizar API_PUBLIC_URL en configmap.yaml con ese DNS y reaplicar
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment notifier
```

## Endpoints

- `POST/GET/PUT/DELETE /clientes`
- `POST /clientes/{id}/domicilios`, `GET/PUT/DELETE /domicilios/{id}`
- `POST/GET/PUT/DELETE /productos`
- `POST /notas`
- `GET /notas/{id}`  (JSON, no afecta metadatos)
- `GET /notas/{id}/pdf`  (descarga PDF, marca nota-descargada=true)
- `POST /notas/{id}/enviar`  (reenvio por email)
