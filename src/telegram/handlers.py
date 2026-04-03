from enum import Enum
from os import getenv
from re import Match, search

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

from src.db_orm import TableManager, Users
from src.methods import Methods
from src.utility import CourseList, FileTemplates, ProcessUser

from .states import ChangeText, ForwardMessage, ViewText


class Callbacks(Enum):
    forward = "forward_link"
    user404 = "user_not_found"
    rewrite = "rewrite_text"
    change = "change_file"


EMAILPATTERN = r"\b[\w.%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
router = Router()
methods = Methods()
load_dotenv(override=True)
courses = [member.value.title for member in CourseList]


@router.message(CommandStart())
async def startup(message: Message):
    await message.answer(
        "Список команд:"
        + "\n  /edit\n  (просто скинуть почту)\n  /view"
        + "\n\n\n/edit - изменить приветственное сообщение"
        + "\n/view - посмотреть приветственные сообщения"
        "\nСкинутый email дает возможность отправить ссылку тем кто уже есть в базе и нет"
        + "\nРаботать с ботом может только человек с разрешенным айди"
    )


@router.message(F.text.regexp(EMAILPATTERN, mode="search"))
async def check_user(message: Message, state: FSMContext):
    try:
        if message.from_user.id != int(
            getenv("SUPPORT_ID")
        ) and message.from_user.id != int(getenv("TECH_SUPPORT_ID")):
            return None

        email: Match[str] = search(EMAILPATTERN, message.text)
        await message.answer(f"Найденый Email: {email.group()}")

        user: Users = TableManager.get_user(email.group())
        builder = InlineKeyboardBuilder()
        if not user:
            builder.button(
                text="Все равно отправить", callback_data=Callbacks.user404.value
            )

            await message.answer(
                f"Пользователь с Email: {email.group()} не найден.",
                reply_markup=builder.as_markup(),
            )
            await state.update_data(Email=email.group())

        else:
            builder.button(
                text="Отправить снова?", callback_data=Callbacks.forward.value
            )
            await message.answer(
                f"Статус: {user.Status}\nКурс: {user.Course}\nИмя: {user.Name}",
                reply_markup=builder.as_markup(),
            )

            await state.set_state(ForwardMessage.collect_data)
            await state.update_data(Email=user.Email)
            await state.update_data(Name=user.Name)

    except Exception:
        await state.clear()


@router.callback_query(F.data == Callbacks.forward.value)
async def forward_message(call: CallbackQuery, state: FSMContext):
    try:
        await state.set_state(ForwardMessage.choose_course)
        builder = InlineKeyboardBuilder()
        for course in courses:
            builder.button(text=course.name, callback_data=course.name)
        builder.adjust(3, 3)
        await call.message.edit_reply_markup(reply_markup=builder.as_markup())

    except Exception:
        await state.clear()


@router.callback_query(F.data == Callbacks.user404.value)
async def forward_message_user404(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        await state.set_state(ForwardMessage.set_name)
        await call.message.answer(
            "Напишите имя которое следует указать при отправке сообщения"
        )

    except Exception:
        await state.clear()


@router.message(F.text, ForwardMessage.set_name)
async def set_name_user404(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        await state.update_data(Name=message.text)
        await state.set_state(ForwardMessage.choose_course)

        builder = InlineKeyboardBuilder()
        for course in courses:
            builder.button(text=course.name, callback_data=course.name)
        builder.adjust(3, 3)
        await message.answer(
            f"Email: {data['Email']} \nИмя: {message.text}",
            reply_markup=builder.as_markup(),
        )

    except Exception:
        await state.clear()


@router.callback_query(F.data.in_(courses))
async def choose_course(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer("Создаем ссылки и отправляем их на Email")
        user = await state.get_data()
        links = await methods.process_user_Telegram(
            ProcessUser(user["Email"], user["Name"], call.data)
        )
        if not links:
            await call.message.answer(f"Проблема с созданием ссылки")
            return None

        await call.message.answer(
            f"Сообщение отправлено, если нужна прямая ссылка: \n{links}"
        )

    finally:
        await state.clear()


@router.message(Command("edit", ignore_case=True))
async def change_file(message: Message, state: FSMContext):
    try:
        if message.from_user.id != int(
            getenv("SUPPORT_ID")
        ) and message.from_user.id != int(getenv("TECH_SUPPORT_ID")):
            return None

        await state.set_state(ChangeText.again)
        await message.answer(
            "Отправьте текст который будет использоваться для отправки на почту"
        )

    except Exception:
        await state.clear()


@router.callback_query(F.data == Callbacks.change.value)
async def choose_file(call: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=FileTemplates.text.value.name, callback_data=str(FileTemplates.text.value)
    )

    await call.message.edit_reply_markup(reply_markup=builder.as_markup())


@router.callback_query(F.data.endswith(".txt"), ChangeText.get_text)
async def write_text(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != int(getenv("SUPPORT_ID")) and call.from_user.id != int(
        getenv("TECH_SUPPORT_ID")
    ):
        return None

    data = await state.get_data()
    await methods.write_file(call.data, data["text"])
    await call.message.answer(f"Файл успешно изменен")


@router.callback_query(F.data == Callbacks.rewrite.value)
async def set_FSM(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    if call.from_user.id != int(getenv("SUPPORT_ID")):
        return None

    await state.set_state(ChangeText.again)
    await call.message.answer(
        "Отправьте текст который будет использоваться для отправки на почту"
    )


@router.message(F.text, ChangeText.again)
async def change_text(message: Message, state: FSMContext):
    try:
        if message.from_user.id != int(getenv("SUPPORT_ID")):
            return None

        tags: list[str] = ["{{ name }}", "{{ channel }}", "{{ chat }}"]
        warn: list[str] = []
        for tag in tags:
            if tag not in message.text:
                warn.append(tag)

        if warn:
            msg = (
                f"{' '.join(warn)} отсутствуют в тексте, уверены что он не нужен?"
                + f"\n\nОбязательные теги:\n  {tags[0]}\n  {tags[1]}"
                + f'\n\nСуществующие теги:\n  {'\n  '.join(tags)}'
            )
            await message.answer(msg)

        builder = InlineKeyboardBuilder()
        builder.button(text="Изменить файл", callback_data=Callbacks.change.value)
        builder.button(text="Переписать текст", callback_data=Callbacks.rewrite.value)
        builder.adjust(1, 1)

        await state.update_data(text=message.text)
        await state.set_state(ChangeText.get_text)

        await message.answer(
            f"Предпросмотр текста:\n{message.text}", reply_markup=builder.as_markup()
        )

    except Exception:
        await state.clear()


@router.message(Command("view", ignore_case=True))
async def view_files(message: Message, state: FSMContext):
    try:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=FileTemplates.text.value.name,
            callback_data=str(FileTemplates.text.value),
        )

        await state.set_state(ViewText.view)
        await message.answer(
            "Какой файл нужно посмотреть?", reply_markup=builder.as_markup()
        )

    except Exception:
        await state.clear()


@router.callback_query(F.data.endswith(".txt"), ViewText.view)
async def choose_view(call: CallbackQuery, state: FSMContext):
    try:
        await call.answer()
        text = await methods.read_file(call.data)
        await call.message.answer(text, parse_mode="HTML")

    finally:
        await state.clear()
