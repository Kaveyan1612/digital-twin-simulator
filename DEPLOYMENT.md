# Deployment Guide

## Overview

This guide covers deploying the Digital Twin Simulator to production environments.

## Architecture Options

### Option 1: Docker Compose (Recommended for Small Deployments)

Single host with all services.

### Option 2: Kubernetes (For Scale)

Container orchestration with auto-scaling.

### Option 3: Traditional VM/Bare Metal

Direct installation on servers.

---

## Docker Compose Deployment

### Prerequisites

- Docker 24+
- Docker Compose 2+
- 2GB+ RAM
- 10GB+ disk

### Production Configuration

Create `.env.production`:

```env
APP_ENV=production
DATABASE_URL=postgresql://postgres:secure_password@db:5432/digital_twin
SIMULATION_FREQUENCY=10
WEBSOCKET_UPDATE_RATE=5
MAX_SPEED=5000
MAX_TEMPERATURE=120
MAX_CURRENT=50
MAX_VIBRATION=10
MOTOR_ID=MOTOR-001
ANOMALY_DETECTION_ENABLED=true
ML_ANOMALY_DETECTION_ENABLED=true
PREDICTION_ENABLED=true
LIVE_HISTORY_POINTS=1000
DATABASE_RETENTION_DAYS=30
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com
```

### Deploy

```bash
# Build and start
docker compose -f docker-compose.yml --env-file .env.production up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop
docker compose down
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend health
curl http://localhost/
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes 1.28+
- kubectl configured
- Helm 3+
- Ingress controller (nginx)
- cert-manager for TLS

### Namespace

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: digital-twin
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: digital-twin-config
  namespace: digital-twin
data:
  APP_ENV: "production"
  SIMULATION_FREQUENCY: "10"
  WEBSOCKET_UPDATE_RATE: "5"
  MAX_SPEED: "5000"
  MAX_TEMPERATURE: "120"
  MAX_CURRENT: "50"
  MAX_VIBRATION: "10"
  MOTOR_ID: "MOTOR-001"
  ANOMALY_DETECTION_ENABLED: "true"
  ML_ANOMALY_DETECTION_ENABLED: "true"
  PREDICTION_ENABLED: "true"
  LIVE_HISTORY_POINTS: "1000"
  DATABASE_RETENTION_DAYS: "30"
  LOG_LEVEL: "INFO"
```

### Secret

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: digital-twin-secrets
  namespace: digital-twin
type: Opaque
stringData:
  DATABASE_URL: "postgresql://postgres:secure_password@postgres:5432/digital_twin"
  CORS_ORIGINS: "https://digital-twin.your-domain.com"
```

### PostgreSQL (Using Operator or External)

```yaml
# postgres.yaml - For external managed DB, skip this
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: digital-twin-db
  namespace: digital-twin
spec:
  instances: 1
  postgresql:
    parameters:
      max_connections: "100"
  storage:
    size: 10Gi
```

### Backend Deployment

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin-backend
  namespace: digital-twin
spec:
  replicas: 2
  selector:
    matchLabels:
      app: digital-twin-backend
  template:
    metadata:
      labels:
        app: digital-twin-backend
    spec:
      containers:
      - name: backend
        image: your-registry/digital-twin-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: digital-twin-config
        - secretRef:
            name: digital-twin-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Backend Service

```yaml
# backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: digital-twin-backend
  namespace: digital-twin
spec:
  selector:
    app: digital-twin-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Frontend Deployment

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: digital-twin-frontend
  namespace: digital-twin
spec:
  replicas: 2
  selector:
    matchLabels:
      app: digital-twin-frontend
  template:
    metadata:
      labels:
        app: digital-twin-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/digital-twin-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
```

### Frontend Service

```yaml
# frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: digital-twin-frontend
  namespace: digital-twin
spec:
  selector:
    app: digital-twin-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: digital-twin-ingress
  namespace: digital-twin
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/websocket-services: "digital-twin-backend"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - digital-twin.your-domain.com
    secretName: digital-twin-tls
  rules:
  - host: digital-twin.your-domain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: digital-twin-backend
            port:
              number: 8000
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: digital-twin-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: digital-twin-frontend
            port:
              number: 80
