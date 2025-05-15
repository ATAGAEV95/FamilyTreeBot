from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def persons_keyboard(persons: list) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с кнопками для списка людей."""
    keyboard = InlineKeyboardBuilder()
    for person in persons:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{person.first_name} {person.last_name}",
                callback_data=f"person_{person.person_id}",
            )
        )
    return keyboard.adjust(1).as_markup()
