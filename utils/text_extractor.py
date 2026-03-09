"""Модуль извлечения текста из файлов разных форматов."""

import logging
from pathlib import Path

from pypdf import PdfReader

from utils.input_validator import validate_file_path

logger = logging.getLogger(__name__)


def extract_text_from_file(filepath: str) -> str:
    """
    Извлекает текст из файла (txt, docx, pdf).

    Args:
        filepath: Путь к файлу.

    Returns:
        Извлечённый текст.

    Raises:
        FileNotFoundError: Файл не найден.
        UnsupportedFormatError: Формат не поддерживается.
        EmptyInputError: Путь пустой.
    """
    path = validate_file_path(filepath)
    suffix = path.suffix.lower()
    logger.info("Извлечение текста из файла: %s (формат: %s)", filepath, suffix)
    
    if suffix == ".txt":
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        text = _extract_from_pdf(path)
    else:
        text = _extract_from_docx(path)

    logger.info("Текст извлечён: %d символов", len(text))
    return text


def _extract_from_pdf(path: Path) -> str:
    """Извлекает текст из PDF."""
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts)


def _extract_from_docx(path: Path) -> str:
    """Извлекает текст из DOCX."""
    from docx import Document
    
    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)
