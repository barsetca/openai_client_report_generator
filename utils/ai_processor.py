"""Модуль взаимодействия с OpenAI для обработки диалогов с клиентами."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

SYSTEM_PROMPT = """Ты — ассистент для анализа диалогов с клиентами.
Проанализируй транскрибацию диалога и извлеки структурированную информацию.
Ответь ТОЛЬКО валидным JSON без дополнительного текста, со следующими полями:
- client_name: имя клиента (если упоминается) или "Клиент"
- topic: основная тема обращения
- main_request: главный запрос или потребность клиента
- mood: эмоциональное состояние клиента (нейтральное, позитивное, негативное, взволнованное и т.д.)
- next_steps: рекомендуемые следующие шаги по работе с клиентом
- desired_deadline: желаемые сроки (если упоминаются) или "Не указано"
- desired_cost: желаемая стоимость/бюджет (если упоминается) или "Не указано"
- main_wishes: что точно должно быть в финальном продукте, основные пожелания клиента (или "Не указано")"""


def process_dialog_with_ai(text: str) -> dict:
    """
    Передаёт транскрибацию в OpenAI и возвращает структурированные данные.
    
    Args:
        text: Текст транскрибации диалога с клиентом.
        
    Returns:
        Словарь с полями: client_name, topic, main_request, mood, next_steps,
        desired_deadline, desired_cost, main_wishes
        
    Raises:
        ValueError: Если API ключ не задан или произошла ошибка OpenAI.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не задан в .env файле")
    
    if not text or not text.strip():
        raise ValueError("Текст транскрибации не может быть пустым")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    
    content = response.choices[0].message.content.strip()
    
    # Убираем возможные markdown-обёртки (```json ... ```)
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        )
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI вернул невалидный JSON: {e}") from e


OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1-mini")

DESIGN_PROMPT_SYSTEM = """Ты — ассистент для создания промптов к генератору изображений.
На основе транскрибации диалога о заказе дизайна сайта создай детальный промпт на английском языке для генерации примера изображения макета/дизайна веб-сайта.
Промпт должен описывать: стиль, цвета, структуру страницы, ключевые элементы (шапка, контент, футер), тип бизнеса/тематику.
Промпт должен быть пригоден для DALL-E. Ответь ТОЛЬКО текстом промпта, без кавычек и пояснений."""


def extract_design_prompt(text: str) -> str:
    """
    Извлекает промпт для генерации изображения дизайна из транскрибации.
    
    Args:
        text: Текст транскрибации о заказе дизайна сайта.
        
    Returns:
        Промпт для DALL-E.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не задан в .env файле")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": DESIGN_PROMPT_SYSTEM},
            {"role": "user", "content": text},
        ],
        temperature=0.5,
    )
    
    return response.choices[0].message.content.strip()


def generate_design_image(prompt: str) -> bytes:
    """
    Генерирует изображение дизайна сайта через OpenAI.
    Поддерживает gpt-image-* и DALL-E модели. Формат ~16:9.
    
    Args:
        prompt: Промпт для генерации изображения.
        
    Returns:
        PNG-изображение в виде байтов.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не задан в .env файле")
    
    import base64
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    is_gpt_image = OPENAI_IMAGE_MODEL.startswith("gpt-image")
    
    # Параметры различаются для GPT Image и DALL-E
    if is_gpt_image:
        # gpt-image-1-mini и др.: без response_format (b64 по умолчанию),
        # size: 1536x1024 (горизонтальный ~16:9), quality: medium/high
        kwargs = {
            "model": OPENAI_IMAGE_MODEL,
            "prompt": prompt,
            "size": "1536x1024",
            "quality": "medium",
            "n": 1,
        }
    else:
        # DALL-E 2/3
        kwargs = {
            "model": OPENAI_IMAGE_MODEL,
            "prompt": prompt,
            "size": "1792x1024",
            "quality": "standard",
            "n": 1,
            "response_format": "b64_json",
        }
    
    response = client.images.generate(**kwargs)
    return base64.b64decode(response.data[0].b64_json)


def generate_product_image(prompt: str) -> bytes:
    """
    Генерирует изображение товара через OpenAI (модель из .env).
    Формат квадратный для карточки товара.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не задан в .env файле")
    
    import base64
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    is_gpt_image = OPENAI_IMAGE_MODEL.startswith("gpt-image")
    
    if is_gpt_image:
        kwargs = {
            "model": OPENAI_IMAGE_MODEL,
            "prompt": prompt,
            "size": "1024x1024",
            "quality": "medium",
            "n": 1,
        }
    else:
        kwargs = {
            "model": OPENAI_IMAGE_MODEL,
            "prompt": prompt,
            "size": "1024x1024",
            "quality": "standard",
            "n": 1,
            "response_format": "b64_json",
        }
    
    response = client.images.generate(**kwargs)
    return base64.b64decode(response.data[0].b64_json)


PRODUCT_CARD_SYSTEM = """Ты — ассистент для создания карточек товаров маркетплейса.
По названию товара создай:
1) Промпт для генерации изображения товара — на английском, детальное описание для AI-генератора изображений (стиль: фото на белом фоне, как для маркетплейса)
2) Краткое описание товара для карточки — 1-2 предложения на русском, привлекательное для покупателя.

Ответь ТОЛЬКО валидным JSON без дополнительного текста:
{"image_prompt": "...", "description": "..."}"""


def get_product_card_data(product_name: str) -> dict:
    """
    Получает промпт для изображения и описание товара через OpenAI.
    
    Args:
        product_name: Название товара.
        
    Returns:
        {"image_prompt": str, "description": str}
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не задан в .env файле")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": PRODUCT_CARD_SYSTEM},
            {"role": "user", "content": f"Название товара: {product_name}"},
        ],
        temperature=0.5,
    )
    
    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        )
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"OpenAI вернул невалидный JSON: {e}") from e
