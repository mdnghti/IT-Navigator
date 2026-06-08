# Deployment Guide

## Quick Start (VPS Deployment)

### Prerequisites
- Docker and Docker Compose installed
- PostgreSQL port 5432 available (or change in docker-compose.yml)
- Ports 80 and 8000 available

### Step 1: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd IT-Navigator

# Create backend .env file
cat > backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://career_user:career_password@db:5432/career_platform
POSTGRES_USER=career_user
POSTGRES_PASSWORD=career_password
POSTGRES_DB=career_platform
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=["http://localhost:3000","http://localhost","http://your-domain.com"]
DEBUG=false
EOF

# Create frontend .env.local file
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://your-domain.com/api/v1
EOF
```

### Step 2: Start Services

```bash
# Start all services
docker compose up -d

# Wait for database to be ready (about 10 seconds)
sleep 10

# Initialize database with all tests (self-contained, no external files needed)
docker compose exec backend python -m scripts.init_db

# Check logs
docker compose logs -f
```

### Step 3: Verify

- Frontend: http://your-domain.com
- Backend API: http://your-domain.com/api/v1/docs
- Admin Panel: http://your-domain.com/admin
  - Email: admin@example.com
  - Password: admin123

## Database Initialization

The `init_db.py` script is **completely self-contained** and includes:
- 7 IT specialties (F1-F7)
- 1 general test with 13 questions
- 7 specialized tests with 10 questions each
- Admin user

**No external files required!** All test data is hardcoded in the script.

## Production Considerations

### Security

1. **Change default passwords:**
   ```bash
   # Change admin password via admin panel after first login
   # Change database password in .env and docker-compose.yml
   ```

2. **Update SECRET_KEY:**
   ```bash
   # Generate new secret key
   openssl rand -hex 32
   # Update in backend/.env
   ```

3. **Configure CORS:**
   ```bash
   # Update CORS_ORIGINS in backend/.env with your actual domain
   CORS_ORIGINS=["https://your-domain.com"]
   ```

### SSL/HTTPS

Add SSL certificate to nginx configuration:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # ... rest of config
}
```

### Backup

```bash
# Backup database
docker compose exec db pg_dump -U career_user career_platform > backup.sql

# Restore database
docker compose exec -T db psql -U career_user career_platform < backup.sql
```

### Monitoring

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Check service status
docker compose ps

# Restart services
docker compose restart backend
docker compose restart frontend
```

## Updating

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker compose down
docker compose up -d --build

# If database schema changed, run migrations
docker compose exec backend alembic upgrade head
```

## Troubleshooting

### Tests not loading

```bash
# Clear Redis cache
docker compose exec redis redis-cli FLUSHALL

# Restart backend
docker compose restart backend
```

### Database issues

```bash
# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
sleep 10
docker compose exec backend python -m scripts.init_db
```

### Port conflicts

If ports 80, 8000, 5432, or 6379 are already in use, update `docker-compose.yml`:

```yaml
services:
  nginx:
    ports:
      - "8080:80"  # Change 80 to 8080
```

## Architecture

```
┌─────────────┐
│   Nginx     │ :80 (reverse proxy)
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
┌──────▼──────┐   ┌─────▼──────┐
│  Frontend   │   │  Backend   │ :8000
│  (Next.js)  │   │  (FastAPI) │
└─────────────┘   └──────┬─────┘
                         │
                    ┌────┴────┬────────┐
                    │         │        │
              ┌─────▼────┐ ┌──▼───┐ ┌─▼──────┐
              │PostgreSQL│ │Redis │ │ Celery │
              └──────────┘ └──────┘ └────────┘
```

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://user:pass@db:5432/dbname |
| SECRET_KEY | JWT signing key | (generate with openssl rand -hex 32) |
| ACCESS_TOKEN_EXPIRE_MINUTES | JWT token lifetime | 1440 (24 hours) |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| CORS_ORIGINS | Allowed origins for CORS | ["http://localhost:3000"] |
| DEBUG | Debug mode | false |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000/api/v1 |

## Support

For issues or questions, check:
- Backend logs: `docker compose logs backend`
- Frontend logs: `docker compose logs frontend`
- Database logs: `docker compose logs db`
