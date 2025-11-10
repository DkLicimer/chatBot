# file: keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_kb() -> InlineKeyboardMarkup:
    """Клавиатура для /start"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Скопление мусора", callback_data="report_type:garbage")],
            [InlineKeyboardButton(text="💨 Загрязнение воздуха / Запах", callback_data="report_type:air")],
            # --- ИЗМЕНЕНИЕ: Добавлена кнопка-ссылка ---
            [InlineKeyboardButton(
                text="🗓️ Узнать график вывоза мусора",
                url="https://oleron.plus/index.php/grafiki-transportirovki-tko/"
            )]
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
            ],
            # --- ИЗМЕНЕНИЕ: Добавлена кнопка "Домой" ---
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="go_to_start")]
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
            ],
            # --- ИЗМЕНЕНИЕ: Добавлена кнопка "Домой" ---
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="go_to_start")]
        ]
    )


def get_back_cancel_kb() -> InlineKeyboardMarkup:
    """Клавиатура 'Назад' и 'Отменить' для текстовых шагов"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_all")
            ],
            # --- ИЗМЕНЕНИЕ: Добавлена кнопка "Домой" ---
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="go_to_start")]
        ]
    )


def get_cancel_kb() -> InlineKeyboardMarkup:
    """Клавиатура 'Отменить' (используется при редактировании)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить заявку", callback_data="cancel_all")]
        ]
    )


# --- ⬇️ НОВАЯ КЛАВИАТУРА ⬇️ ---
def get_skip_email_kb() -> InlineKeyboardMarkup:
    """Клавиатура для шага ввода email (с кнопкой 'Пропустить')"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Пропустить ввод Email", callback_data="skip:email")],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_all")
            ],
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="go_to_start")]
        ]
    )
# --- ⬆️ КОНЕЦ НОВОЙ КЛАВИАТУРЫ ⬆️ ---


# --- ИЗМЕНЕННАЯ КЛАВИАТУРА ---
def get_rodents_choice_kb(is_editing: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура 'Есть ли грызуны?'"""

    # Условная кнопка "Назад"
    # При редактировании - ведем на сводку, при заполнении - используем "go_back"
    back_button_callback = "edit:back_to_confirm" if is_editing else "go_back"
    back_button = InlineKeyboardButton(text="⬅️ Назад", callback_data=back_button_callback)

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Да, есть", callback_data="rodents:yes"),
                InlineKeyboardButton(text="Нет", callback_data="rodents:no")
            ],
            [
                back_button,  # Условная кнопка
                InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_all")
            ],
            # --- ИЗМЕНЕНИЕ: Добавлена кнопка "Домой" ---
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="go_to_start")]
        ]
    )


def get_confirmation_kb() -> InlineKeyboardMarkup:
    """Клавиатура 'Подтвердить / Редактировать'"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Все верно, отправить", callback_data="confirm:send")],
            [InlineKeyboardButton(text="✏️ Редактировать", callback_data="confirm:edit")],
            # --- ИЗМЕНЕНИЕ: "Отменить" заменено на "Домой" ---
            [InlineKeyboardButton(text="🏠 На главный экран", callback_data="go_to_start")]
        ]
    )


# --- ИЗМЕНЕННАЯ КЛАВИАТУРА ---
def get_edit_kb(is_garbage_report: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования"""

    # Создаем базовый список кнопок
    keyboard_buttons = [
        [InlineKeyboardButton(text="📷 Фото / Видео", callback_data="edit:media")],
        [InlineKeyboardButton(text="📝 Описание", callback_data="edit:description")],
    ]

    # Условная кнопка
    if is_garbage_report:
        keyboard_buttons.append(
            [InlineKeyboardButton(text="🐹 Наличие грызунов", callback_data="edit:rodents")]
        )

    # Добавляем остальные кнопки
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="🗺️ Местоположение", callback_data="edit:location")],
        [InlineKeyboardButton(text="🔔 Статус обратной связи", callback_data="edit:feedback_choice")],
        [InlineKeyboardButton(text="👤 Контактные данные", callback_data="edit:contacts")],
        [InlineKeyboardButton(text="✅ Готово, назад к сводке", callback_data="edit:back_to_confirm")]
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)