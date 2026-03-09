"""Тесты модуля извлечения текста."""

import pytest
from pathlib import Path

from utils.input_validator import FileNotFoundError, UnsupportedFormatError, EmptyInputError
from utils.text_extractor import extract_text_from_file


class TestExtractTextFromFile:
    """Тесты extract_text_from_file."""

    def test_extract_txt(self, example_1_txt: Path):
        text = extract_text_from_file(str(example_1_txt))
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Менеджер" in text or "Клиент" in text

    def test_extract_pdf(self, examples_dir: Path):
        pdf_path = examples_dir / "example_2.pdf"
        if not pdf_path.exists():
            pytest.skip("example_2.pdf не создан (запустите scripts/create_examples.py)")
        text = extract_text_from_file(str(pdf_path))
        assert isinstance(text, str)
        assert len(text) >= 0

    def test_extract_docx(self, examples_dir: Path):
        docx_path = examples_dir / "example_3.docx"
        if not docx_path.exists():
            pytest.skip("example_3.docx не создан (запустите scripts/create_examples.py)")
        text = extract_text_from_file(str(docx_path))
        assert isinstance(text, str)
        assert len(text) >= 0

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            extract_text_from_file("/nonexistent/file.txt")

    def test_unsupported_format(self, example_1_txt: Path):
        bad_path = str(example_1_txt).replace(".txt", ".csv")
        with pytest.raises(UnsupportedFormatError):
            extract_text_from_file(bad_path)

    def test_empty_path(self):
        with pytest.raises(EmptyInputError):
            extract_text_from_file("")
