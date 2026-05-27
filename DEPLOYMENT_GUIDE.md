# 🚀 Инструкция по развертыванию на сервере

## Предварительные требования на сервере

### Минимальные системные требования
- **OS**: Ubuntu 22.04 LTS / Debian 11+ / CentOS 8+
- **RAM**: минимум 2GB, рекомендуется 4GB+
- **CPU**: 2+ cores
- **Disk**: минимум 20GB свободного места
- **Порты**: 80, 443 (открыты в firewall)

### Необходимое ПО

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установите Docker Compose
sudo apt install docker-compose-plugin -y

# Установите Git
sudo apt install git -y

# Перелогиньтесь для применения прав Docker
exit
# Войдите снова по SSH
```

## 📋 Пошаговое развертывание

### Шаг 1: Клонирование проекта

```bash
# Создайте директорию для проекта
mkdir -p /opt/apps
cd /opt/apps

# Клонируйте репозиторий (или загрузите архив)
git clone <your-repo-url> IT-Navigator
# ИЛИ загрузите через scp/sftp

cd IT-Navigator
```

### Шаг 2: Настройка переменных окружения

#### Production .env для backend

```bash
# Создайте .env.prod в корне проекта
nano .env.prod
```

Содержимое `.env.prod`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://career_user:STRONG_PASSWORD_HERE@db:5432/career_platform
POSTGRES_USER=career_user
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
POSTGRES_DB=career_platform

# Security - ОБЯЗАТЕЛЬНО СМЕНИТЕ!
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE_64_CHARS_MIN
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# Redis
REDIS_URL=redis://redis:6379/0

# CORS - укажите ваш домен
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# App
DEBUG=false
PROJECT_NAME=Career Platform API
API_V1_PREFIX=/api/v1
```

**Генерация SECRET_KEY:**

```bash
# Сгенерируйте безопасный ключ
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### Production .env для frontend

```bash
nano frontend/.env.production
```

Содержимое:

```env
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
```

### Шаг 3: SSL сертификаты

#### Вариант A: Let's Encrypt (рекомендуется)

```bash
# Установите certbot
sudo apt install certbot -y

# Получите сертификаты (замените yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Скопируйте сертификаты в проект
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R $USER:$USER nginx/ssl
```

#### Вариант B: Самоподписанный сертификат (только для тестирования)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=yourdomain.com"
```

### Шаг 4: Обновление Nginx конфигурации

```bash
nano nginx/nginx.prod.conf
```

Замените `server_name _;` на ваш домен:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

### Шаг 5: Сборка и запуск

```bash
# Создайте production Dockerfile для backend (если нет)
cat > backend/Dockerfile <<'EOF'
FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Копирование приложения
COPY . .

# Создание директории для media
RUN mkdir -p /app/media/reports

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Создайте production Dockerfile для frontend
cat > frontend/Dockerfile <<'EOF'
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
EOF

# Обновите frontend/next.config.js для standalone
cat > frontend/next.config.js <<'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
}

module.exports = nextConfig
EOF
```

### Шаг 6: Запуск production

```bash
# Остановите dev версию если запущена
docker-compose down

# Запустите production
docker-compose -f docker-compose.prod.yml up -d --build

# Проверьте статус
docker-compose -f docker-compose.prod.yml ps
```

### Шаг 7: Применение миграций БД

```bash
# Дождитесь запуска всех контейнеров (30-60 сек)
sleep 30

# Примените миграции
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Проверьте логи
docker-compose -f docker-compose.prod.yml logs backend
```

### Шаг 8: Создание первого админа

```bash
# Войдите в контейнер backend
docker-compose -f docker-compose.prod.yml exec backend bash

# Запустите Python shell
python3 -c "
from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@yourdomain.com',
    hashed_password=get_password_hash('CHANGE_THIS_PASSWORD'),
    full_name='Admin User',
    is_active=True,
    is_admin=True
)
db.add(admin)
db.commit()
print('Admin created!')
"

exit
```

### Шаг 9: Настройка автозапуска

```bash
# Создайте systemd service
sudo nano /etc/systemd/system/career-platform.service
```

Содержимое:

```ini
[Unit]
Description=Career Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/apps/IT-Navigator
ExecStart=/usr/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.prod.yml down
User=root

[Install]
WantedBy=multi-user.target
```

```bash
# Активируйте service
sudo systemctl daemon-reload
sudo systemctl enable career-platform
sudo systemctl start career-platform
```

### Шаг 10: Настройка firewall

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# Или firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🔍 Проверка работоспособности

### Проверка сервисов

```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Все должны быть "Up"
# db, redis, backend, celery_worker, frontend, nginx

# Проверка логов
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f celery_worker
```

### Проверка доступности

```bash
# Проверка backend API
curl -k https://yourdomain.com/api/v1/
# Должен вернуть: {"message":"Career Platform API",...}

# Проверка health endpoint
curl -k https://yourdomain.com/health
# Должен вернуть: {"status":"healthy"}

# Проверка frontend
curl -I https://yourdomain.com/
# Должен вернуть: HTTP/2 200
```

### Проверка в браузере

1. **Frontend**: https://yourdomain.com
2. **API Docs**: https://yourdomain.com/docs
3. **Admin Panel**: https://yourdomain.com/admin
4. **Flower**: http://yourdomain.com:5555 (или закройте порт и используйте SSH tunnel)

## ⚠️ Важные отличия от локальной разработки

### 1. **Порты**
- **Локально**: сервисы доступны напрямую (backend:8000, frontend:3000)
- **Production**: все через Nginx на портах 80/443

