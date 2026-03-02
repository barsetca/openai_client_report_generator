"""Модуль извлечения текста из файлов разных форматов."""

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_file(filepath: str) -> str:
    """
    Извлекает текст из файла (txt, docx, pdf).
    
    Args:
        filepath: Путь к файлу.
        
    Returns:
        Извлечённый текст.
        
    Raises:
        ValueError: Если формат не поддерживается или файл не найден.
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {filepath}")
    
    suffix = path.suffix.lower()
    
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        return _extract_from_pdf(path)
    elif suffix in (".docx", ".doc"):
        return _extract_from_docx(path)
    else:
        raise ValueError(
            f"Неподдерживаемый формат: {suffix}. "
            "Используйте .txt, .pdf или .docx"
        )


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
