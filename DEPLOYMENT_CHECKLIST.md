# ⚡ Быстрый чеклист развертывания

## 🎯 Будет ли работать так же, как локально?

**ДА!** Приложение будет работать идентично, но с улучшениями:

### ✅ Что работает одинаково:
- Все API эндпоинты
- Авторизация и регистрация
- Прохождение тестов
- Подсчет результатов
- Административная панель
- Celery задачи
- Кэширование Redis
- База данных PostgreSQL

### 🚀 Что работает ЛУЧШЕ на сервере:
- **HTTPS** вместо HTTP (безопасность)
- **Production build** frontend (быстрее)
- **Nginx кэширование** статики
- **Оптимизированные Docker образы**
- **Автозапуск** при перезагрузке сервера
- **Логирование** в файлы

### ⚠️ Что нужно изменить:

| Параметр | Локально | Production |
|----------|----------|------------|
| URL | http://localhost | https://yourdomain.com |
| DEBUG | true | false |
| SECRET_KEY | простой | сгенерированный |
| POSTGRES_PASSWORD | простой | сложный |
| CORS_ORIGINS | localhost:3000 | yourdomain.com |
| SSL | нет | обязателен |

## 📋 Минимальный чеклист (10 шагов)

```bash
# 1. Установите Docker
curl -fsSL https://get.docker.com | sh

# 2. Клонируйте проект
git clone <repo> /opt/apps/IT-Navigator
cd /opt/apps/IT-Navigator

# 3. Создайте .env.prod
nano .env.prod
# Скопируйте из DEPLOYMENT_GUIDE.md и измените пароли

# 4. Получите SSL сертификаты
sudo certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/*.pem nginx/ssl/

# 5. Обновите nginx/nginx.prod.conf
nano nginx/nginx.prod.conf
# Замените server_name на ваш домен

# 6. Запустите
docker-compose -f docker-compose.prod.yml up -d --build

# 7. Примените миграции
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 8. Создайте админа
docker-compose -f docker-compose.prod.yml exec backend python3 -c "
from app.db.session import SessionLocal
from app.db.models.user import User
from app.core.security import get_password_hash
db = SessionLocal()
admin = User(
    email='admin@yourdomain.com',
    hashed_password=get_password_hash('CHANGE_PASSWORD'),
    full_name='Admin',
    is_active=True,
    is_admin=True
)
db.add(admin)
db.commit()
"

# 9. Откройте порты
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 10. Проверьте
curl https://yourdomain.com/health
```

## 🔍 Быстрая проверка работоспособности

```bash
# Все контейнеры запущены?
docker-compose -f docker-compose.prod.yml ps
# Должно быть 7 контейнеров "Up"

# Backend отвечает?
curl -k https://yourdomain.com/api/v1/
# {"message":"Career Platform API",...}

# Frontend загружается?
curl -I https://yourdomain.com/
# HTTP/2 200

# База данных работает?
docker-compose -f docker-compose.prod.yml exec db psql -U career_user -d career_platform -c "SELECT 1;"
# 1

# Redis работает?
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
# PONG

# Celery работает?
docker-compose -f docker-compose.prod.yml logs celery_worker | grep "ready"
# celery@... ready.
```

## 🐛 Быстрое решение проблем

### Контейнер не запускается
```bash
docker-compose -f docker-compose.prod.yml logs <service_name>
docker-compose -f docker-compose.prod.yml restart <service_name>
```

### 502 Bad Gateway
```bash
# Проверьте backend
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml restart backend nginx
```

### CORS ошибки
```bash
# Проверьте CORS_ORIGINS в .env.prod
grep CORS_ORIGINS .env.prod
# Должно быть: CORS_ORIGINS=["https://yourdomain.com"]

docker-compose -f docker-compose.prod.yml restart backend
```

### База данных не подключается
```bash
# Проверьте пароль в .env.prod
grep POSTGRES_PASSWORD .env.prod

# Пересоздайте БД (ВНИМАНИЕ: удалит данные!)
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

## 💾 Быстрый бэкап

```bash
# Бэкап БД
docker exec it-navigator-db-1 pg_dump -U career_user career_platform | gzip > backup_$(date +%Y%m%d).sql.gz

# Восстановление
gunzip < backup_20260520.sql.gz | docker exec -i it-navigator-db-1 psql -U career_user career_platform
```

## 🔄 Быстрое обновление

```bash
cd /opt/apps/IT-Navigator

# Бэкап
docker exec it-navigator-db-1 pg_dump -U career_user career_platform | gzip > backup_before_update.sql.gz

# Обновление
git pull
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## 📊 Мониторинг одной командой

```bash
# Создайте скрипт
cat > /usr/local/bin/career-status <<'EOF'
#!/bin/bash
echo "=== Career Platform Status ==="
echo ""
echo "Containers:"
docker-compose -f /opt/apps/IT-Navigator/docker-compose.prod.yml ps
echo ""
echo "Disk usage:"
df -h | grep -E "Filesystem|/dev/sda"
echo ""
echo "Memory:"
free -h
echo ""
echo "Recent errors:"
docker-compose -f /opt/apps/IT-Navigator/docker-compose.prod.yml logs --tail=20 | grep -i error
EOF

chmod +x /usr/local/bin/career-status

# Используйте
career-status
```

## ✅ Финальный чеклист

После развертывания проверьте:

- [ ] https://yourdomain.com - открывается frontend
- [ ] https://yourdomain.com/docs - открывается Swagger
- [ ] https://yourdomain.com/admin - открывается админка
- [ ] Можно зарегистрироваться
- [ ] Можно войти
- [ ] Можно пройти тест (если есть вопросы)
- [ ] Flower доступен (http://server-ip:5555)
- [ ] SSL сертификат валиден (зеленый замок)
- [ ] Все 7 контейнеров "Up"
- [ ] Бэкапы настроены

## 🎉 Готово!

Если все пункты выше ✅ - приложение работает идентично локальной версии, но в production режиме.

---

**Полная инструкция**: см. `DEPLOYMENT_GUIDE.md`