### 2. **HTTPS**
- **Локально**: HTTP (http://localhost)
- **Production**: HTTPS обязателен (https://yourdomain.com)
- **Важно**: обновите CORS_ORIGINS в .env.prod

### 3. **Переменные окружения**
- **Локально**: `backend/.env` с DEBUG=true
- **Production**: `.env.prod` с DEBUG=false и сильными паролями

### 4. **База данных**
- **Локально**: данные в Docker volume, можно пересоздавать
- **Production**: данные критичны, нужны бэкапы!

### 5. **Логи**
- **Локально**: выводятся в консоль
- **Production**: собираются Docker, нужен мониторинг

### 6. **Celery Worker**
- **Локально**: loglevel=info
- **Production**: loglevel=warning (меньше логов)

### 7. **Frontend build**
- **Локально**: dev server с hot reload
- **Production**: optimized production build

## 🔒 Безопасность

### Обязательные меры

```bash
# 1. Смените все пароли
# - POSTGRES_PASSWORD
# - SECRET_KEY
# - Admin password

# 2. Ограничьте доступ к Flower
# Добавьте в docker-compose.prod.yml:
# ports:
#   - "127.0.0.1:5555:5555"  # Только localhost

# 3. Настройте fail2ban для SSH
sudo apt install fail2ban -y
sudo systemctl enable fail2ban

# 4. Регулярно обновляйте систему
sudo apt update && sudo apt upgrade -y

# 5. Настройте автоматическое обновление SSL
sudo crontab -e
# Добавьте:
# 0 3 * * * certbot renew --quiet && docker-compose -f /opt/apps/IT-Navigator/docker-compose.prod.yml restart nginx
```

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f backend

# Последние 100 строк
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Место на диске
df -h
docker system df
```

### Flower (Celery мониторинг)

```bash
# Доступ через SSH tunnel (безопаснее)
ssh -L 5555:localhost:5555 user@yourdomain.com

# Затем откройте в браузере: http://localhost:5555
```

## 💾 Бэкапы

### Автоматический бэкап PostgreSQL

```bash
# Создайте скрипт бэкапа
sudo nano /opt/scripts/backup-db.sh
```

Содержимое:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="it-navigator-db-1"

mkdir -p $BACKUP_DIR

docker exec $CONTAINER pg_dump -U career_user career_platform | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Удалить бэкапы старше 7 дней
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

```bash
# Сделайте исполняемым
sudo chmod +x /opt/scripts/backup-db.sh

# Добавьте в cron (каждый день в 3:00)
sudo crontab -e
# Добавьте:
# 0 3 * * * /opt/scripts/backup-db.sh >> /var/log/db-backup.log 2>&1
```

### Восстановление из бэкапа

```bash
# Восстановить базу данных
gunzip < /opt/backups/postgres/backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i it-navigator-db-1 psql -U career_user career_platform
```

## 🔄 Обновление приложения

```bash
cd /opt/apps/IT-Navigator

# 1. Сделайте бэкап БД
/opt/scripts/backup-db.sh

# 2. Получите новый код
git pull origin main
# ИЛИ загрузите новые файлы

# 3. Пересоберите и перезапустите
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Примените новые миграции (если есть)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 5. Проверьте логи
docker-compose -f docker-compose.prod.yml logs -f
```

## 🐛 Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверьте логи
docker-compose -f docker-compose.prod.yml logs backend

# Проверьте конфигурацию
docker-compose -f docker-compose.prod.yml config

# Пересоздайте контейнер
docker-compose -f docker-compose.prod.yml up -d --force-recreate backend
```

### Проблема: 502 Bad Gateway

```bash
# Проверьте, что backend запущен
docker-compose -f docker-compose.prod.yml ps backend

# Проверьте логи nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Проверьте логи backend
docker-compose -f docker-compose.prod.yml logs backend
```

### Проблема: CORS ошибки

```bash
# Проверьте CORS_ORIGINS в .env.prod
# Должен содержать ваш домен с https://

# Перезапустите backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Проблема: Celery задачи не выполняются

```bash
# Проверьте Celery worker
docker-compose -f docker-compose.prod.yml logs celery_worker

# Проверьте Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
# Должен вернуть: PONG

# Перезапустите worker
docker-compose -f docker-compose.prod.yml restart celery_worker
```

## ✅ Чеклист перед запуском

- [ ] Сервер соответствует минимальным требованиям
- [ ] Docker и Docker Compose установлены
- [ ] Проект загружен на сервер
- [ ] `.env.prod` создан с сильными паролями
- [ ] `SECRET_KEY` сгенерирован и уникален
- [ ] SSL сертификаты получены и настроены
- [ ] `CORS_ORIGINS` содержит ваш домен
- [ ] Firewall настроен (порты 80, 443)
- [ ] DNS записи указывают на сервер
- [ ] Все контейнеры запущены (`docker-compose ps`)
- [ ] Миграции применены
- [ ] Админ пользователь создан
- [ ] Бэкапы настроены
- [ ] Мониторинг настроен

## 📞 Поддержка

Если что-то не работает:

1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs -f`
2. Проверьте статус: `docker-compose -f docker-compose.prod.yml ps`
3. Проверьте переменные окружения в `.env.prod`
4. Убедитесь, что все порты открыты в firewall
5. Проверьте DNS записи домена

---

**Важно**: После развертывания на сервере приложение будет работать **идентично** локальной версии, но с production оптимизациями (кэширование, сжатие, HTTPS, безопасность).
