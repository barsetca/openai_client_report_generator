# AI Client Report Generator

Автоматическое формирование PDF-отчётов по диалогам с клиентами с использованием ИИ и HTML-шаблонов.

## Возможности

- Загрузка транскрибации из файлов: **txt**, **pdf**, **docx**
- Три типа отчётов:
  - **Отчёт по диалогу** — сроки, стоимость, пожелания, следующие шаги
  - **Отчёт по заказу дизайна сайта** — то же + пример изображения макета
  - **Карточка товара для маркетплейса** — изображение товара (фон) + название, цена, описание
- Обработка через OpenAI (GPT) для извлечения структурированных данных
- Генерация PDF-отчётов по HTML-шаблону

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

Создайте файл `.env` в корне проекта:

```
OPENAI_API_KEY=sk-ваш-ключ-openai
OPENAI_MODEL=gpt-4.1
OPENAI_IMAGE_MODEL=dall-e-3
```

- `OPENAI_API_KEY` — обязательный API-ключ OpenAI
- `OPENAI_MODEL` — модель для анализа текста (по умолчанию gpt-4.1)
- `OPENAI_IMAGE_MODEL` — модель для генерации изображений (по умолчанию gpt-image-1-mini)
- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather (для tg_bot.py)

## Использование

**Интерактивный режим** (при запуске без аргументов):
```bash
python3 main.py
```
Программа выведет краткую информацию, предложит выбрать тип отчёта, затем — ввести текст или путь к файлу.

**Режим с аргументами** (для скриптов):
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
├── templates/
│   ├── report_template.html      # Шаблон отчёта по диалогу
│   └── report_design_template.html  # Шаблон отчёта по дизайну
├── reports/                # Готовые PDF-отчёты
├── utils/
│   ├── ai_processor.py     # Взаимодействие с OpenAI
│   ├── pdf_generator.py    # HTML → PDF
│   └── text_extractor.py   # Извлечение текста из файлов
├── examples/               # Примеры для тестирования
│   ├── example_1.txt       # Диалог об услугах
│   ├── example_4.txt       # Диалог о заказе дизайна (сроки, бюджет)
│   ├── example_product.txt  # Карточка товара (название, цена)
│   ├── example_2.pdf
│   └── example_3.docx
├── .env                    # API ключ и настройки
├── requirements.txt
└── README.md
```

## Примеры

В папке `examples/` находятся тестовые файлы:
- `example_1.txt` — диалог об услугах (тарифы, подключение)
- `example_4.txt` — диалог о заказе дизайна сайта (сроки, бюджет, пожелания)
- `example_2.pdf`, `example_3.docx` — альтернативные форматы

Для генерации `example_2.pdf` и `example_3.docx` из `example_1.txt` выполните:
```bash
python3 scripts/create_examples.py
```

## Зависимости

- **openai** — взаимодействие с OpenAI API
- **aiogram** — Telegram-бот
- **jinja2** — HTML-шаблоны
- **weasyprint** — генерация PDF из HTML
- **python-dotenv** — загрузка переменных из .env
- **python-docx** — чтение .docx
- **pypdf** — чтение .pdf
