"""Тесты модуля валидации входных данных."""

import pytest
from pathlib import Path

from utils.input_validator import (
    validate_file_path,
    validate_transcription_text,
    validate_product_name,
    validate_product_price,
    validate_product_file_lines,
    InputValidationError,
    EmptyInputError,
    UnsupportedFormatError,
)


class TestValidateFilePath:
    """Тесты validate_file_path."""

    def test_valid_txt_file(self, example_1_txt: Path):
        result = validate_file_path(str(example_1_txt))
        assert result == example_1_txt.resolve()

    def test_valid_pdf_file(self, examples_dir: Path):
        pdf_path = examples_dir / "example_2.pdf"
        if pdf_path.exists():
            result = validate_file_path(str(pdf_path))
            assert result.suffix.lower() == ".pdf"

    def test_valid_docx_file(self, examples_dir: Path):
        docx_path = examples_dir / "example_3.docx"
        if docx_path.exists():
            result = validate_file_path(str(docx_path))
            assert result.suffix.lower() in (".docx", ".doc")

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Файл не найден"):
            validate_file_path("/nonexistent/file.txt")

    def test_empty_path(self):
        with pytest.raises(EmptyInputError, match="Путь к файлу не указан"):
            validate_file_path("")
        with pytest.raises(EmptyInputError):
            validate_file_path("   ")

    def test_unsupported_format(self, example_1_txt: Path):
        with pytest.raises(UnsupportedFormatError, match="Неподдерживаемый формат"):
            validate_file_path(str(example_1_txt).replace(".txt", ".xyz"))

    def test_relative_path_with_base(self, project_root: Path, example_1_txt: Path):
        rel = "examples/example_1.txt"
        result = validate_file_path(rel, base_path=project_root)
        assert result.exists()
        assert "example_1.txt" in str(result)


class TestValidateTranscriptionText:
    """Тесты validate_transcription_text."""

    def test_valid_text(self):
        text = "Клиент: Здравствуйте! Менеджер: Добрый день."
        assert validate_transcription_text(text) == text

    def test_strips_whitespace(self):
        assert validate_transcription_text("  hello  ") == "hello"

    def test_empty_raises(self):
        with pytest.raises(EmptyInputError, match="пустым"):
            validate_transcription_text("")
        with pytest.raises(EmptyInputError):
            validate_transcription_text("   ")

    def test_none_raises(self):
        with pytest.raises(EmptyInputError):
            validate_transcription_text(None)


class TestValidateProductName:
    """Тесты validate_product_name."""

    def test_valid_name(self):
        assert validate_product_name("Смартфон Samsung") == "Смартфон Samsung"

    def test_empty_raises(self):
        with pytest.raises(EmptyInputError):
            validate_product_name("")
        with pytest.raises(EmptyInputError):
            validate_product_name("   ")


class TestValidateProductPrice:
    """Тесты validate_product_price."""

    def test_valid_price(self):
        assert validate_product_price("24 990 ₽") == "24 990 ₽"

    def test_empty_raises(self):
        with pytest.raises(EmptyInputError):
            validate_product_price("")
        with pytest.raises(EmptyInputError):
            validate_product_price("   ")


class TestValidateProductFileLines:
    """Тесты validate_product_file_lines."""

    def test_valid_lines(self):
        name, price = validate_product_file_lines(["Товар", "100 ₽"])
        assert name == "Товар"
        assert price == "100 ₽"

    def test_single_line_name_only(self):
        name, price = validate_product_file_lines(["Товар"])
        assert name == "Товар"
        assert price == ""

    def test_empty_lines_raises(self):
        with pytest.raises(EmptyInputError):
            validate_product_file_lines([])

    def test_empty_name_raises(self):
        with pytest.raises(EmptyInputError):
            validate_product_file_lines(["", "100"])
