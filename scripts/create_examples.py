"""Скрипт для создания example_2.pdf и example_3.docx из example_1.txt."""

import html
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"
EXAMPLE_TXT = EXAMPLES_DIR / "example_1.txt"


def create_docx():
    """Создаёт example_3.docx из текста example_1.txt."""
    from docx import Document
    
    text = EXAMPLE_TXT.read_text(encoding="utf-8")
    doc = Document()
    for paragraph in text.split("\n"):
        doc.add_paragraph(paragraph)
    doc.save(EXAMPLES_DIR / "example_3.docx")
    print("Создан: examples/example_3.docx")


def create_pdf():
    """Создаёт example_2.pdf из текста example_1.txt через WeasyPrint."""
    from weasyprint import HTML
    
    text = EXAMPLE_TXT.read_text(encoding="utf-8")
    html_content = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"></head>
    <body style="font-family: sans-serif; padding: 2cm;">
        <pre style="white-space: pre-wrap;">{html.escape(text)}</pre>
    </body></html>
    """
    output_path = EXAMPLES_DIR / "example_2.pdf"
    HTML(string=html_content).write_pdf(str(output_path))
    print("Создан: examples/example_2.pdf")


if __name__ == "__main__":
    if not EXAMPLE_TXT.exists():
        print("Файл examples/example_1.txt не найден")
        sys.exit(1)
    
    create_docx()
    create_pdf()
    print("Готово!")
