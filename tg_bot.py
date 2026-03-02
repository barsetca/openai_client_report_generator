"""
Telegram-бот AI Client Report Generator.

Весь функционал CLI доступен через кнопки:
- Отчёт по диалогу
- Отчёт по заказу дизайна
- Карточка товара для маркетплейса
"""

import asyncio
import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

load_dotenv()

from main import (
    create_dialog_report,
    create_design_report,
    create_product_card_report,
)
from utils.text_extractor import extract_text_from_file

PROJECT_ROOT = Path(__file__).resolve().parent


class ReportStates(StatesGroup):
    main = State()
    awaiting_transcription = State()
    awaiting_product_name = State()
    awaiting_product_price = State()


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню выбора типа отчёта."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 Отчёт по диалогу",
            callback_data="report_1"
        )],
        [InlineKeyboardButton(
            text="🎨 Отчёт по дизайну сайта",
            callback_data="report_2"
        )],
        [InlineKeyboardButton(
            text="🛒 Карточка товара",
            callback_data="report_3"
        )],
    ])


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Кнопка отмены."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")]
    ])


WELCOME = (
    "👋 <b>AI Client Report Generator</b>\n\n"
    "Генерирую PDF-отчёты с помощью ИИ.\n"
    "Выберите тип отчёта:"
)

REPORT_PROMPTS = {
    "1": (
        "📋 <b>Отчёт по диалогу с клиентом</b>\n\n"
        "Отправьте <b>файл</b> (txt, pdf, docx) или <b>текст</b> транскрибации диалога."
    ),
    "2": (
        "🎨 <b>Отчёт по заказу дизайна сайта</b>\n\n"
        "Отправьте <b>файл</b> (txt, pdf, docx) или <b>текст</b> транскрибации.\n"
        "Будет сгенерирован пример макета."
    ),
    "3": (
        "🛒 <b>Карточка товара для маркетплейса</b>\n\n"
        "Введите <b>название товара</b>:"
    ),
}


async def run_sync(func, *args):
    """Выполняет синхронную функцию в пуле потоков."""
    return await asyncio.to_thread(func, *args)


