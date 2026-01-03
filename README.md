
---

## `README.md`

````md
# Kubernetes Minimal App (Ingress + Service + Liveness/Readiness)

This repository is a **starter Kubernetes project** designed to demonstrate core
Kubernetes concepts without focusing on application development.

The application is intentionally minimal and based on a simple Python template.
The main goal is to show how Kubernetes interacts with an application through
**liveness and readiness probes**, **Services**, and **Ingress**.

## What this project demonstrates

- A minimal HTTP application running in a container
- Liveness probe (`GET /healthz`)
- Readiness probe (`GET /readyz`)
- Kubernetes Deployment with multiple replicas
- ClusterIP Service for internal load balancing
- Ingress (nginx) as the external entry point
- Basic networking flow: Ingress → Service → Pod

## Application overview

The application:
- is written in **plain Python (no framework)**
- exposes a small HTTP server on port `8080`
- is **not** intended for production use
- contains no business logic or persistence

Endpoints:
- `GET /` – test endpoint
- `GET /healthz` – liveness probe
- `GET /readyz` – readiness probe

The `/readyz` endpoint performs a simple DNS/network check to simulate an external
dependency and demonstrate how Kubernetes removes Pods from traffic when they are
not ready.

## Repository structure

```text
.
├── app/
│   ├── app.py
│   └── Dockerfile
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 10-deployment.yaml
│   ├── 20-service.yaml
│   └── 30-ingress.yaml
├── .gitignore
└── README.md
````

## Prerequisites

* Docker
* kubectl
* kind (Kubernetes in Docker)

## Build the Docker image

```bash
docker build -t minimal-app:dev ./app
```

# Create a local Kubernetes cluster
```bash
kind create cluster --name demo --config kind-config.yaml
```

This configuration:
- Exposes ports 80 and 443 on localhost for Ingress
- Labels the control-plane node as `ingress-ready=true`
- Enables the Ingress controller to work correctly with kind
```

Load the local image into the kind cluster:

```bash
kind load docker-image minimal-app:dev --name demo
```

## Install ingress-nginx (for kind)

```bash
kubectl label node demo-control-plane ingress-ready=true
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx rollout status deployment/ingress-nginx-controller
```

## Deploy the application

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/10-deployment.yaml
kubectl apply -f k8s/20-service.yaml
kubectl apply -f k8s/30-ingress.yaml
```

Check resources:

```bash
kubectl -n demo get pods
kubectl -n demo get svc
kubectl -n demo get ingress
```

## Test without Ingress (port-forward)

```bash
kubectl -n demo port-forward svc/minimal-app 8080:80
```

In another terminal:

```bash
curl http://localhost:8080/
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
```

## Test with Ingress

On kind, ingress-nginx is exposed on localhost:

```bash
curl http://app.localtest.me/
curl http://app.localtest.me/healthz
curl http://app.localtest.me/readyz
```

## Notes about readiness

The `/readyz` endpoint performs a simple DNS check (`google.com`) to simulate a
network dependency.

If outbound internet access or DNS is blocked in your environment, `/readyz`
may return `503`, causing Pods to become **NotReady**. This behavior is intentional
and useful to observe how Kubernetes stops routing traffic to unhealthy Pods.

## Cleanup

```bash
kind delete cluster --name demo
```

## Disclaimer

This project uses a **minimal application template**.
The focus of the repository is Kubernetes behavior and networking concepts,
not application development.

```



