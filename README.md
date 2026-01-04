
---

# `README2.md`

````md
# Kubernetes Minimal App (Ingress + Service + Liveness/Readiness + Path Routing)

This repository is a **starter Kubernetes project** designed to demonstrate core
Kubernetes concepts, focusing on **networking behavior**, **health checks** and
**traffic routing**, rather than application development.

The application is intentionally minimal and based on a simple Python HTTP server.
The goal is to show how Kubernetes interacts with applications through
**liveness and readiness probes**, **Services**, and **Ingress**.

---

## What this project demonstrates

- A minimal HTTP application running in a container
- Liveness probe (`GET /healthz`)
- Readiness probe (`GET /readyz`)
- Kubernetes Deployments with multiple replicas
- ClusterIP Services for internal load balancing
- Ingress (nginx) as the external entry point
- **Path-based HTTP routing**
- Networking flow: **Ingress → Service → Pod**

---

## Application overview

The application:
- is written in **plain Python (no framework)**
- exposes an HTTP server on port `8080`
- is **not** intended for production use
- contains no business logic or persistence

Endpoints:
- `GET /` – test endpoint
- `GET /healthz` – liveness probe
- `GET /readyz` – readiness probe

The `/readyz` endpoint performs a simple DNS check (`google.com`) to simulate an
external dependency and demonstrate how Kubernetes removes Pods from traffic
when they are not ready.

---

## Path-based routing overview

This project deploys **two backend applications** using the same container image:

- **minimal-app (v1)** – default backend
- **minimal-app-v2 (v2)** – secondary backend

Ingress routing rules:
- `GET /` → `minimal-app`
- `GET /v2` → `minimal-app-v2`

Each backend has its own Deployment, Service and health probes, allowing
independent readiness and traffic routing.

---

## Repository structure

```text
.
├── app/
│   ├── app.py
│   └── Dockerfile
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 10-deployment.yaml
│   ├── 15-deployment-v2.yaml
│   ├── 20-service.yaml
│   ├── 25-service-v2.yaml
│   └── 30-ingress.yaml
├── kind-config.yaml
├── .gitignore
└── README2.md
````

---

## Prerequisites

* Docker
* kubectl
* kind (Kubernetes in Docker)

---

## Build the Docker image

```bash
docker build -t minimal-app:dev ./app
```

---

## Create a local Kubernetes cluster

```bash
kind create cluster --name demo --config kind-config.yaml
```

This configuration:

* Exposes ports 80 and 443 on localhost for Ingress
* Labels the control-plane node as `ingress-ready=true`
* Enables the ingress-nginx controller to work correctly with kind

Load the local image into the cluster:

```bash
kind load docker-image minimal-app:dev --name demo
```

---

## Install ingress-nginx (for kind)

```bash
kubectl label node demo-control-plane ingress-ready=true
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx rollout status deployment/ingress-nginx-controller
```

---

## Deploy the application

Apply all Kubernetes manifests:

```bash
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/10-deployment-v1.yaml
kubectl apply -f k8s/15-deployment-v2.yaml
kubectl apply -f k8s/20-service-v1.yaml
kubectl apply -f k8s/25-service-v2.yaml
kubectl apply -f k8s/30-ingress.yaml
```

---

## Check resources

```bash
kubectl -n demo get pods
kubectl -n demo get svc
kubectl -n demo get ingress
```

---

## Test without Ingress (port-forward)

### Test v1 backend

```bash
kubectl -n demo port-forward svc/minimal-app 8080:80
```

In another terminal:

```bash
curl http://localhost:8080/
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
```

### Test v2 backend

Stop the previous port-forward and run:

```bash
kubectl -n demo port-forward svc/minimal-app-v2 8081:80
```

Then:

```bash
curl http://localhost:8081/
curl http://localhost:8081/healthz
curl http://localhost:8081/readyz
```

---

## Test with Ingress

On kind, ingress-nginx is exposed on localhost:

```bash
# Default backend (v1)
curl http://app.localtest.me/
curl http://app.localtest.me/healthz
curl http://app.localtest.me/readyz

# Path-based routing to v2 backend
curl http://app.localtest.me/v2
```

---

## Notes about readiness

The `/readyz` endpoint performs a DNS check to simulate a network dependency.

If outbound internet access or DNS is blocked, `/readyz` may return `503`,
causing Pods to become **NotReady**.
This demonstrates how Kubernetes removes unhealthy Pods from Service endpoints
and how Ingress stops routing traffic to them.

---

## Cleanup

```bash
kind delete cluster --name demo
```

---

## Disclaimer

This project uses a **minimal application template**.
The focus is on Kubernetes behavior, networking and traffic routing,
not on application development.

```

---




