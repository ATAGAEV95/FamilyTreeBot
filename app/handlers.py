from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb
import app.requests as req
import app.utils as ut

router = Router()


ACCESS_PASSWORD = "e5ae93bd8095fbd86c25a110bbf194a5a1a209f1e8eb31bb30c8b0ecbe254d58"


class RegisterState(StatesGroup):
    waiting_for_password = State()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await req.get_user_by_id(user_id)
    if user:
        await message.answer(
            "Добро пожаловать! Чтобы начать поиск, просто введите имя или фамилию персоны."
        )
    else:
        await message.answer("Добро пожаловать! Для продолжения работы введите пароль для доступа.")
        await state.set_state(RegisterState.waiting_for_password)


@router.message(RegisterState.waiting_for_password)
async def password_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if ut.hash_password(message.text.strip()) == ACCESS_PASSWORD:
        await req.add_user(user_id, message.from_user.username or "")
        await message.answer(
            "Авторизация успешна! Теперь у вас полный доступ. "
            "Чтобы начать поиск, просто введите имя или фамилию персоны."
        )
        await state.clear()
    else:
        await message.answer("Неверный пароль. Попробуйте еще раз:")


@router.message()
async def after_auth_person_search(message: Message):
    user = await req.get_user_by_id(message.from_user.id)
    if not user:
        await message.answer("Доступ запрещён. Для доступа введите /start.")
        return
    persons = await req.search_persons(message.text)
    if not persons:
        await message.answer("Ничего не найдено. Попробуйте изменить запрос или уточнить данные.")
    else:
        await message.answer("Все совпадения:", reply_markup=await kb.persons_keyboard(persons))


@router.callback_query(F.data.startswith("person_"))
async def persons_callback_query(callback: CallbackQuery):
    person_id = int(callback.data.split("_")[1])
    person = await req.get_person(person_id)
    if not person:
        await callback.answer("Персонаж не найден")
        return
    photo_info = (
        f"🖼️ Фото: <a href='{person.photo_url}'>Смотреть</a>"
        if person.photo_url
        else "🖼️ Фото: не указано"
    )
    main_info = (
        f"👤 {person.first_name} {person.last_name} {person.father_name}\n"
        f"🎂 Дата рождения: {person.birth_date.strftime('%d.%m.%Y') if person.birth_date else 'Не указана'}\n"
        f"💀 Дата смерти: {person.death_date.strftime('%d.%m.%Y') if person.death_date else 'Не указана'}\n"
        f"⚧ Пол: {person.gender if person.gender else 'Не указан'}\n"
        f"📖 Биография: {person.bio if person.bio else 'Не указана'}\n"
        f"{photo_info}"
    )
    siblings = await req.get_siblings(person.first_name, person.last_name)
    siblings_info = ""
    if siblings:
        siblings_info = "\n\n👨👦 Братья/сестры:\n" + "\n".join(
            [
                f"{sib['sibling_type']}: {sib['first_name']} {sib['last_name']} {sib['father_name']}"
                for sib in siblings
            ]
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
            [
                f"{s['spouse_type']}: {s['first_name']} {s['last_name']} {s['father_name']}"
                for s in spouses
            ]
        )
    children = await req.get_children(person.first_name, person.last_name)
    children_info = ""
    if children:
        children_info = "\n\n👶 Дети:\n" + "\n".join(
            [
                f"{child['child_type']}: {child['first_name']} {child['last_name']} {child['father_name']}"
                for child in children
            ]
        )
    full_response = main_info + parents_info + siblings_info + spouses_info + children_info
    await callback.message.answer(full_response, parse_mode="HTML")
    await callback.answer()
