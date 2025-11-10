# file: handlers/form_editing.py
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from keyboards import (get_edit_kb, get_cancel_kb, get_location_choice_kb,
                       get_feedback_choice_kb, get_rodents_choice_kb)  # <<< Добавлен импорт
from states import ReportForm
from logic import send_final_report, show_confirmation_summary

router = Router()


# --- Обработчики для шага Подтверждения (awaiting_confirmation) ---

@router.callback_query(ReportForm.awaiting_confirmation, F.data == "confirm:send")
async def process_confirmation_send(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if data.get('wants_feedback') is True and (not data.get('email') or not data.get('phone')):
        await call.answer("❗️ Вы выбрали 'получить обратную связь', но не указали email или телефон. "
                          "Пожалуйста, нажмите 'Редактировать' и 'Контактные данные'.", show_alert=True)
        return

    await state.update_data(is_editing=False)

    await call.message.edit_text(
        "✅ <b>Принято!</b>\n\nСпасибо за вашу помощь. Отправляю заявку в работу...",
        reply_markup=None
    )
    await call.answer()

    await send_final_report(call, state, bot)

    await call.message.answer(
        "Заявка успешно отправлена.",
        reply_markup=ReplyKeyboardRemove()
    )
    await call.message.answer("Чтобы создать новую заявку, просто введите /start.")


@router.callback_query(ReportForm.awaiting_confirmation, F.data == "confirm:edit")
async def process_confirmation_edit(call: CallbackQuery, state: FSMContext):
    await state.update_data(is_editing=True)

    # --- НОВОЕ: Динамическая клавиатура ---
    data = await state.get_data()
    type_text = data.get('complaint_type', '')
    is_garbage = "мусора" in type_text.lower()
    # --- КОНЕЦ НОВОГО ---

    await call.message.edit_text(
        "✏️ <b>Какой пункт вы хотите изменить?</b>",
        reply_markup=get_edit_kb(is_garbage_report=is_garbage)  # <<< Передаем флаг
    )
    await call.answer()


@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:back_to_confirm")
async def process_edit_back_to_confirm(call: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(is_editing=False)
    await show_confirmation_summary(call, state, bot)
    await call.answer()


# --- Обработчики кнопок редактирования ---

@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:media")
async def process_edit_media(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.awaiting_media)
    await call.message.edit_text(
        "📸 Пожалуйста, прикрепите <b>новое фото или видео</b>.",
        reply_markup=get_cancel_kb()
    )
    await call.answer()


@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:description")
async def process_edit_description(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.awaiting_description)
    await call.message.edit_text(
        "✍️ Пожалуйста, введите <b>новое описание</b> проблемы.",
        reply_markup=get_cancel_kb()
    )
    await call.answer()


# --- НОВЫЙ БЛОК: Редактирование грызунов ---
@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:rodents")
async def process_edit_rodents(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.awaiting_rodents_choice)
    await call.message.edit_text(
        "🐹 <b>Были ли замечены грызуны (крысы, мыши)?</b>",
        reply_markup=get_rodents_choice_kb(is_editing=True)  # Передаем флаг
    )
    await call.answer()


# --- КОНЕЦ НОВОГО БЛОКА ---


@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:location")
async def process_edit_location(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.awaiting_location_choice)
    await call.message.edit_text(
        "🗺️ Пожалуйста, <b>выберите способ</b>, как указать новое местоположение.",
        reply_markup=get_location_choice_kb()
    )
    await call.answer()


@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:feedback_choice")
async def process_edit_feedback_choice(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.awaiting_feedback_choice)
    await call.message.edit_text(
        "🔔 Хотите, чтобы мы <b>сообщили вам о решении</b> этой проблемы?",
        reply_markup=get_feedback_choice_kb()
    )
    await call.answer()


@router.callback_query(ReportForm.awaiting_confirmation, F.data == "edit:contacts")
async def process_edit_contacts(call: CallbackQuery, state: FSMContext):
    await state.set_state(ReportForm.awaiting_name)
    await call.message.edit_text(
        "👤 Пожалуйста, введите ваше <b>имя</b>.",
        reply_markup=get_cancel_kb()
    )
    await call.answer()