#!/bin/bash
set -e

echo "🚀 Starting deployment of Inventory microservice to Minikube..."

# Start Minikube if not running
if ! minikube status >/dev/null 2>&1; then
  echo "🔧 Starting Minikube..."
  minikube start
else
  echo "✅ Minikube already running."
fi

echo "📦 Applying Kubernetes manifests..."

# Apply all manifests
kubectl apply -f k8s/inventory-deployment.yaml
kubectl apply -f k8s/inventory-service.yaml

echo "⏳ Waiting for all pods to become ready..."
kubectl wait --for=condition=available --timeout=120s deployment/inventory-service

echo "✅ Inventory service deployed successfully!"

echo ""
echo "🌐 Access Inventory service via the following URL:"

# Retrieve and print service URL
echo "Inventory service: $(minikube service inventory-service --url)"

echo ""
echo "🎉 Deployment complete!"
