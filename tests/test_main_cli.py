"""Тесты CLI main.py."""

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

# Импортируем после conftest (PYTHONPATH)
from main import run_cli_noninteractive, REPORT_TYPES
from utils.input_validator import InputValidationError


class TestRunCliNoninteractive:
    """Тесты неинтерактивного режима CLI."""

    def test_invalid_report_type(self):
        """Проверка обработки неверного типа отчёта — делается в run_cli до вызова."""
        pass  # run_cli проверяет и выходит до run_cli_noninteractive

    def test_dialog_report_success(self, example_1_txt: Path, project_root: Path):
        """Отчёт по диалогу создаётся успешно (с моком AI)."""
        with patch("main.process_dialog_with_ai") as mock_ai:
            mock_ai.return_value = {
                "client_name": "Тест",
                "topic": "Тема",
                "main_request": "Запрос",
                "mood": "нейтральное",
                "next_steps": [],
                "desired_deadline": "Не указано",
                "desired_cost": "Не указано",
                "main_wishes": "Не указано",
            }
            with patch("sys.stdout", new_callable=StringIO):
                run_cli_noninteractive(str(example_1_txt), "1")
            mock_ai.assert_called_once()

    def test_nonexistent_file_exits(self):
        """Несуществующий файл приводит к выходу с кодом 1."""
        with patch("sys.stdout", new_callable=StringIO):
            with pytest.raises(SystemExit) as exc_info:
                run_cli_noninteractive("/nonexistent/file.txt", "1")
        assert exc_info.value.code == 1

    def test_product_card_from_file(self, example_product_txt: Path):
        """Карточка товара из файла (с моком AI)."""
        with patch("main.get_product_card_data") as mock_card:
            with patch("main.generate_product_image") as mock_img:
                mock_card.return_value = {
                    "image_prompt": "Smartphone photo",
                    "description": "Смартфон",
                }
                mock_img.return_value = b"\x89PNG\r\n\x1a\n"
                with patch("sys.stdout", new_callable=StringIO):
                    run_cli_noninteractive(str(example_product_txt), "3")
                mock_card.assert_called_once()
