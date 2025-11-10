# file: handlers/form_filling.py
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from config import (PHONE_REGEX, EMAIL_REGEX, MAX_VIDEO_SIZE_BYTES,
                    MAX_VIDEO_NOTE_SIZE_BYTES, MAX_VIDEO_SIZE_MB, MAX_VIDEO_NOTE_SIZE_MB)
from keyboards import (get_back_cancel_kb, get_location_choice_kb,
                       get_feedback_choice_kb, get_rodents_choice_kb,
                       get_skip_email_kb)
from states import ReportForm
from logic import show_confirmation_summary, escape_html

router = Router()


# 4. Обработчик ТИПА ПРОБЛЕМЫ
@router.callback_query(ReportForm.awaiting_type, F.data.startswith("report_type:"))
async def process_type_callback(call: CallbackQuery, state: FSMContext):
    report_type = call.data.split(":")[1]

    # --- ⬇️ ИЗМЕНЕНИЕ: Рефакторинг "магических строк" ⬇️ ---
    is_garbage_report = (report_type == "garbage")

    type_text = "🗑 Скопление мусора" if is_garbage_report else "💨 Загрязнение воздуха / Запах"

    await state.update_data(
        complaint_type=type_text,
        is_garbage_report=is_garbage_report  # Сохраняем флаг
    )
    # --- ⬆️ КОНЕЦ ИЗМЕНЕНИЯ ⬆️ ---

    await call.message.edit_text(
        "📸 Понял. Теперь, пожалуйста, прикрепите <b>одно фото, видео или видео-кружок</b>, "
        "которое фиксирует проблему.",  # <--- Изменен текст
        reply_markup=get_back_cancel_kb()
    )
    await call.answer()
    await state.set_state(ReportForm.awaiting_media)


@router.message(ReportForm.awaiting_type)
async def process_type_invalid(message: Message):
    await message.answer("Пожалуйста, <b>используйте кнопки выше</b>, чтобы выбрать тип проблемы.")


# 5. Обработчики ФОТО / ВИДЕО
@router.message(ReportForm.awaiting_media, F.photo)
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    photo_file_id = message.photo[-1].file_id

    # --- ИЗМЕНЕНИЕ: Обнуляем другие медиа ---
    await state.update_data(
        photo_id=photo_file_id,
        media_type='photo',
        video_id=None,
        video_note_id=None
    )

    data = await state.get_data()

    # --- ИЗМЕНЕНО: Динамический пример на основе флага ---
    example_text = "<i>Например: «Контейнеры переполнены уже неделю».</i>"
    if not data.get('is_garbage_report'):  # Проверяем флаг
        example_text = "<i>Например: «Сильный химический запах со стороны промзоны».</i>"
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    if data.get("is_editing"):
        await message.answer("✅ Фото обновлено.")
        await show_confirmation_summary(message, state, bot)
    else:
        await message.answer(
            f"👍 Фото получено. Теперь, пожалуйста, <b>опишите проблему</b> своими словами.\n\n"
            f"{example_text}",
            reply_markup=get_back_cancel_kb()
        )
        await state.set_state(ReportForm.awaiting_description)


@router.message(ReportForm.awaiting_media, F.video)
async def process_video(message: Message, state: FSMContext, bot: Bot):
    # --- ⬇️ НОВАЯ ПРОВЕРКА: Лимит размера видео ⬇️ ---
    if message.video.file_size > MAX_VIDEO_SIZE_BYTES:
        await message.answer(
            f"❗️ <b>Видео слишком большое!</b>\n\n"
            f"Пожалуйста, прикрепите видео размером "
            f"не более <b>{MAX_VIDEO_SIZE_MB} МБ</b>."
        )
        return
    # --- ⬆️ КОНЕЦ ПРОВЕРКИ ⬆️ ---

    video_file_id = message.video.file_id

    # --- ИЗМЕНЕНИЕ: Обнуляем другие медиа ---
    await state.update_data(
        video_id=video_file_id,
        media_type='video',
        photo_id=None,
        video_note_id=None
    )

    data = await state.get_data()

    # --- ИЗМЕНЕНО: Динамический пример на основе флага ---
    example_text = "<i>Например: «Сброс отходов в реку».</i>"
    if not data.get('is_garbage_report'):  # Проверяем флаг
        example_text = "<i>Например: «Черный дым из трубы завода».</i>"
    # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    if data.get("is_editing"):
        await message.answer("✅ Видео обновлено.")
        await show_confirmation_summary(message, state, bot)
    else:
        await message.answer(
            f"👍 Видео получено. Теперь, пожалуйста, <b>опишите проблему</b> своими словами.\n\n"
            f"{example_text}",
            reply_markup=get_back_cancel_kb()
        )
        await state.set_state(ReportForm.awaiting_description)


