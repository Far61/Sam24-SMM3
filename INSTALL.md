# Установка SAM-24 SMM на Linux

## Предварительные требования

1. Установите необходимые пакеты:
```bash
sudo apt update
sudo apt install python3-venv python3-pip redis-server nginx
```

2. Создайте директорию для приложения:
```bash
sudo mkdir -p /var/www/sam24smm
sudo chown www-data:www-data /var/www/sam24smm
```

## Установка приложения

1. Клонируйте репозиторий:
```bash
cd /var/www/sam24smm
sudo -u www-data git clone [URL] .
```

2. Создайте и активируйте виртуальное окружение:
```bash
sudo -u www-data python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте необходимые директории и установите права:
```bash
sudo -u www-data mkdir -p app/static/generated
sudo -u www-data mkdir -p instance
sudo -u www-data mkdir -p logs
sudo chmod 755 app/static/generated instance logs
```

## Настройка systemd сервисов

1. Скопируйте файлы сервисов:
```bash
sudo cp sam24smm.service /etc/systemd/system/
sudo cp sam24smm-celery.service /etc/systemd/system/
```

2. Перезагрузите systemd и включите сервисы:
```bash
sudo systemctl daemon-reload
sudo systemctl enable redis-server
sudo systemctl enable sam24smm
sudo systemctl enable sam24smm-celery
```

3. Запустите сервисы:
```bash
sudo systemctl start redis-server
sudo systemctl start sam24smm
sudo systemctl start sam24smm-celery
```

## Настройка Nginx

1. Создайте конфигурацию Nginx:
```bash
sudo nano /etc/nginx/sites-available/sam24smm
```

2. Добавьте следующую конфигурацию:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;  # Увеличенный таймаут
    }

    location /static/ {
        alias /var/www/sam24smm/app/static/;
    }
}
```

3. Активируйте сайт:
```bash
sudo ln -s /etc/nginx/sites-available/sam24smm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Проверка работоспособности

1. Проверьте статус сервисов:
```bash
sudo systemctl status redis-server
sudo systemctl status sam24smm
sudo systemctl status sam24smm-celery
```

2. Проверьте логи:
```bash
tail -f /var/www/sam24smm/logs/access.log
tail -f /var/www/sam24smm/logs/error.log
tail -f /var/www/sam24smm/logs/celery.log
```

## Обновление приложения

1. Остановите сервисы:
```bash
sudo systemctl stop sam24smm sam24smm-celery
```

2. Обновите код:
```bash
cd /var/www/sam24smm
sudo -u www-data git pull
```

3. Обновите зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Запустите сервисы:
```bash
sudo systemctl start sam24smm sam24smm-celery
```

## Устранение неполадок

1. Если возникают проблемы с правами доступа:
```bash
sudo chown -R www-data:www-data /var/www/sam24smm
sudo chmod -R 755 /var/www/sam24smm
```

2. Если Redis не запускается:
```bash
sudo systemctl status redis-server
sudo journalctl -u redis-server
```

3. Если Celery не запускается:
```bash
sudo systemctl status sam24smm-celery
sudo journalctl -u sam24smm-celery
``` 