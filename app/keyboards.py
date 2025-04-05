from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


# main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Имя Фамилия')],
#                                      [KeyboardButton(text='Фамилия')]],
#                            resize_keyboard=True)



async def persons_keyboard(persons: list):
    keyboard = InlineKeyboardBuilder()
    for person in persons:
        keyboard.add(InlineKeyboardButton(
            text=f"{person.first_name} {person.last_name}",
            callback_data=f"person_{person.person_id}"
        ))
    # keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()