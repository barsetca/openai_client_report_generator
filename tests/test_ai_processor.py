"""Тесты модуля AI-обработки (с моками OpenAI)."""

import json
from unittest.mock import patch, MagicMock

import pytest

from utils.ai_processor import (
    process_dialog_with_ai,
    extract_design_prompt,
    get_product_card_data,
)
from utils.input_validator import EmptyInputError


@pytest.fixture
def mock_openai_client():
    """Мок OpenAI client."""
    with patch("utils.ai_processor.OpenAI") as mock_cls:
        client = MagicMock()
        mock_cls.return_value = client
        yield client


class TestProcessDialogWithAi:
    """Тесты process_dialog_with_ai."""

    def test_returns_structured_data(self, mock_openai_client):
        mock_openai_client.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "client_name": "Иван",
                            "topic": "Услуги",
                            "main_request": "Консультация",
                            "mood": "нейтральное",
                            "next_steps": ["Перезвонить"],
                            "desired_deadline": "Не указано",
                            "desired_cost": "Не указано",
                            "main_wishes": "Не указано",
                        })
                    )
                )
            ]
        )
        result = process_dialog_with_ai("Текст диалога")
        assert result["client_name"] == "Иван"
        assert result["topic"] == "Услуги"

    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="пустым"):
            process_dialog_with_ai("")
        with pytest.raises(ValueError):
            process_dialog_with_ai("   ")


class TestExtractDesignPrompt:
    """Тесты extract_design_prompt."""

    def test_returns_prompt(self, mock_openai_client):
        mock_openai_client.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(message=MagicMock(content="A modern minimalist website design"))
            ]
        )
        result = extract_design_prompt("Диалог о дизайне сайта")
        assert "modern" in result.lower() or "website" in result.lower()


class TestGetProductCardData:
    """Тесты get_product_card_data."""

    def test_returns_image_prompt_and_description(self, mock_openai_client):
        mock_openai_client.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "image_prompt": "Product photo on white background",
                            "description": "Качественный товар",
                        })
                    )
                )
            ]
        )
        result = get_product_card_data("Смартфон")
        assert "image_prompt" in result
        assert "description" in result
        assert "Product" in result["image_prompt"]