```

### Apply

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
kubectl apply -f ingress.yaml
```

### Verify

```bash
kubectl get pods -n digital-twin
kubectl get svc -n digital-twin
kubectl get ingress -n digital-twin
kubectl logs -n digital-twin -l app=digital-twin-backend
```

---

## Traditional VM Deployment

### Server Requirements

- Ubuntu 22.04 LTS or RHEL 9
- 4GB RAM, 2 vCPU
- 20GB disk
- Python 3.11, Node.js 20

### Backend Setup

```bash
# Install dependencies
sudo apt update && sudo apt install -y python3.11-venv postgresql-client nginx

# Create user
sudo useradd -m -s /bin/bash digitaltwin
sudo su - digitaltwin

# Clone and setup
git clone https://github.com/your-org/digital-twin-simulator.git
cd digital-twin-simulator/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with production values

# Systemd service
sudo tee /etc/systemd/system/digital-twin-backend.service << EOF
[Unit]
Description=Digital Twin Backend
After=network.target postgresql.service

[Service]
Type=exec
User=digitaltwin
WorkingDirectory=/home/digitaltwin/digital-twin-simulator/backend
Environment=PATH=/home/digitaltwin/digital-twin-simulator/backend/.venv/bin
ExecStart=/home/digitaltwin/digital-twin-simulator/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable digital-twin-backend
sudo systemctl start digital-twin-backend
```

### Frontend Setup

```bash
# Build
cd digital-twin-simulator/frontend
npm install
npm run build

# Nginx config
sudo tee /etc/nginx/sites-available/digital-twin << EOF
server {
    listen 80;
    server_name digital-twin.your-domain.com;
    
    root /home/digitaltwin/digital-twin-simulator/frontend/dist;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_read_timeout 86400;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/digital-twin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d digital-twin.your-domain.com
```

---

## Database Setup

### PostgreSQL (Production)

```bash
# Install
sudo apt install postgresql-15 postgresql-client-15

# Configure
sudo -u postgres psql << EOF
CREATE DATABASE digital_twin;
CREATE USER digitaltwin WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE digital_twin TO digitaltwin;
ALTER USER digitaltwin CREATEDB;
EOF

# Run migrations
cd backend
alembic upgrade head
```

### Connection Pooling (PgBouncer)

```bash
sudo apt install pgbouncer
# Configure /etc/pgbouncer/pgbouncer.ini
# Point DATABASE_URL to pgbouncer:6432
```

---

## Monitoring & Observability

### Prometheus Metrics

Add to backend:
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge

WEBSOCKET_CONNECTIONS = Gauge('digital_twin_websocket_connections', 'Active WebSocket connections')
SIMULATION_UPDATES = Counter('digital_twin_simulation_updates_total', 'Total simulation updates')
ANOMALY_DETECTED = Counter('digital_twin_anomalies_total', 'Anomalies detected', ['type', 'severity'])
PREDICTION_LATENCY = Histogram('digital_twin_prediction_latency_seconds', 'Prediction latency')
```

### Grafana Dashboards

Key panels:
- Simulation update rate
- WebSocket connections
- Anomaly rate by type
- Prediction latency
- System health score
- Database size

### Log Aggregation

```yaml
# docker-compose logging
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

Ship to Elasticsearch/Loki/Datadog.

### Alerting Rules

```yaml
# Prometheus alerts
groups:
- name: digital-twin
  rules:
  - alert: SimulationStopped
    expr: digital_twin_simulation_running == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Digital twin simulation stopped"
      
  - alert: HighAnomalyRate
    expr: rate(digital_twin_anomalies_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High anomaly detection rate"
```

---

## Backup & Recovery

### Database Backup

```bash
# Daily backup
pg_dump -h localhost -U digitaltwin digital_twin | gzip > backup_$(date +%F).sql.gz

# Restore
gunzip -c backup_2024-01-15.sql.gz | psql -h localhost -U digitaltwin digital_twin
```

