# Docker Build and Run Guide

## Prerequisites
- Docker installed (https://www.docker.com/products/docker-desktop)
- Docker Compose installed (comes with Docker Desktop)
- 2GB+ available disk space
- 2GB+ available RAM

---

## Quick Start (All-in-One with MSSQL)

### 1. Build and Run Everything
```bash
# From backend directory
cd backend

# Build the image
docker build -t ussi-backend:latest .

# Run with docker-compose (includes MSSQL)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 2. Access the Application
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 3. Verify Database
```bash
# Check MSSQL is running
docker-compose ps mssql

# Connect to database
docker exec -it ussi-mssql sqlcmd -S localhost -U sa -P YourStrongPassword123!

# In sqlcmd, verify database
> SELECT name FROM sys.databases;
> GO
```

---

## Development Workflow

### Using Docker for Development
```bash
# Start containers
docker-compose up -d

# Rebuild after code changes
docker-compose build --no-cache backend
docker-compose up -d backend

# View real-time logs
docker-compose logs -f backend

# Run tests inside container
docker exec ussi-backend python test_connection.py

# Stop containers
docker-compose down

# Stop and remove volumes (careful!)
docker-compose down -v
```

### Local MSSQL with Docker Backend
If you already have MSSQL running locally:

```bash
# Update .env to point to local MSSQL
DATABASE_URL=mssql+pyodbc://sa:password@host.docker.internal/ussi_legal_tracker?driver=ODBC+Driver+17+for+SQL+Server

# Run only the backend service
docker-compose up -d backend --no-deps
```

---

## Production Deployment on VM

### Step 1: Prepare VM
```bash
# SSH into VM
ssh user@your-vm-ip

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (optional, restart required)
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Deploy Application
```bash
# Clone or copy repository
git clone https://github.com/UrbanSys/ussi-legal-document-tracker.git
cd ussi-legal-document-tracker/backend

# Set environment variables for production
cat > .env << EOF
DATABASE_URL=mssql+pyodbc://sa:YourSecurePassword@your-mssql-server/ussi_legal_tracker?driver=ODBC+Driver+17+for+SQL+Server
HOST=0.0.0.0
PORT=8000
RELOAD=False
DEBUG=False
UPLOAD_DIRECTORY=/app/uploads
EOF

# Build and start
docker-compose up -d
```

### Step 3: Configure Reverse Proxy (Optional but Recommended)

#### Using Nginx
```bash
# Create nginx config
sudo cat > /etc/nginx/sites-available/ussi-backend << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ussi-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Using SSL with Let's Encrypt
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Docker Commands Reference

### Container Management
```bash
# Build image
docker build -t ussi-backend:latest .

# Run container
docker run -d -p 8000:8000 --name ussi-backend ussi-backend:latest

# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs -f ussi-backend

# Execute command in container
docker exec -it ussi-backend bash

# Stop container
docker stop ussi-backend

# Remove container
docker rm ussi-backend

# View images
docker images

# Remove image
docker rmi ussi-backend:latest
```

### Docker Compose
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild services
docker-compose build --no-cache

# Run one-off command
docker-compose exec backend python test_connection.py

# Scale services (if configured)
docker-compose up -d --scale backend=2
```

---

## Volumes and Data Persistence

### Uploaded Files
- Stored in: `/app/uploads` inside container
- Mounted from: `./uploads` on host
- Persists after container restart

### Database
- MSSQL data stored in named volume `mssql_data`
- Persists across container restarts
- View volumes: `docker volume ls`
- Inspect volume: `docker volume inspect mssql_data`

### Backup Database
```bash
# Dump MSSQL database
docker exec ussi-mssql \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P password \
  -Q "BACKUP DATABASE ussi_legal_tracker TO DISK = '/var/opt/mssql/backup/db.bak'"

# Copy backup to host
docker cp ussi-mssql:/var/opt/mssql/backup/db.bak ./database_backup.bak
```

---

## Network Configuration

### Docker Network
- Name: `ussi-network`
- Type: bridge
- Services communicate by service name:
  - Backend → `backend:8000`
  - MSSQL → `mssql:1433`

### Expose Ports
- Backend: `8000:8000` (host:container)
- MSSQL: `1433:1433` (host:container)

---

## Performance Tuning

### Resource Limits
```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Database Performance
```bash
# Increase MSSQL memory
docker exec ussi-mssql \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P password \
  -Q "EXEC sp_configure 'max server memory', 2048; RECONFIGURE;"
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port already in use: change PORT in .env
# 2. MSSQL not ready: wait 30 seconds
# 3. Bad credentials: verify DATABASE_URL
```

### Connection Refused
```bash
# Verify container is running
docker ps | grep ussi

# Check network
docker network inspect ussi-network

# Ping from backend to mssql
docker exec ussi-backend ping mssql
```

### Out of Disk Space
```bash
# Clean up unused images
docker image prune -a

# Clean up unused volumes
docker volume prune

# Check disk usage
docker system df
```

---

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to VM

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push image
        run: |
          docker build -t ussi-backend:latest backend/
          # Push to registry (Docker Hub, ECR, etc)
      - name: Deploy to VM
        run: |
          ssh user@vm-ip 'cd ussi-legal-document-tracker && docker-compose pull && docker-compose up -d'
```

---

## Monitoring

### Health Checks
```bash
# Manual health check
curl http://localhost:8000/health

# Docker health status
docker ps --filter health=healthy

# Logs for debugging
docker-compose logs --tail 100 backend
```

### Resource Monitoring
```bash
# CPU and memory usage
docker stats

# Container inspect
docker inspect ussi-backend
```

---

## Next Steps

1. ✅ Build Docker image locally: `docker build -t ussi-backend .`
2. ✅ Test with compose: `docker-compose up -d`
3. ✅ Verify services: `docker ps` and `curl http://localhost:8000/health`
4. ✅ Deploy to VM: Copy files and run `docker-compose up -d`
5. ✅ Set up monitoring and logging
6. ✅ Configure SSL/TLS for production

---

## Support & Resources

- Docker Docs: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose
- MSSQL in Docker: https://hub.docker.com/_/microsoft-mssql-server
- Nginx Proxy: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
