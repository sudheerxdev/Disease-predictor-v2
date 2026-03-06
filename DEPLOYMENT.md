# Production Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker & Docker Compose (for containerized deployment)
- PostgreSQL 12+ (for production database)
- Redis 6+ (for caching)
- Python 3.11+ (for direct installation)
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- SSL certificate (Let's Encrypt recommended)

---

## Environment Setup

### 1. Copy and Configure Environment Variables
```bash
cp .env.example .env
```

### 2. Edit `.env` with Production Values
```bash
# Must change these in production
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@db-host:5432/disease_db
GEMINI_API_KEY=your-api-key-here
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Database Configuration

### PostgreSQL Setup
```bash
# Create database and user
psql -U postgres
CREATE USER disease_user WITH PASSWORD 'secure_password';
CREATE DATABASE disease_db OWNER disease_user;
GRANT ALL PRIVILEGES ON DATABASE disease_db TO disease_user;
\q
```

### Database Migration
```bash
flask db upgrade
```

### Initialize Database
```bash
python -c "from backend import create_app, db; app = create_app(); db.create_all()"
```

---

## Docker Deployment

### Quick Start with Docker Compose
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Use production-specific compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec web flask db upgrade

# Create admin user
docker-compose exec web python -c "from backend.models.user import User; ..."
```

---

## Kubernetes Deployment

### Prerequisites
- kubectl configured
- Kubernetes cluster running
- Container registry access (Docker Hub, ECR, GCR)

### Push Docker Image
```bash
docker tag disease-predictor:latest your-registry/disease-predictor:latest
docker push your-registry/disease-predictor:latest
```

### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace disease-predictor

# Create secrets
kubectl create secret generic disease-secrets \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=GEMINI_API_KEY='your-api-key' \
  -n disease-predictor

# Apply manifests
kubectl apply -f k8s/ -n disease-predictor

# Check deployment
kubectl get pods -n disease-predictor
kubectl logs -n disease-predictor <pod-name>
```

---

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Request certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Certificate location
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Update Nginx Configuration
Uncomment the HTTPS server block in `nginx.conf` and update paths:
```nginx
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

### Enable Redirect HTTP → HTTPS
Uncomment the HTTP redirect in `nginx.conf`

---

## Monitoring & Logging

### Application Logs
```bash
# Docker
docker-compose logs -f web

# Kubernetes
kubectl logs -f deployment/disease-predictor -n disease-predictor

# File-based
tail -f logs/disease_predictor.log
```

### Health Checks
```bash
# Check application health
curl http://localhost:5000/health

# With SSL
curl https://yourdomain.com/health
```

### Performance Monitoring
- Enable Sentry for error tracking (update SENTRY_DSN in .env)
- Use CloudWatch, DataDog, or New Relic for metrics
- Monitor database with pgAdmin or DBeaver

---

## Backup & Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump disease_db > backup_$(date +%Y%m%d).sql

# With Docker
docker-compose exec db pg_dump -U disease_user disease_db > backup.sql
```

### Restore from Backup
```bash
# PostgreSQL restore
psql disease_db < backup.sql

# With Docker
docker-compose exec -T db psql -U disease_user disease_db < backup.sql
```

### Automated Backups
```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * pg_dump disease_db > /backups/disease_$(date +\%Y\%m\%d).sql
```

---

## Performance Optimization

### Database Optimization
```bash
# Analyze and vacuum
VACUUM ANALYZE;

# Create indices
CREATE INDEX idx_predictions_user_id ON prediction_history(user_id);
CREATE INDEX idx_predictions_created_at ON prediction_history(created_at);
```

### Caching Configuration
- Redis is configured in docker-compose.yml
- Flask-Caching is installed for view caching
- API responses are cached for 5 minutes by default

### Static File Optimization
- CSS/JS are gzipped by Nginx
- Static files are cached for 30 days
- Use CDN for global distribution

---

## Security Hardening

- [x] HTTPS/TLS enabled
- [x] CSRF protection enabled
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] XSS protection enabled
- [x] Rate limiting enabled
- [x] Security headers configured
- [x] Non-root Docker user
- [x] Database password not in code
- [x] API key not in code
- [x] Input validation enabled
- [x] CORS configured
- [x] Session security enabled

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Rebuild without cache
docker-compose build --no-cache

# Check port availability
lsof -i :5000
```

### Database Connection Issues
```bash
# Test connection
psql -h localhost -U disease_user -d disease_db

# Check environment variables
docker-compose exec web env | grep DATABASE

# Verify database is running
docker-compose logs db
```

### High Memory Usage
```bash
# Check memory consumption
docker stats

# Reduce worker count in gunicorn
# Modify docker-compose.yml CMD
CMD ["gunicorn", "--workers=2", ...]
```

### SSL Certificate Issues
```bash
# Test SSL
curl -v https://yourdomain.com

# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -noout -dates

# Renew certificate
sudo certbot renew --dry-run
```

---

## Support & Maintenance

- Regular security updates: `pip install --upgrade -r requirements.txt`
- Monitor logs for errors
- Regular backups (daily recommended)
- Test disaster recovery procedures
- Keep dependencies updated

For issues, refer to the main README.md or create an issue on GitHub.
