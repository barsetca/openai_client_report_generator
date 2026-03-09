# AI Client Report Generator

Автоматическое формирование PDF-отчётов по транскрибации диалогов с клиентами с использованием ИИ и HTML-шаблонов.

**Документация для разработчиков:**
- [Руководство для разработчиков](docs/DEVELOPMENT.md) — подключение к проекту, тесты, структура
- [Развёртывание](docs/DEPLOYMENT.md) — Docker, systemd, production

## Возможности

- Загрузка транскрибации из файлов: **txt**, **pdf**, **docx**
- Два типа отчётов:
  - **Отчёт по диалогу** — сроки, стоимость, пожелания, следующие шаги
  - **Отчёт по заказу дизайна сайта** — то же + пример изображения макета
- Возможность генерации карточки товара
  - **Карточка товара для маркетплейса** — изображение товара (фон) + название, цена, описание
- Обработка через OpenAI (GPT) для извлечения структурированных данных
- Осуществление генерация (PDF-отчётов и карточки товара) по HTML-шаблонам


## Установка

```bash
# Клонируйте репозиторий и перейдите в папку проекта
cd openai_client_report_generator

# Создайте виртуальное окружение (рекомендуется)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или: venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env и укажите свой OPENAI_API_KEY
```

## Настройка .env

Создайте файл `.env` в корне проекта (скопируйте из `.env.example`):

```
OPENAI_API_KEY=sk-ваш-ключ-openai
OPENAI_MODEL=gpt-4.1
OPENAI_IMAGE_MODEL=gpt-image-1-mini
TELEGRAM_BOT_TOKEN=ваш-токен-от-@BotFather
# Уровень логирования: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO
# Диагностика: сохранять изображения дизайна в папку temp/
SAVE_DESIGN_IMAGES_TO_TEMP=false
```

| Переменная | Обязательная | Описание |
|------------|--------------|----------|
| `OPENAI_API_KEY` | Да | API-ключ OpenAI |
| `OPENAI_MODEL` | Нет | Модель для анализа текста (по умолчанию `gpt-4.1`) |
| `OPENAI_IMAGE_MODEL` | Нет | Модель генерации изображений (по умолчанию `gpt-image-1-mini`) |
| `TELEGRAM_BOT_TOKEN` | Для бота | Токен бота от @BotFather (для `tg_bot.py`) |
| `LOG_LEVEL` | Нет | Уровень логирования (см. ниже) |
| `SAVE_DESIGN_IMAGES_TO_TEMP` | Нет | При `true` сохранять PNG изображения дизайна в `temp/` для диагностики |

### Логирование

Переменная `LOG_LEVEL` управляет детализацией логов в консоль и может принимать значения:

- **DEBUG** — полная отладка (включая внутренние сообщения зависимостей)
- **INFO** — основные операции: загрузка файлов, вызовы API, создание отчётов, запрос на генерацию дизайна сайта
- **WARNING** — предупреждения
- **ERROR** — только ошибки

При `LOG_LEVEL=INFO` шумные библиотеки (fontTools, PIL и др.) автоматически переключаются на WARNING, чтобы не засорять вывод.

Для диагностики проблем с изображениями:
- Установите `LOG_LEVEL=INFO` — перед генерацией дизайна в лог выводится полный промпт, отправляемый модели
- Включите `SAVE_DESIGN_IMAGES_TO_TEMP=true` — PNG полученное от модели сохраняется в `temp/` для диагности проблем с формированием карточки товара в PDF

## Использование

**Интерактивный CLI режим** (при запуске без аргументов):
```bash
python3 main.py
```
Программа выведет краткую информацию, предложит выбрать тип отчёта, затем — ввести текст или путь к файлу.

**CLI Режим с аргументами** (для скриптов):
```bash
python3 main.py examples/example_1.txt        # отчёт по диалогу
python3 main.py examples/example_4.txt 2      # отчёт по дизайну
python3 main.py examples/example_product.txt 3  # карточка товара
```

**Telegram-бот** (весь функционал через кнопки):
```bash
# Добавьте TELEGRAM_BOT_TOKEN в .env
python3 tg_bot.py
```
Откройте бота в Telegram, нажмите /start и выберите тип отчёта.

## Структура проекта

```
project_root/
├── main.py                 # CLI
├── tg_bot.py               # Telegram-бот (aiogram)
├── Dockerfile              # Docker-образ
├── docker-compose.yml      # Оркестрация для бота
├── pytest.ini              # Настройки тестов
├── tests/                  # Тесты pytest
├── docs/
│   ├── DEVELOPMENT.md      # Руководство для разработчиков
│   └── DEPLOYMENT.md       # Развёртывание
├── templates/
│   ├── report_template.html
│   ├── report_design_template.html
│   └── report_product_card_template.html
├── reports/                # Готовые PDF-отчёты
├── utils/
│   ├── ai_processor.py     # Взаимодействие с OpenAI
│   ├── pdf_generator.py    # HTML → PDF
│   ├── text_extractor.py   # Извлечение текста из файлов
│   ├── input_validator.py  # Валидация входных данных
│   └── logger.py           # Логирование
├── examples/               # Примеры для тестирования
├── .env                    # API ключ и настройки
├── requirements.txt
└── README.md
```
## Зависимости

- **openai** — взаимодействие с OpenAI API
- **aiogram** — Telegram-бот
- **jinja2** — HTML-шаблоны
- **weasyprint** — генерация PDF из HTML
- **python-dotenv** — загрузка переменных из .env
- **python-docx** — чтение .docx
- **pypdf** — чтение .pdf


## Тестирование

```bash
pytest                    # Запуск тестов
pytest --cov=utils       # С отчётом покрытия
```

## Развёртывание

Docker-образ (по умолчанию запускает Telegram-бота):

```bash
docker build -t report-generator .
docker run -d --env-file .env report-generator
```

Подробнее: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)



## Примеры

В папке `examples/` находятся тестовые файлы:
- `example_1.txt` — диалог об услугах (тарифы, подключение)
- `example_4.txt` — диалог о заказе дизайна сайта (сроки, бюджет, пожелания)
- `example_2.pdf`, `example_3.docx` — альтернативные форматы

Для генерации `example_2.pdf` и `example_3.docx` из `example_1.txt` выполните:
```bash
python3 scripts/create_examples.py
```
В папке `reports/` находятся готовый pdf файлы после генерации.

В папке `screenshots/` находятся скриншоты работы бота.




