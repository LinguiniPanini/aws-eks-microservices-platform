# AWS EKS Microservices Platform

[![AWS EKS](https://img.shields.io/badge/AWS-EKS-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/eks/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Docker](https://img.shields.io/badge/Containers-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS SQS](https://img.shields.io/badge/Messaging-AWS%20SQS-FF4F8B?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/sqs/)
[![PostgreSQL](https://img.shields.io/badge/Database-Amazon%20RDS-336791?logo=postgresql&logoColor=white)](https://aws.amazon.com/rds/)

A distributed, event-driven sales and invoicing microservices platform orchestrated on **Amazon Elastic Kubernetes Service (EKS)**. The architecture integrates asynchronous message buffering (**Amazon SQS**), cloud artifact storage (**Amazon S3**), event notifications (**Amazon SNS**), and relational persistence (**Amazon RDS PostgreSQL**).

---

## Architecture Overview

```
                          [ Client Request ]
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │ AWS LoadBalancer / K8s Svc   │
                   └──────────────┬───────────────┘
                                  │
            ┌─────────────────────┴─────────────────────┐
            ▼                                           ▼
   ┌──────────────────┐                       ┌──────────────────┐
   │    API Pod       │                       │  Notifier Pod    │
   │  (Flask REST)    ├──────────┐            │   (Email / SNS)  │
   └────────┬─────────┘          │            └─────────▲────────┘
            │                    ▼                      │
            │           ┌─────────────────┐             │
            │           │   Amazon SQS    │             │
            │           │  (Order Queue)  │             │
            │           └────────┬────────┘             │
            ▼                    │                      │
   ┌──────────────────┐          ▼                      │
   │    Amazon RDS    │   ┌──────────────────┐          │
   │   (PostgreSQL)   │   │  Receipt Worker  ├──────────┘
   └──────────────────┘   │  (SQS Consumer)  │
                          └────────┬─────────┘
                                   │
                                   ▼
                          ┌──────────────────┐
                          │    Amazon S3     │
                          │ (PDF Generation) │
                          └──────────────────┘
```

### Microservices
1. **API Service (`/api`)**: Core REST entrypoint managing customers, addresses, products, and order notes.
2. **PDF Generator (`/pdf-generator`)**: Dedicated document rendering engine producing formatted purchase receipts.
3. **Receipt Worker (`/receipt-worker`)**: High-throughput asynchronous daemon pulling order messages from Amazon SQS, invoking receipt generation, and managing state transitions.
4. **Notifier (`/notifier`)**: Event integration publishing delivery and invoice notifications via Amazon SNS email topics.

---

## Repository Structure

```
├── api/             # REST API microservice (Python / Flask)
├── pdf-generator/   # Document synthesis engine (Flask / PDF generation)
├── notifier/        # Notification service publishing to Amazon SNS
├── receipt-worker/  # Long-polling SQS consumer worker
├── k8s/             # Kubernetes manifests (Deployments, Services, ConfigMaps, Secrets)
├── infra/           # Automated AWS infrastructure scripts (SQS, S3, SNS, RDS, IAM)
├── cluster/         # EKS cluster definition (cluster.yaml) & provisioning scripts
└── sql/             # PostgreSQL database schema and migrations
```

---

## Deployment Workflow

### 1. Provision Amazon EKS Cluster
Configure your AWS Account ID in `cluster/cluster.yaml` and run:
```bash
cd cluster/
./crear-cluster.sh
```

### 2. Provision AWS Infrastructure
Configure environment variables in `infra/00-config.sh` (credentials, notification email, region):
```bash
cd infra/
./02-sqs.sh     # Amazon SQS order queues
./03-s3.sh      # Amazon S3 receipts bucket
./04-sns.sh     # Amazon SNS topics and email subscription
./01-rds.sh     # Amazon RDS PostgreSQL instance within cluster VPC

# Initialize database schema
PGPASSWORD=$DB_PASSWORD psql -h <RDS_ENDPOINT> -U postgres -d salesdb -f ../sql/iniciador.sql

# Synchronize Kubernetes Secrets with AWS resources
RDS_HOST=<ENDPOINT> SQS_QUEUE_URL=<URL> SNS_TOPIC_ARN=<ARN> ./05-secrets.sh
```

### 3. Container Images (Docker)
Build and push images for each microservice:
```bash
for service in api pdf-generator notifier receipt-worker; do
  docker build -t <DOCKER_USER>/sales-$service ./$service
  docker push <DOCKER_USER>/sales-$service
done
```

### 4. Kubernetes Deployment
Apply the Kubernetes manifests to orchestrate the pods across the EKS cluster:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pdf-generator.yaml
kubectl apply -f k8s/notifier.yaml
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/receipt-worker.yaml

# Retrieve the external DNS of the AWS LoadBalancer service:
kubectl get svc api

# Update API_PUBLIC_URL in k8s/configmap.yaml with the LoadBalancer DNS and rollout:
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment notifier
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST / GET / PUT / DELETE` | `/clientes` | Customer management |
| `POST / GET / PUT / DELETE` | `/clientes/{id}/domicilios` | Customer address records |
| `POST / GET / PUT / DELETE` | `/productos` | Catalog & product inventory |
| `POST` | `/notas` | Create purchase order (triggers SQS flow) |
| `GET` | `/notas/{id}` | Retrieve order details |
| `GET` | `/notas/{id}/pdf` | Stream or download generated receipt from S3 |
| `POST` | `/notas/{id}/enviar`| Re-dispatch notification via SNS |

---

## Author
**Luis Alberto González Escamilla**  
Software & Systems Engineer · AI Agents & Cloud Solutions
