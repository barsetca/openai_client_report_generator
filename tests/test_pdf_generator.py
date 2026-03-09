"""Тесты модуля генерации PDF."""

import pytest
from pathlib import Path

from utils.pdf_generator import (
    generate_pdf_report,
    generate_pdf_design_report,
    generate_pdf_product_card,
)

# Минимальный PNG 1x1 пиксель (валидный) для тестов
MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestGeneratePdfReport:
    """Тесты generate_pdf_report."""

    def test_generates_report(self, sample_dialog_data: dict):
        path = generate_pdf_report(sample_dialog_data)
        assert Path(path).exists()
        assert path.endswith(".pdf")
        Path(path).unlink(missing_ok=True)


class TestGeneratePdfDesignReport:
    """Тесты generate_pdf_design_report."""

    def test_generates_design_report(self, sample_dialog_data: dict):
        path = generate_pdf_design_report(sample_dialog_data, MINIMAL_PNG)
        assert Path(path).exists()
        assert "design" in Path(path).name
        Path(path).unlink(missing_ok=True)


class TestGeneratePdfProductCard:
    """Тесты generate_pdf_product_card."""

    def test_generates_product_card(self):
        path = generate_pdf_product_card(
            product_name="Тестовый товар",
            product_price="999 ₽",
            product_description="Описание для теста",
            product_image_bytes=MINIMAL_PNG,
        )
        assert Path(path).exists()
        assert "product_card" in Path(path).name
        Path(path).unlink(missing_ok=True)
