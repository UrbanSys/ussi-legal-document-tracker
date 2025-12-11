# Quick Reference Card

## 🚀 Local Development

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f backend

# Access API docs
http://localhost:8000/docs

# Health check
curl http://localhost:8000/health

# Connect to MSSQL
docker exec -it ussi-mssql sqlcmd -S localhost -U sa -P YourStrongPassword123!
```

---

## 🖥️ VM Deployment

```bash
# From your local machine (Linux/Mac)
bash backend/deploy.sh 192.168.1.100 ubuntu main

# From your local machine (Windows PowerShell)
.\backend\deploy.ps1 -VMIp "192.168.1.100" -VMUser "ubuntu"

# SSH into VM after deployment
ssh ubuntu@192.168.1.100
cd /opt/ussi-legal-document-tracker/backend

# View running containers
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop and start
docker-compose stop
docker-compose up -d
```

---

## 📝 Configuration

### Environment Variables (.env)

**Windows/Local MSSQL:**
```env
DATABASE_URL=mssql+pyodbc://?odbc_connect=Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=ussi_legal_tracker;Trusted_Connection=yes
```

**Docker with MSSQL Container:**
```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@mssql:1433/ussi_legal_tracker?driver=ODBC+Driver+17+for+SQL+Server
```

**Remote MSSQL Server:**
```env
DATABASE_URL=mssql+pyodbc://username:password@server.com/ussi_legal_tracker?driver=ODBC+Driver+17+for+SQL+Server
```

---

## 🔍 Debugging

```bash
# Test connection
docker exec ussi-backend python test_connection.py

# Run setup verification
docker exec ussi-backend python test_setup.py

# View system resources
docker stats

# Check network
docker network inspect ussi-network

# View volume details
docker volume inspect mssql_data

# Container logs (last 100 lines)
docker-compose logs --tail 100 backend
```

---

## 📦 Docker Commands

```bash
# Build
docker build -t ussi-backend:latest .

# List images
docker images | grep ussi

# List containers
docker ps -a | grep ussi

# Remove image
docker rmi ussi-backend:latest

# Clean up unused resources
docker system prune -a

# Check disk usage
docker system df

# View image layers
docker history ussi-backend:latest
```

---

## 🔄 Update & Redeploy

```bash
# Update code from git
git pull origin main

# Rebuild image (no cache)
docker-compose build --no-cache backend

# Restart service
docker-compose up -d backend

# Verify
curl http://localhost:8000/health
```

---

## 💾 Database Operations

```bash
# Backup database
docker exec ussi-mssql \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P password \
  -Q "BACKUP DATABASE ussi_legal_tracker TO DISK = '/var/opt/mssql/backup/db.bak'"

# Restore database
docker exec ussi-mssql \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P password \
  -Q "RESTORE DATABASE ussi_legal_tracker FROM DISK = '/var/opt/mssql/backup/db.bak'"

# Export database to CSV
docker exec ussi-mssql \
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P password \
  -Q "SELECT * FROM Project" -o output.csv
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change PORT in .env |
| MSSQL not responding | Wait 30-60 seconds, check logs |
| Database not found | Run database_schema.sql |
| Connection refused | Verify DATABASE_URL, check network |
| Out of disk space | `docker system prune -a` |
| Slow performance | Increase memory in docker-compose |

---

## 📊 Service Status

```bash
# All services
docker-compose ps

# Detailed status
docker-compose ps --format "table {{.Service}}\t{{.Status}}"

# Check health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

---

## 🔐 Security Checklist

- [ ] Change SA_PASSWORD in .env
- [ ] Use environment variables (not .env in production)
- [ ] Set up SSL/TLS with nginx
- [ ] Restrict database ports (not expose 1433 externally)
- [ ] Use strong passwords
- [ ] Regular backups
- [ ] Monitor logs and access
- [ ] Keep Docker and base images updated

---

## 📚 Documentation

- `DOCKER_GUIDE.md` — Full Docker reference
- `MSSQL_SETUP.md` — Database setup guide
- `README.md` — Backend overview
- `BACKEND_BUILD_SUMMARY.md` — Architecture summary
- `DOCKER_DEPLOYMENT_SUMMARY.md` — Deployment overview

---

## 🆘 Support URLs

- FastAPI: https://fastapi.tiangolo.com
- Docker: https://docs.docker.com
- MSSQL: https://hub.docker.com/_/microsoft-mssql-server
- PyODBC: https://github.com/mkleehammer/pyodbc/wiki

---

## ⏱️ Typical Timings

| Task | Time |
|------|------|
| Local build | 2-3 minutes |
| Start containers | 30-60 seconds |
| MSSQL ready | 30-40 seconds |
| Database init | 5-10 seconds |
| VM deployment | 3-5 minutes |
| API health check | < 1 second |

---

## 🎯 Next Commands to Run

```bash
# 1. Test local setup
cd backend
docker-compose up -d
sleep 30
curl http://localhost:8000/health

# 2. Deploy to VM
bash backend/deploy.sh 192.168.1.100 ubuntu main

# 3. Verify on VM
ssh ubuntu@192.168.1.100
docker-compose ps
docker-compose logs -f backend
```

---

**Last Updated:** December 4, 2025
**Version:** 1.0
