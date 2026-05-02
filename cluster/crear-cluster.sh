#!/usr/bin/env bash
set -e

# Reemplazar ACCOUNT_ID en cluster.yaml antes de correr este script.
# Luego:
#   1) eksctl crea el cluster + nodegroup
#   2) actualiza kubeconfig para apuntar al cluster nuevo

eksctl create cluster -f cluster.yaml

aws eks update-kubeconfig --region us-east-1 --name examen2

kubectl get nodes
