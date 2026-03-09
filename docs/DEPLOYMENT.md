# Руководство по развёртыванию

Подробная инструкция по развёртыванию AI Client Report Generator в различных средах.

## Содержание

1. [Локальный запуск](#локальный-запуск)
2. [Docker](#docker)
3. [Systemd (Linux-сервер)](#systemd-linux-сервер)
4. [Переменные окружения](#переменные-окружения)
5. [Рекомендации по production](#рекомендации-по-production)

---

## Локальный запуск

### CLI

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Заполнить OPENAI_API_KEY в .env

python3 main.py examples/example_1.txt 1
```

### Telegram-бот

```bash
# Добавить TELEGRAM_BOT_TOKEN в .env
python3 tg_bot.py
```

Бот работает в режиме long polling. Для production с высоким трафиком рекомендуется webhook (см. ниже).

---

## Docker

### Dockerfile

Создайте `Dockerfile` в корне проекта:

```dockerfile
FROM python:3.11-slim

# Системные зависимости для WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# По умолчанию — бот
CMD ["python3", "tg_bot.py"]
```

### Сборка и запуск

```bash
docker build -t report-generator .
docker run -d --name report-bot \
  -e OPENAI_API_KEY=sk-xxx \
  -e TELEGRAM_BOT_TOKEN=xxx \
  -e LOG_LEVEL=INFO \
  report-generator
```

С использованием `.env` файла:

```bash
docker run -d --name report-bot --env-file .env report-generator
```

### docker-compose

`docker-compose.yml`:

```yaml
version: "3.8"
services:
  report-bot:
    build: .
    env_file: .env
    restart: unless-stopped
    volumes:
      - ./reports:/app/reports
      - ./temp:/app/temp
```

Запуск: `docker-compose up -d`

---

## Systemd (Linux-сервер)

### Сервис для Telegram-бота

Файл `/etc/systemd/system/report-bot.service`:

```ini
[Unit]
Description=AI Client Report Generator Telegram Bot
After=network.target

[Service]
Type=simple
User=deploy
Group=deploy
WorkingDirectory=/opt/report-generator
Environment="PATH=/opt/report-generator/venv/bin"
ExecStart=/opt/report-generator/venv/bin/python3 tg_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Команды:

```bash
sudo systemctl daemon-reload
sudo systemctl enable report-bot
sudo systemctl start report-bot
sudo systemctl status report-bot
sudo journalctl -u report-bot -f
```

### Вариант с виртуальным окружением

```ini
ExecStart=/opt/report-generator/venv/bin/python3 /opt/report-generator/tg_bot.py
```

Переменные из `.env` можно подгрузить через:

```ini
EnvironmentFile=/opt/report-generator/.env
```

---

## Переменные окружения

| Переменная | Обязательная | По умолчанию | Описание |
|------------|--------------|--------------|----------|
| `OPENAI_API_KEY` | Да | — | API-ключ OpenAI |
| `OPENAI_MODEL` | Нет | gpt-4.1 | Модель для анализа текста |
| `OPENAI_IMAGE_MODEL` | Нет | gpt-image-1-mini | Модель генерации изображений |
| `TELEGRAM_BOT_TOKEN` | Для бота | — | Токен от @BotFather |
| `LOG_LEVEL` | Нет | INFO | DEBUG, INFO, WARNING, ERROR |
| `SAVE_DESIGN_IMAGES_TO_TEMP` | Нет | false | Сохранять PNG в temp/ для диагностики |

---

## Рекомендации по production

### Безопасность

- Никогда не коммитить `.env` в репозиторий
- Использовать секреты (Docker secrets, Vault, переменные CI/CD)
- Ограничить доступ к API-ключам по принципу наименьших привилегий

### Надёжность

- Использовать `restart: unless-stopped` / `Restart=always` для автоматического перезапуска
- Логировать в файл или централизованную систему (при `LOG_LEVEL=INFO` объём логов умеренный)
- Для бота при высоком RPS рассмотреть webhook вместо long polling

### Ресурсы

- WeasyPrint использует память для рендеринга PDF; при большом количестве параллельных запросов возможны пики
- Рекомендуемый минимум: 512 MB RAM для контейнера/процесса

### Мониторинг

- Проверять логи на ошибки OpenAI (rate limit, недоступность API)
- При `SAVE_DESIGN_IMAGES_TO_TEMP=true` можно контролировать качество генерации изображений

### Обновление

```bash
git pull
pip install -r requirements.txt --upgrade
# Перезапуск сервиса
sudo systemctl restart report-bot
# или
docker-compose pull && docker-compose up -d
```
