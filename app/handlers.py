from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import app.requests as req

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать!'#, reply_markup=kb.main
                         )


@router.message()
async def process_fullname(message: Message):
    persons = await req.search_persons(message.text)
    if not persons:
        await message.answer("Ничего не найдено.")
        return
    else:
        await message.answer(
            "Все совпадения:",
            reply_markup=await kb.persons_keyboard(persons)
        )


@router.callback_query(F.data.startswith("person_"))
async def persons_callback_query(callback: CallbackQuery):
    person_id = int(callback.data.split("_")[1])
    person = await req.get_person(person_id)
    if not person:
        await callback.answer("Персонаж не найден")
        return
    main_info = (
        f"👤 {person.first_name} {person.last_name} {person.father_name}\n"
        f"🎂 Дата рождения: {person.birth_date.strftime('%d.%m.%Y') if person.birth_date else 'Не указана'}\n"
        f"💀 Дата смерти: {person.death_date.strftime('%d.%m.%Y') if person.death_date else 'Не указана'}\n"
        f"⚧ Пол: {person.gender if person.gender else 'Не указан'}\n"
        f"📖 Биография: {person.bio if person.bio else 'Не указана'}"
    )
    siblings = await req.get_siblings(person.first_name, person.last_name)
    siblings_info = ""
    if siblings:
        siblings_info = "\n\n👨👦 Братья/сестры:\n" + "\n".join(
            [f"{sib['sibling_type']}: {sib['first_name']} {sib['last_name']} {sib['father_name']}"
             for sib in siblings]
        )
    parents = await req.get_parents(person.first_name, person.last_name)
    parents_info = ""
    if parents:
        parents_info = "\n\n👪 Родители:\n" + "\n".join(
            [f"{p['first_name']} {p['last_name']} {p['father_name']}" for p in parents]
        )
    spouses = await req.get_spouses(person.first_name, person.last_name)
    spouses_info = ""
    if spouses:
        spouses_info = "\n\n👫 Супруг(а):\n" + "\n".join(
            [f"{s['spouse_type']}: {s['first_name']} {s['last_name']} {s['father_name']}"
             for s in spouses]
        )
    children = await req.get_children(person.first_name, person.last_name)
    children_info = ""
    if children:
        children_info = "\n\n👶 Дети:\n" + "\n".join(
            [f"{child['child_type']}: {child['first_name']} {child['last_name']} {child['father_name']}"
             for child in children]
        )
    full_response = main_info + parents_info + siblings_info + spouses_info + children_info
    if person.photo_url:
        await callback.message.answer_photo(
            photo=person.photo_url,
            caption=full_response
        )
    else:
        await callback.message.answer(full_response)
    await callback.answer()