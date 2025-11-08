# file: handlers/common.py
from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from keyboards import (get_start_kb, get_back_cancel_kb, get_location_choice_kb,
                       get_feedback_choice_kb)
from states import ReportForm

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # ... (код cmd_start без изменений)
    await state.clear()
    await message.answer(
        "👋 <b>Здравствуйте!</b>\n\n"
        "Я помогу вам сообщить об экологической проблеме. Пожалуйста, выберите тип проблемы:",
        reply_markup=get_start_kb()
    )
    await state.set_state(ReportForm.awaiting_type)


@router.callback_query(F.data == "cancel_all", StateFilter(ReportForm))
async def cancel_handler_callback(call: CallbackQuery, state: FSMContext):
    # ... (код cancel_handler_callback без изменений)
    await state.clear()
    await call.message.edit_text(
        "Действие отменено. Вы можете создать новую заявку в любой момент, введя /start.",
        reply_markup=None
    )
    await call.answer()


@router.message(F.text == "❌ Отменить", StateFilter(ReportForm))
async def cancel_handler_text(message: Message, state: FSMContext):
    # ... (код cancel_handler_text без изменений)
    await state.clear()
    await message.answer(
        "Действие отменено. Вы можете создать новую заявку в любой момент, введя /start.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.callback_query(F.data == "go_back", StateFilter(ReportForm))
async def back_handler_callback(call: CallbackQuery, state: FSMContext):
    # ... (код back_handler_callback без изменений)
    current_state_str = await state.get_state()
    await call.answer()

    current_state = current_state_str

    if current_state == ReportForm.awaiting_media:
        await state.set_state(ReportForm.awaiting_type)
        await call.message.edit_text(
            "↩️ Вы вернулись к выбору типа проблемы.\n\nПожалуйста, укажите, о чем вы хотите сообщить:",
            reply_markup=get_start_kb()
        )
    elif current_state == ReportForm.awaiting_description:
        await state.set_state(ReportForm.awaiting_media)
        await call.message.edit_text(
            "↩️ Вы вернулись к загрузке фото/видео.\n\nПожалуйста, прикрепите <b>фото или видео</b>.",
            reply_markup=get_back_cancel_kb()
        )
    elif current_state == ReportForm.awaiting_location_choice:
        await state.set_state(ReportForm.awaiting_description)
        await call.message.edit_text(
            "↩️ Вы вернулись к вводу описания.\n\n<b>Добавьте краткое описание</b> проблемы.",
            reply_markup=get_back_cancel_kb()
        )
    elif current_state in [ReportForm.awaiting_location_geo.state, ReportForm.awaiting_location_address.state]:
        await state.set_state(ReportForm.awaiting_location_choice)
        await call.message.edit_text(
            "↩️ Вы вернулись к выбору способа геолокации.\n\nКак вам удобнее указать адрес?",
            reply_markup=get_location_choice_kb()
        )
    elif current_state == ReportForm.awaiting_name:
        await state.set_state(ReportForm.awaiting_location_choice)
        await call.message.edit_text(
            "↩️ Вы вернулись к выбору способа геолокации.",
            reply_markup=get_location_choice_kb()
        )
    elif current_state == ReportForm.awaiting_feedback_choice:
        await state.set_state(ReportForm.awaiting_name)
        await call.message.edit_text(
            "↩️ Вы вернулись к вводу имени.\n\nПожалуйста, введите ваше <b>имя</b>.",
            reply_markup=get_back_cancel_kb()
        )
    elif current_state == ReportForm.awaiting_contact_email:
        await state.set_state(ReportForm.awaiting_feedback_choice)
        await call.message.edit_text(
            "↩️ Вы вернулись к выбору обратной связи.\n\nЖелаете получить ответ по вашей заявке?",
            reply_markup=get_feedback_choice_kb()
        )
    elif current_state == ReportForm.awaiting_contact_phone:
        await state.set_state(ReportForm.awaiting_contact_email)
        await call.message.edit_text(
            "↩️ Вы вернулись к вводу email.\n\nПожалуйста, введите ваш <b>email-адрес</b>."
            "\n\n<i>Например: example@mail.ru</i>",
            reply_markup=get_back_cancel_kb()
        )