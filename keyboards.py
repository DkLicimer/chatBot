# file: keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_kb() -> InlineKeyboardMarkup:
    """Клавиатура для /start"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Скопление мусора", callback_data="report_type:garbage")],
            [InlineKeyboardButton(text="💨 Загрязнение воздуха / Запах", callback_data="report_type:air")]
        ]
    )

def get_location_choice_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора способа геолокации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📍 Текущая геолокация", callback_data="loc_choice:geo")],
            [InlineKeyboardButton(text="✍️ Ввести адрес", callback_data="loc_choice:address")],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_all")
            ]
        ]
    )

def get_feedback_choice_kb() -> InlineKeyboardMarkup:
    """Клавиатура запроса обратной связи"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, сообщите мне", callback_data="feedback:yes")],
            [InlineKeyboardButton(text="Нет, не нужно", callback_data="feedback:no")],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_all")
            ]
        ]
    )

def get_back_cancel_kb() -> InlineKeyboardMarkup:
    """Клавиатура 'Назад' и 'Отменить' для текстовых шагов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_all")
            ]
        ]
    )

def get_cancel_kb() -> InlineKeyboardMarkup:
    """Клавиатура 'Отменить' (используется при редактировании)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить заявку", callback_data="cancel_all")]
        ]
    )

def get_confirmation_kb() -> InlineKeyboardMarkup:
    """Клавиатура 'Подтвердить / Редактировать'"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Все верно, отправить", callback_data="confirm:send")],
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data="confirm:edit")],
            [InlineKeyboardButton(text="❌ Отменить заявку", callback_data="cancel_all")]
        ]
    )

def get_edit_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📷 Фото / Видео", callback_data="edit:media")],
            [InlineKeyboardButton(text="📝 Описание", callback_data="edit:description")],
            [InlineKeyboardButton(text="🗺️ Местоположение", callback_data="edit:location")],
            [InlineKeyboardButton(text="🔔 Статус обратной связи", callback_data="edit:feedback_choice")],
            [InlineKeyboardButton(text="👤 Контактные данные", callback_data="edit:contacts")],
            [InlineKeyboardButton(text="✅ Готово, назад к сводке", callback_data="edit:back_to_confirm")]
        ]
    )