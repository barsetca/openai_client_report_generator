"""
AI Client Report Generator — основной модуль.

Автоматически формирует PDF-отчёты по диалогам с клиентами
с использованием ИИ и HTML-шаблонов.
"""

import sys
from pathlib import Path

from utils.ai_processor import (
    process_dialog_with_ai,
    extract_design_prompt,
    generate_design_image,
    generate_product_image,
    get_product_card_data,
    OPENAI_MODEL,
    OPENAI_IMAGE_MODEL,
)
from utils.pdf_generator import (
    generate_pdf_report,
    generate_pdf_design_report,
    generate_pdf_product_card,
)
from utils.text_extractor import extract_text_from_file

PROJECT_ROOT = Path(__file__).resolve().parent

REPORT_TYPES = {
    "1": ("dialog", "Отчёт по диалогу с клиентом"),
    "2": ("design", "Отчёт по заказу дизайна сайта"),
    "3": ("product_card", "Карточка товара для маркетплейса"),
}


def show_intro():
    """Выводит информацию о программе и используемых моделях."""
    print()
    print("═" * 60)
    print("  AI Client Report Generator")
    print("  Автоматическое формирование PDF-отчётов по диалогам с клиентами")
    print("═" * 60)
    print()
    print("Используемые модели OpenAI:")
    print(f"  • Анализ текста: {OPENAI_MODEL}")
    print(f"  • Генерация изображений: {OPENAI_IMAGE_MODEL}")
    print()


def get_report_type() -> str:
    """Запрашивает выбор типа отчёта."""
    print("Выберите тип отчёта:")
    for key, (_, desc) in REPORT_TYPES.items():
        print(f"  {key} — {desc}")
    print()
    
    while True:
        choice = input("Введите номер (1, 2 или 3): ").strip()
        if choice in REPORT_TYPES:
            return choice
        print("Введите 1, 2 или 3.")


def get_product_input() -> tuple[str, str]:
    """
    Запрашивает название товара и стоимость для карточки.
    Можно ввести путь к файлу (первая строка — название, вторая — цена).
    """
    print()
    print("Введите название товара и стоимость.")
    print("Варианты: путь к файлу (txt) или ввод с клавиатуры")
    print()
    
    first_line = input("Название товара или путь к файлу: ").strip()
    
    # Проверяем, не путь ли к файлу
    if first_line:
        path = Path(first_line.strip().strip('"').strip("'"))
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.suffix.lower() == ".txt" and path.exists():
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").strip().split("\n")
                name = lines[0].strip() if lines else ""
                price = lines[1].strip() if len(lines) > 1 else ""
                if name:
                    return name, price
            except Exception as e:
                print(f"Ошибка чтения: {e}")
    
    name = first_line or input("Название товара: ").strip()
    price = input("Стоимость: ").strip()
    return name, price


def get_text_or_file() -> str:
    """
    Запрашивает текст транскрибации или путь к файлу.
    Определяет автоматически: если ввод похож на путь к файлу — читает файл.
    """
    print()
    print("Введите текст транскрибации или путь к файлу (txt, pdf, docx):")
    print("(Для текста: вставьте и нажмите Ctrl+D / Ctrl+Z+Enter)")
    print()
    
    first_line = input().strip()
    
    # Проверяем, не путь ли к файлу
    if first_line:
        path = Path(first_line.strip().strip('"').strip("'"))
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.suffix.lower() in (".txt", ".pdf", ".docx") and path.exists():
            try:
                return extract_text_from_file(str(path))
            except Exception as e:
                print(f"Ошибка чтения файла: {e}")
                print("Трактуем ввод как текст.")
    
    # Собираем текст до EOF (Ctrl+D / Ctrl+Z)
    lines = [first_line] if first_line else []
    while True:
        try:
            line = input()
        except EOFError:
            break
        lines.append(line)
    
    text = "\n".join(lines).strip()
    return text


def create_dialog_report(text: str) -> str:
    """Создаёт отчёт по диалогу."""
    data = process_dialog_with_ai(text)
    return generate_pdf_report(data)


def create_design_report(text: str) -> str:
    """Создаёт отчёт по заказу дизайна с примером изображения."""
    data = process_dialog_with_ai(text)
    prompt = extract_design_prompt(text)
    image_bytes = generate_design_image(prompt)
    return generate_pdf_design_report(data, image_bytes)


def create_product_card_report(product_name: str, product_price: str) -> str:
    """Создаёт карточку товара для маркетплейса."""
    card_data = get_product_card_data(product_name)
    image_bytes = generate_product_image(card_data["image_prompt"])
    return generate_pdf_product_card(
        product_name=product_name,
        product_price=product_price,
        product_description=card_data["description"],
        product_image_bytes=image_bytes,
    )


def run_cli_noninteractive(filepath: str, report_type: str):
    """Запуск с аргументами командной строки (для скриптов)."""
    _, report_name = REPORT_TYPES[report_type]
    
    try:
        if report_type == "3":
            # Файл: первая строка — название, вторая — цена
            lines = Path(filepath).read_text(encoding="utf-8", errors="replace").strip().split("\n")
            product_name = lines[0].strip() if lines else ""
            product_price = lines[1].strip() if len(lines) > 1 else ""
            if not product_name:
                print("Ошибка: укажите название товара в первой строке файла")
                sys.exit(1)
            pdf_path = create_product_card_report(product_name, product_price)
        else:
            text = extract_text_from_file(filepath)
            if not text.strip():
                print("Ошибка: текст не может быть пустым")
                sys.exit(1)
            if report_type == "1":
                pdf_path = create_dialog_report(text)
            else:
                pdf_path = create_design_report(text)
        
        rel_path = Path(pdf_path).relative_to(PROJECT_ROOT)
        print(f"{report_name} успешно создан: {rel_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


def run_cli():
    """Запуск в интерактивном режиме."""
    # Если переданы аргументы — неинтерактивный режим
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
        report_type = sys.argv[2] if len(sys.argv) > 2 else "1"
        if report_type not in REPORT_TYPES:
            print(f"Неизвестный тип отчёта: {report_type}. Допустимо: 1, 2, 3")
            sys.exit(1)
        run_cli_noninteractive(filepath, report_type)
        return
    
    show_intro()
    report_type = get_report_type()
    
    if report_type == "3":
        product_name, product_price = get_product_input()
        if not product_name.strip():
            print("Ошибка: название товара не может быть пустым.")
            sys.exit(1)
        text = None
    else:
        text = get_text_or_file()
        if not text.strip():
            print("Ошибка: текст не может быть пустым.")
            sys.exit(1)
        product_name, product_price = None, None
    
    _, report_name = REPORT_TYPES[report_type]
    print()
    print("Обработка...")
    
    try:
        if report_type == "1":
            pdf_path = create_dialog_report(text)
        elif report_type == "2":
            pdf_path = create_design_report(text)
        else:
            pdf_path = create_product_card_report(product_name, product_price)
        
        rel_path = Path(pdf_path).relative_to(PROJECT_ROOT)
        print()
        print(f"✓ {report_name} успешно создан: {rel_path}")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
