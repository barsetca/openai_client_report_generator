"""Фикстуры pytest для AI Client Report Generator."""

import os
import sys
from pathlib import Path

import pytest

# Добавляем корень проекта в PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Отключаем загрузку .env во время тестов (можно переопределить через monkeypatch)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-not-real")
os.environ.setdefault("LOG_LEVEL", "WARNING")


@pytest.fixture
def project_root() -> Path:
    """Корень проекта."""
    return PROJECT_ROOT


@pytest.fixture
def examples_dir(project_root: Path) -> Path:
    """Директория с примерами."""
    return project_root / "examples"


@pytest.fixture
def example_1_txt(examples_dir: Path) -> Path:
    """Путь к example_1.txt."""
    return examples_dir / "example_1.txt"


@pytest.fixture
def example_product_txt(examples_dir: Path) -> Path:
    """Путь к example_product.txt."""
    return examples_dir / "example_product.txt"


@pytest.fixture
def sample_dialog_data() -> dict:
    """Пример структурированных данных диалога из AI."""
    return {
        "client_name": "Сергей Петров",
        "topic": "Тарифный план",
        "main_request": "Уточнение условий тарифа Бизнес",
        "mood": "нейтральное",
        "next_steps": ["Подготовить коммерческое предложение"],
        "desired_deadline": "Не указано",
        "desired_cost": "Не указано",
        "main_wishes": "Не указано",
    }