# --- ⬇️ НОВЫЙ ХЭНДЛЕР: Видео-кружок ⬇️ ---
@router.message(ReportForm.awaiting_media, F.video_note)
async def process_video_note(message: Message, state: FSMContext, bot: Bot):
    # --- НОВАЯ ПРОВЕРКА: Лимит размера кружка ---
    if message.video_note.file_size > MAX_VIDEO_NOTE_SIZE_BYTES:
        await message.answer(
            f"❗️ <b>Видео-кружок слишком большой!</b>\n\n"
            f"Что-то пошло не так, кружок не должен превышать "
            f"<b>{MAX_VIDEO_NOTE_SIZE_MB} МБ</b>. Попробуйте записать короче."
        )
        return
    # --- КОНЕЦ ПРОВЕРКИ ---

    video_note_file_id = message.video_note.file_id

    # --- Обновляем состояние ---
    await state.update_data(
        video_note_id=video_note_file_id,
        media_type='video_note',
        photo_id=None,
        video_id=None
    )

    data = await state.get_data()

    # --- Динамический пример на основе флага ---
    example_text = "<i>Например: «Контейнеры переполнены...»</i>"
    if not data.get('is_garbage_report'):  # Проверяем флаг
        example_text = "<i>Например: «Сильный химический запах...»</i>"

    if data.get("is_editing"):
        await message.answer("✅ Видео-кружок обновлен.")
        await show_confirmation_summary(message, state, bot)
    else:
        await message.answer(
            f"👍 Видео-кружок получен. Теперь, пожалуйста, <b>опишите проблему</b> своими словами.\n\n"
            f"{example_text}",
            reply_markup=get_back_cancel_kb()
        )
        await state.set_state(ReportForm.awaiting_description)


# --- ⬆️ КОНЕЦ НОВОГО ХЭНДЛЕРА ⬆️ ---


@router.message(ReportForm.awaiting_media)
async def process_media_invalid(message: Message):
    # --- ИЗМЕНЕНИЕ: Обновлен текст ошибки ---
    await message.answer(
        "❗️ Пожалуйста, отправьте <b>одно фото, одно видео или один видео-кружок</b>, чтобы продолжить.")


