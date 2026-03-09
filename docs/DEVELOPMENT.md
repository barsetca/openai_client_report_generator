# Руководство для разработчиков

Документ для подключения новых разработчиков к проекту AI Client Report Generator.

## Требования

- **Python 3.10+**
- **Системные зависимости для WeasyPrint:**
  - Ubuntu/Debian: `libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev`
  - macOS: `brew install pango`

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo_url>
cd openai_client_report_generator

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить .env
cp .env.example .env
# Отредактировать .env: OPENAI_API_KEY, опционально TELEGRAM_BOT_TOKEN

# 5. Проверить запуск CLI
python3 main.py examples/example_1.txt 1

# 6. Запустить тесты
pytest
```

## Структура проекта

| Путь | Назначение |
|------|------------|
| `main.py` | CLI: интерактивный и неинтерактивный режимы |
| `tg_bot.py` | Telegram-бот (aiogram) |
| `utils/ai_processor.py` | Взаимодействие с OpenAI (диалоги, изображения) |
| `utils/pdf_generator.py` | Генерация PDF из HTML (Jinja2 + WeasyPrint) |
| `utils/text_extractor.py` | Извлечение текста из txt, pdf, docx |
| `utils/input_validator.py` | Валидация входных данных и типизированные ошибки |
| `utils/logger.py` | Настройка логирования |
| `templates/` | HTML-шаблоны отчётов |
| `examples/` | Тестовые файлы |
| `reports/` | Сгенерированные PDF (создаётся автоматически) |
| `tests/` | Тесты pytest |

## Тестирование

```bash
# Запуск всех тестов
pytest

# С покрытием
pytest --cov=utils --cov-report=term-missing

# Только тесты валидатора
pytest tests/test_input_validator.py -v

# Пропуск тестов, требующих example_2.pdf / example_3.docx
pytest -v  # они автоматически skip если файлов нет
```

Для создания `example_2.pdf` и `example_3.docx` перед тестами:
```bash
python3 scripts/create_examples.py
```

## Валидация входных данных

Модуль `utils/input_validator.py` обеспечивает явную обработку ошибок:

| Исключение | Когда возникает |
|------------|-----------------|
| `EmptyInputError` | Пустой текст, путь, название товара |
| `FileNotFoundError` | Файл не найден |
| `UnsupportedFormatError` | Неподдерживаемый формат (.csv, .xlsx и т.д.) |
| `InputLengthError` | Превышена максимальная длина текста/названия |

Использование в коде:
```python
from utils.input_validator import validate_transcription_text, InputValidationError

try:
    text = validate_transcription_text(user_input)
except InputValidationError as e:
    print(f"Ошибка: {e}")
```

## Логирование

- Уровень задаётся в `.env`: `LOG_LEVEL=DEBUG|INFO|WARNING|ERROR`
- По умолчанию: `INFO`
- Шумные библиотеки (fontTools, PIL) автоматически переводятся на WARNING при INFO

## Работа с OpenAI API

- Для тестов используются моки (`unittest.mock`) — реальные вызовы API не выполняются
- Токен хранится в `.env`, не коммитить в репозиторий
- Модели: `OPENAI_MODEL` (чат), `OPENAI_IMAGE_MODEL` (изображения)

## Добавление нового типа отчёта

1. Создать HTML-шаблон в `templates/`
2. Добавить функцию генерации в `utils/pdf_generator.py`
3. Добавить логику в `utils/ai_processor.py` (если нужен AI)
4. Обновить `REPORT_TYPES` в `main.py` и `tg_bot.py`
5. Добавить тесты в `tests/`

## Чек-лист перед коммитом

- [ ] `pytest` проходит
- [ ] `main.py examples/example_1.txt 1` создаёт PDF
- [ ] В `.gitignore` есть `.env`, `venv/`, `reports/`, `temp/`
