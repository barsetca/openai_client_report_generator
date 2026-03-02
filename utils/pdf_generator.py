"""Модуль генерации PDF из HTML-шаблона через Jinja2 и WeasyPrint."""

import base64
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
REPORTS_DIR = PROJECT_ROOT / "reports"

DEFAULT_FIELDS = {
    "desired_deadline": "Не указано",
    "desired_cost": "Не указано",
    "main_wishes": "Не указано",
}


def _ensure_data_defaults(data: dict) -> dict:
    """Добавляет значения по умолчанию для полей, которые могли отсутствовать."""
    for key, default in DEFAULT_FIELDS.items():
        if key not in data or data[key] is None:
            data[key] = default
    return data


def generate_pdf_report(data: dict) -> str:
    """
    Подставляет данные в HTML-шаблон и конвертирует в PDF (отчёт по диалогу).
    
    Args:
        data: Словарь с полями client_name, topic, main_request, mood, next_steps,
              desired_deadline, desired_cost, main_wishes
        
    Returns:
        Путь к созданному PDF-файлу.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    data = _ensure_data_defaults(dict(data))
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report_template.html")
    report_datetime = datetime.now().strftime("%d.%m.%Y, %H:%M")
    
    html_content = template.render(report_datetime=report_datetime, **data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{timestamp}.pdf"
    output_path = REPORTS_DIR / filename
    
    html_doc = HTML(string=html_content, base_url=str(TEMPLATES_DIR))
    html_doc.write_pdf(str(output_path))
    
    return str(output_path)


def generate_pdf_design_report(data: dict, design_image_bytes: bytes) -> str:
    """
    Генерирует PDF-отчёт по заказу дизайна с примером изображения.
    
    Args:
        data: Словарь с полями (аналогично generate_pdf_report)
        design_image_bytes: PNG-изображение в виде байтов
        
    Returns:
        Путь к созданному PDF-файлу.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    data = _ensure_data_defaults(dict(data))
    data["design_image_base64"] = base64.b64encode(design_image_bytes).decode("ascii")
    
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report_design_template.html")
    report_datetime = datetime.now().strftime("%d.%m.%Y, %H:%M")
    
    html_content = template.render(report_datetime=report_datetime, **data)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_design_{timestamp}.pdf"
    output_path = REPORTS_DIR / filename
    
    html_doc = HTML(string=html_content, base_url=str(TEMPLATES_DIR))
    html_doc.write_pdf(str(output_path))
    
    return str(output_path)


def generate_pdf_product_card(
    product_name: str,
    product_price: str,
    product_description: str,
    product_image_bytes: bytes,
) -> str:
    """
    Генерирует PDF с карточкой товара для маркетплейса.
    Изображение — фон карточки, поверх — название, цена, описание.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report_product_card_template.html")
    
    html_content = template.render(
        product_name=product_name,
        product_price=product_price,
        product_description=product_description,
        product_image_base64=base64.b64encode(product_image_bytes).decode("ascii"),
    )
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"product_card_{timestamp}.pdf"
    output_path = REPORTS_DIR / filename
    
    html_doc = HTML(string=html_content, base_url=str(TEMPLATES_DIR))
    html_doc.write_pdf(str(output_path))
    
    return str(output_path)