# 6. Обработчик ОПИСАНИЯ
@router.message(ReportForm.awaiting_description, F.text)
async def process_description(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(description=message.text)
    data = await state.get_data()

    if data.get("is_editing"):
        await message.answer("✅ Описание обновлено.")
        await show_confirmation_summary(message, state, bot)
    else:
        # --- ⬇️ ИЗМЕНЕНИЕ: Проверка флага грызунов ⬇️ ---
        if data.get('is_garbage_report') is True:
            # Если мусор - спрашиваем про грызунов
            await message.answer(
                "📝 Описание принято. \n\n"
                "Уточняющий вопрос: <b>были ли замечены грызуны (крысы, мыши)</b> в месте скопления мусора?",
                reply_markup=get_rodents_choice_kb(is_editing=False)
            )
            await state.set_state(ReportForm.awaiting_rodents_choice)
        else:
            # Если не мусор - переход к локации
            await message.answer(
                "📝 Описание принято. Теперь укажите, <b>где это происходит</b>.",
                reply_markup=get_location_choice_kb()
            )
            await state.set_state(ReportForm.awaiting_location_choice)
        # --- ⬆️ КОНЕЦ ИЗМЕНЕНИЙ ⬆️ ---


@router.message(ReportForm.awaiting_description)
async def process_description_invalid(message: Message):
    await message.answer("❗️ Пожалуйста, введите <b>описание в виде обычного текста</b>.")


# --- (Остальная часть файла `form_filling.py` остается без изменений) ---

# --- НОВЫЙ БЛОК: Обработчик ГРЫЗУНОВ ---
@router.callback_query(ReportForm.awaiting_rodents_choice, F.data.startswith("rodents:"))
async def process_rodents_choice(call: CallbackQuery, state: FSMContext, bot: Bot):
    has_rodents = call.data.split(":")[1] == "yes"
    await state.update_data(rodents=has_rodents)
    await call.answer()

    data = await state.get_data()
    if data.get("is_editing"):
        # Если редактируем, возвращаемся к сводке
        await call.message.edit_text("✅ Статус по грызунам обновлен.")
        await show_confirmation_summary(call, state, bot)
    else:
        # Если заполняем, идем к выбору локации
        await call.message.edit_text(
            "Понял. Теперь укажите, <b>где это происходит</b>.",
            reply_markup=get_location_choice_kb()
        )
        await state.set_state(ReportForm.awaiting_location_choice)


@router.message(ReportForm.awaiting_rodents_choice)
async def process_rodents_invalid(message: Message):
    await message.answer("Пожалуйста, <b>используйте кнопки 'Да' или 'Нет'</b>, чтобы сделать выбор.")


# --- КОНЕЦ НОВОГО БЛОКА ---


# 7. Обработчик ВЫБОРА ЛОКАЦИИ
@router.callback_query(ReportForm.awaiting_location_choice, F.data == "loc_choice:geo")
async def process_location_choice_geo(call: CallbackQuery, state: FSMContext):
    await state.update_data(location_type='geo')
    await call.message.edit_text(
        "Вы можете либо <b>отправить вашу текущую геолокацию</b> (предпочтительно), либо вручную указать точку на карте.\n\n"
        "Нажмите 📎 (скрепку) → 'Геолокация' 📍 → 'Отправить мою текущую геопозицию'.",
        reply_markup=get_back_cancel_kb()
    )
    await call.answer()
    await state.set_state(ReportForm.awaiting_location_geo)


@router.callback_query(ReportForm.awaiting_location_choice, F.data == "loc_choice:address")
async def process_location_choice_address(call: CallbackQuery, state: FSMContext):
    await state.update_data(location_type='address')
    await call.message.edit_text(
        "Пожалуйста, <b>напишите текстом</b> точный адрес (город, улица, номер дома).",
        reply_markup=get_back_cancel_kb()
    )
    await call.answer()
    await state.set_state(ReportForm.awaiting_location_address)


@router.message(ReportForm.awaiting_location_choice)
async def process_location_choice_invalid(message: Message):
    await message.answer("Пожалуйста, <b>используйте кнопки выше</b>, чтобы выбрать способ.")


# 8. Обработчики ГЕОЛОКАЦИИ / АДРЕСА
@router.message(ReportForm.awaiting_location_geo, F.location)
async def process_location_geo(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(
        latitude=message.location.latitude,
        longitude=message.location.longitude,
        address_text=None
    )

    data = await state.get_data()
    if data.get("is_editing"):
        await message.answer("✅ Геолокация обновлена.")
        await show_confirmation_summary(message, state, bot)
    else:
        await message.answer(
            "📍 Местоположение принято. \n\nКак я могу к вам обращаться? (Введите ваше <b>имя</b>)",
            reply_markup=get_back_cancel_kb()
        )
        await state.set_state(ReportForm.awaiting_name)


@router.message(ReportForm.awaiting_location_geo)
async def process_location_geo_invalid(message: Message):
    await message.answer(
        "❗️ Это не похоже на геолокацию. \n\n"
        "Пожалуйста, <b>прикрепите геолокацию</b>, используя 📎 (скрепку) в меню."
    )


@router.message(ReportForm.awaiting_location_address, F.text)
async def process_location_address(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(
        address_text=message.text,
        latitude=None,
        longitude=None
    )

    data = await state.get_data()
    if data.get("is_editing"):
        await message.answer("✅ Адрес обновлен.")
        await show_confirmation_summary(message, state, bot)
    else:
        await message.answer(
            "📍 Адрес принят. \n\nКак я могу к вам обращаться? (Введите ваше <b>имя</b>)",
            reply_markup=get_back_cancel_kb()
        )
        await state.set_state(ReportForm.awaiting_name)


@router.message(ReportForm.awaiting_location_address)
async def process_location_address_invalid(message: Message):
    await message.answer("❗️ Пожалуйста, введите <b>адрес в виде обычного текста</b>.")


# 9. Обработчик для ИМЕНИ
@router.message(ReportForm.awaiting_name, F.text)
async def process_name(message: Message, state: FSMContext, bot: Bot):
    safe_name = escape_html(message.text)
    await state.update_data(name=safe_name)

    data = await state.get_data()
    if data.get("is_editing"):
        if data.get('wants_feedback') is True:
            # --- ИЗМЕНЕНИЕ: Новая клавиатура и текст ---
            await message.answer(
                f"✅ Имя обновлено, {safe_name}! \n\n"
                "📧 Теперь, пожалуйста, введите ваш <b>email-адрес</b>."
                "\n\n<i>Например: example@mail.ru\n(Можно пропустить, если у вас его нет)</i>",
                reply_markup=get_skip_email_kb()
            )
            await state.set_state(ReportForm.awaiting_contact_email)
        else:
            await message.answer("✅ Имя обновлено.")
            await show_confirmation_summary(message, state, bot)
    else:
        await message.answer(
            f"✅ Приятно познакомиться, {safe_name}! \n\n"
            "🔔 Хотите, чтобы мы <b>сообщили вам о решении</b> этой проблемы? \n\n"
            "<i>(Если да, на следующем шаге я попрошу у вас email и телефон для связи).</i>",
            reply_markup=get_feedback_choice_kb()
        )
        await state.set_state(ReportForm.awaiting_feedback_choice)


@router.message(ReportForm.awaiting_name)
async def process_name_invalid(message: Message):
    await message.answer("❗️ Пожалуйста, введите ваше <b>имя в виде обычного текста</b>.")


# 10. Обработчик ВЫБОРА ОБРАТНОЙ СВЯЗИ
@router.callback_query(ReportForm.awaiting_feedback_choice, F.data == "feedback:yes")
async def process_feedback_yes(call: CallbackQuery, state: FSMContext):
    await state.update_data(wants_feedback=True)
    # --- ИЗМЕНЕНИЕ: Новая клавиатура и текст ---
    await call.message.edit_text(
        "📧 Принято. Пожалуйста, введите ваш <b>email-адрес</b>."
        "\n\n<i>Например: example@mail.ru\n(Можно пропустить, если у вас его нет)</i>",
        reply_markup=get_skip_email_kb()  # Используем новую клавиатуру
    )
    await call.answer()
    await state.set_state(ReportForm.awaiting_contact_email)


@router.callback_query(ReportForm.awaiting_feedback_choice, F.data == "feedback:no")
async def process_feedback_no(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(wants_feedback=False, email=None, phone=None)

    await call.message.edit_text(
        "Хорошо, обратная связь не потребуется. \n\nГотовлю сводку вашей заявки...",
        reply_markup=None
    )
    await call.answer()
    await show_confirmation_summary(call, state, bot)


@router.message(ReportForm.awaiting_feedback_choice)
async def process_feedback_invalid(message: Message):
    await message.answer("Пожалуйста, <b>используйте кнопки 'Да' или 'Нет'</b>, чтобы сделать выбор.")


# --- ⬇️ НОВЫЙ ХЭНДЛЕР ⬇️ ---
@router.callback_query(ReportForm.awaiting_contact_email, F.data == "skip:email")
async def process_email_skip(call: CallbackQuery, state: FSMContext):
    """Обработчик пропуска ввода Email"""
    await state.update_data(email=None)  # Сохраняем email как None
    await call.answer()

    # Переходим к вводу телефона
    await call.message.edit_text(
        "📞 Email пропущен. \n\nТеперь введите ваш <b>контактный номер телефона</b> для связи."
        "\n\n<i>Например: +79991234567</i>",
        reply_markup=get_back_cancel_kb()  # Возвращаем обычную клавиатуру
    )
    await state.set_state(ReportForm.awaiting_contact_phone)


# --- ⬆️ КОНЕЦ НОВОГО ХЭНДЛЕРА ⬆️ ---


# 11. Обработчик EMAIL
@router.message(ReportForm.awaiting_contact_email, F.text.regexp(EMAIL_REGEX))
async def process_email(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(email=message.text)

    data = await state.get_data()
    if data.get("is_editing"):
        if data.get('phone'):
            await message.answer("✅ Email обновлен.")
            await show_confirmation_summary(message, state, bot)
        else:
            await message.answer(
                "✅ Email обновлен. \n\n📞 Теперь введите ваш <b>контактный номер телефона</b>."
                "\n\n<i>Например: +79991234567</i>",
                reply_markup=get_back_cancel_kb()
            )
            await state.set_state(ReportForm.awaiting_contact_phone)
    else:
        # Обычный поток
        await message.answer(
            "📞 Email принят. \n\nТеперь введите ваш <b>контактный номер телефона</b> для связи."
            "\n\n<i>Например: +79991234567</i>",
            reply_markup=get_back_cancel_kb()
        )
        await state.set_state(ReportForm.awaiting_contact_phone)


@router.message(ReportForm.awaiting_contact_email)
async def process_email_invalid(message: Message):
    await message.answer(
        "❗️ <b>Неверный формат email.</b>\n\n"
        "Пожалуйста, введите корректный email (например, <i>example@mail.ru</i>)."
    )


# 12. Обработчик для ТЕЛЕФОНА
@router.message(ReportForm.awaiting_contact_phone, F.text.regexp(PHONE_REGEX))
async def process_phone_and_finish(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(phone=message.text)

    await message.answer(
        "✅ Телефон принят. \n\nСпасибо! Все данные собраны. Давайте сверимся.",
        reply_markup=ReplyKeyboardRemove()
    )
    await show_confirmation_summary(message, state, bot)


# 13. Обработчик невалидного ТЕЛЕФОНА
@router.message(ReportForm.awaiting_contact_phone)
async def process_phone_invalid(message: Message):
    await message.answer(
        "❗️ <b>Формат номера не распознан.</b>\n\n"
        "Пожалуйста, введите номер в формате <b>+79991234567</b> или <b>89991234567</b>."
    )