from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def persons_keyboard(persons: list):
    keyboard = InlineKeyboardBuilder()
    for person in persons:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{person.first_name} {person.last_name}",
                callback_data=f"person_{person.person_id}",
            )
        )
    return keyboard.adjust(1).as_markup()
