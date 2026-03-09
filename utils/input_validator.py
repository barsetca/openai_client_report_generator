"""
Валидация входных данных и явная обработка ошибок.

Определяет пользовательские исключения и функции проверки
для входных файлов, текста и параметров.
"""

from pathlib import Path

# Поддерживаемые форматы
SUPPORTED_TEXT_FORMATS = (".txt", ".pdf", ".docx", ".doc")
SUPPORTED_PRODUCT_FILE_FORMAT = ".txt"

# Ограничения
MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 500_000
MIN_PRODUCT_NAME_LENGTH = 1
MAX_PRODUCT_NAME_LENGTH = 500


class InputValidationError(Exception):
    """Ошибка валидации входных данных."""
    pass


class FileNotFoundError(InputValidationError, FileNotFoundError):
    """Файл не найден."""
    pass


class UnsupportedFormatError(InputValidationError):
    """Неподдерживаемый формат файла."""
    pass


class EmptyInputError(InputValidationError):
    """Пустой входной данные."""
    pass


class InputLengthError(InputValidationError):
    """Превышена допустимая длина входных данных."""
    pass


def validate_file_path(
    filepath: str,
    allowed_formats: tuple[str, ...] = SUPPORTED_TEXT_FORMATS,
    must_exist: bool = True,
    base_path: Path | None = None,
) -> Path:
    """
    Проверяет путь к файлу.

    Args:
        filepath: Путь к файлу.
        allowed_formats: Допустимые расширения (например, (.txt, .pdf, .docx)).
        must_exist: Файл должен существовать.
        base_path: Базовая директория для относительных путей (по умолчанию — текущая).

    Returns:
        Объект Path при успешной валидации.

    Raises:
        EmptyInputError: Путь пустой.
        FileNotFoundError: Файл не найден.
        UnsupportedFormatError: Формат не поддерживается.
    """
    if not filepath or not str(filepath).strip():
        raise EmptyInputError("Путь к файлу не указан")

    path = Path(filepath)
    if not path.is_absolute() and base_path is not None:
        path = base_path / path
    path = path.resolve()
    suffix = path.suffix.lower()

    if suffix not in allowed_formats:
        formats_str = ", ".join(allowed_formats)
        raise UnsupportedFormatError(
            f"Неподдерживаемый формат: {suffix or '(без расширения)'}. "
            f"Допустимые форматы: {formats_str}"
        )

    if must_exist and not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")

    return path


def validate_transcription_text(text: str) -> str:
    """
    Проверяет текст транскрибации.

    Args:
        text: Исходный текст.

    Returns:
        Очищенный текст.

    Raises:
        EmptyInputError: Текст пустой.
        InputLengthError: Текст слишком длинный.
    """
    if text is None:
        raise EmptyInputError("Текст транскрибации не указан")

    cleaned = str(text).strip()
    if not cleaned:
        raise EmptyInputError("Текст транскрибации не может быть пустым")

    if len(cleaned) > MAX_TEXT_LENGTH:
        raise InputLengthError(
            f"Текст слишком длинный ({len(cleaned)} символов). "
            f"Максимум: {MAX_TEXT_LENGTH} символов"
        )

    return cleaned


def validate_product_name(name: str) -> str:
    """
    Проверяет название товара.

    Args:
        name: Название товара.

    Returns:
        Очищенное название.

    Raises:
        EmptyInputError: Название пустое.
        InputLengthError: Название слишком длинное.
    """
    if name is None:
        raise EmptyInputError("Название товара не указано")

    cleaned = str(name).strip()
    if len(cleaned) < MIN_PRODUCT_NAME_LENGTH:
        raise EmptyInputError("Название товара не может быть пустым")

    if len(cleaned) > MAX_PRODUCT_NAME_LENGTH:
        raise InputLengthError(
            f"Название товара слишком длинное ({len(cleaned)} символов). "
            f"Максимум: {MAX_PRODUCT_NAME_LENGTH} символов"
        )

    return cleaned


def validate_product_price(price: str) -> str:
    """
    Проверяет цену товара (базовая проверка).

    Args:
        price: Цена (строка, может быть любой формат).

    Returns:
        Очищенная строка цены.

    Raises:
        EmptyInputError: Цена не указана.
    """
    if price is None:
        raise EmptyInputError("Стоимость товара не указана")

    cleaned = str(price).strip()
    if not cleaned:
        raise EmptyInputError("Стоимость товара не может быть пустой")

    return cleaned


def validate_product_file_lines(lines: list[str]) -> tuple[str, str]:
    """
    Проверяет строки файла для карточки товара (название, цена).

    Args:
        lines: Строки файла (минимум 2: название, цена).

    Returns:
        (product_name, product_price).

    Raises:
        EmptyInputError: Недостаточно данных.
    """
    if not lines:
        raise EmptyInputError("Файл карточки товара пуст")

    name = lines[0].strip() if lines else ""
    price = lines[1].strip() if len(lines) > 1 else ""

    validated_name = validate_product_name(name)
    validated_price = validate_product_price(price) if price else ""
    return validated_name, validated_price