async def start_handler(message: Message, state: FSMContext):
    """Команда /start."""
    await state.clear()
    await message.answer(
        WELCOME,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(ReportStates.main)


async def main_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора типа отчёта."""
    await callback.answer()
    data = callback.data
    
    if data == "cancel":
        await state.clear()
        await callback.message.edit_text(
            WELCOME,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(ReportStates.main)
        return
    
    if data.startswith("report_"):
        report_type = data.split("_")[1]
        await state.update_data(report_type=report_type)
        
        prompt = REPORT_PROMPTS.get(report_type, "")
        await callback.message.edit_text(
            prompt,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
        
        if report_type == "3":
            await state.set_state(ReportStates.awaiting_product_name)
        else:
            await state.set_state(ReportStates.awaiting_transcription)


async def transcription_handler(message: Message, state: FSMContext):
    """Обработка текста транскрибации."""
    if not message.text:
        return
    
    data = await state.get_data()
    report_type = data.get("report_type", "1")
    
    text = message.text.strip()
    if not text:
        await message.answer("Текст не может быть пустым. Отправьте транскрибацию.")
        return
    
    status_msg = await message.answer("⏳ Обработка...")
    
    try:
        if report_type == "1":
            pdf_path = await run_sync(create_dialog_report, text)
        else:
            pdf_path = await run_sync(create_design_report, text)
        
        await status_msg.edit_text("✅ Готово! Отправляю PDF...")
        
        doc = FSInputFile(pdf_path, filename=Path(pdf_path).name)
        await message.answer_document(doc)
        await status_msg.delete()
        
        await state.clear()
        await message.answer(WELCOME, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await state.set_state(ReportStates.main)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {str(e)}")


async def document_handler(message: Message, state: FSMContext):
    """Обработка загруженного файла."""
    if not message.document:
        return
    
    doc = message.document
    suffix = Path(doc.file_name or "").suffix.lower()
    
    if suffix not in (".txt", ".pdf", ".docx"):
        await message.answer(
            "❌ Формат не поддерживается. Используйте .txt, .pdf или .docx"
        )
        return
    
    data = await state.get_data()
    report_type = data.get("report_type", "1")
    
    status_msg = await message.answer("⏳ Скачиваю и обрабатываю файл...")
    
    try:
        bot = message.bot
        file = await bot.get_file(doc.file_id)
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            await bot.download_file(file.file_path, tmp.name)
            tmp_path = tmp.name
        
        try:
            text = extract_text_from_file(tmp_path)
            if not text.strip():
                await status_msg.edit_text("❌ Файл пустой или не удалось извлечь текст.")
                return
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        
        await status_msg.edit_text("⏳ Генерирую отчёт...")
        
        if report_type == "1":
            pdf_path = await run_sync(create_dialog_report, text)
        else:
            pdf_path = await run_sync(create_design_report, text)
        
        await status_msg.edit_text("✅ Готово! Отправляю PDF...")
        
        result_doc = FSInputFile(pdf_path, filename=Path(pdf_path).name)
        await message.answer_document(result_doc)
        await status_msg.delete()
        
        await state.clear()
        await message.answer(WELCOME, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await state.set_state(ReportStates.main)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {str(e)}")


async def product_name_handler(message: Message, state: FSMContext):
    """Обработка названия товара."""
    if not message.text:
        return
    
    name = message.text.strip()
    if not name:
        await message.answer("Введите название товара.")
        return
    
    await state.update_data(product_name=name)
    await state.set_state(ReportStates.awaiting_product_price)
    await message.answer(
        "💰 Введите <b>стоимость</b> товара:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


async def product_price_handler(message: Message, state: FSMContext):
    """Обработка стоимости товара и генерация карточки."""
    if not message.text:
        return
    
    price = message.text.strip()
    if not price:
        await message.answer("Введите стоимость.")
        return
    
    data = await state.get_data()
    product_name = data.get("product_name", "")
    
    if not product_name:
        await state.clear()
        await message.answer("Сессия сброшена. Начните заново.")
        return
    
    status_msg = await message.answer("⏳ Генерирую карточку товара...")
    
    try:
        pdf_path = await run_sync(create_product_card_report, product_name, price)
        
        await status_msg.edit_text("✅ Готово! Отправляю PDF...")
        
        doc = FSInputFile(pdf_path, filename=Path(pdf_path).name)
        await message.answer_document(doc)
        await status_msg.delete()
        
        await state.clear()
        await message.answer(WELCOME, reply_markup=get_main_keyboard(), parse_mode="HTML")
        await state.set_state(ReportStates.main)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Ошибка: {str(e)}")


def setup_bot() -> tuple[Bot, Dispatcher]:
    """Настройка бота и диспетчера."""
    import os
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
    
    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.message.register(start_handler, CommandStart())
    dp.callback_query.register(main_callback, F.data.in_({"report_1", "report_2", "report_3", "cancel"}))

    async def main_menu_hint(message: Message, state: FSMContext):
        """Подсказка при вводе в главном меню."""
        await message.answer("👆 Выберите тип отчёта кнопками выше.")

    dp.message.register(main_menu_hint, ReportStates.main)
    
    dp.message.register(
        document_handler,
        ReportStates.awaiting_transcription,
        F.document
    )
    dp.message.register(
        transcription_handler,
        ReportStates.awaiting_transcription,
        F.text
    )
    
    dp.message.register(
        product_name_handler,
        ReportStates.awaiting_product_name,
        F.text
    )
    dp.message.register(
        product_price_handler,
        ReportStates.awaiting_product_price,
        F.text
    )
    
    return bot, dp


async def main():
    """Запуск бота."""
    bot, dp = setup_bot()
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import os
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("Ошибка: укажите TELEGRAM_BOT_TOKEN в .env")
        exit(1)
    
    asyncio.run(main())