### Model Backup

```bash
# Backup ML models
tar -czf models_backup_$(date +%F).tar.gz backend/models/
```

### Disaster Recovery

1. Restore database from latest backup
2. Restore ML models
3. Restart services
4. Verify health endpoint

---

## Scaling Considerations

### Horizontal Scaling

- **Backend**: Multiple replicas with shared PostgreSQL
- **WebSocket**: Use Redis pub/sub for cross-instance messaging
- **Frontend**: Stateless, scale behind load balancer

### Vertical Scaling

- Increase CPU for simulation (10 Hz requires ~10% CPU)
- Increase memory for ML models (~100MB)
- Database: Scale based on retention needs

### Database Scaling

- Read replicas for historical queries
- TimescaleDB for time-series optimization
- Partition by time (monthly)

---

## Security Hardening

### Network

- Private networks for internal communication
- WAF for HTTP endpoints
- Rate limiting on API

### Application

- Non-root containers
- Read-only filesystem where possible
- Security headers (CSP, HSTS)
- Input validation on all endpoints

### Secrets

- Use Vault/Sealed Secrets for Kubernetes
- Rotate database passwords quarterly
- Audit CORS origins

---

## Rollout Strategy

### Blue-Green Deployment

```bash
# Deploy to green environment
docker compose -f docker-compose.green.yml up -d

# Health check
curl https://green.digital-twin.your-domain.com/api/health

# Switch traffic
# Update DNS or load balancer
```

### Canary Deployment

```yaml
# Kubernetes: 10% traffic to new version
spec:
  replicas: 10
  template:
    metadata:
      labels:
        version: v1.1.0
        canary: "true"
```

### Rollback

```bash
# Docker Compose
docker compose down
docker compose -f docker-compose.previous.yml up -d

# Kubernetes
kubectl rollout undo deployment/digital-twin-backend -n digital-twin
```

---

## Maintenance

### Scheduled Tasks

```bash
# Cron jobs
0 2 * * * /home/digitaltwin/backup.sh
0 3 * * 0 /home/digitaltwin/cleanup_old_data.sh
0 4 * * * /home/digitaltwin/retrain_models.sh
```

### Updates

```bash
# Pull latest
git pull origin main

# Backend
cd backend && pip install -r requirements.txt
systemctl restart digital-twin-backend

# Frontend
cd frontend && npm install && npm run build
systemctl reload nginx
```

### Database Maintenance

```bash
# Vacuum
psql -c "VACUUM ANALYZE;"

# Reindex
psql -c "REINDEX DATABASE digital_twin;"
```

---

## Troubleshooting Deployment

### Backend Won't Start

```bash
# Check logs
journalctl -u digital-twin-backend -f

# Common issues:
# - Database connection (check DATABASE_URL)
# - Port 8000 in use (check firewall)
# - Missing dependencies (pip install)
```

### Frontend Not Loading

```bash
# Check nginx
nginx -t
systemctl status nginx

# Check build
ls -la frontend/dist/

# Check browser console for errors
```

### WebSocket Fails

```bash
# Check proxy config
# Ensure WebSocket upgrade headers passed
# Check firewall allows WebSocket
```

### High Memory Usage

```bash
# Check simulation frequency
# Reduce LIVE_HISTORY_POINTS
# Check for memory leaks in Python
```

---

## Performance Tuning

### Backend

```env
# Increase for more responsive UI
WEBSOCKET_UPDATE_RATE=10

# Decrease for lower CPU
SIMULATION_FREQUENCY=5
```

### Database

```sql
-- Add indexes for common queries
CREATE INDEX idx_motor_states_timestamp ON motor_states(timestamp);
CREATE INDEX idx_motor_states_motor_id_timestamp ON motor_states(motor_id, timestamp);
```

### Nginx

```nginx
# Enable gzip
gzip on;
gzip_types text/plain application/json;

# Cache static assets
location ~* \.(js|css|png|jpg|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```