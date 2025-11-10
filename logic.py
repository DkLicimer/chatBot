# file: logic.py
import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from io import BytesIO

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from config import (SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD,
                    RECIPIENT_EMAIL, admin_group_id)
from keyboards import get_confirmation_kb
from states import ReportForm


def escape_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_email_sync(msg: MIMEMultipart):
    with smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT)) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


async def send_email_notification(data: dict, file_content: BytesIO | None, file_name: str | None):
    if not all([SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        logging.warning("Настройки SMTP для отправки email не сконфигурированы в .env. Письмо не будет отправлено.")
        return
    try:
        user_info = escape_html(data.get('user_info', 'Не указан'))
        user_name = escape_html(data.get('name', 'Не указано'))
        user_phone = escape_html(data.get('phone', 'Не указано'))
        user_email = escape_html(data.get('email', 'Не указано'))
        complaint_type = escape_html(data.get('complaint_type', 'Тип не указан'))
        description = escape_html(data.get('description', 'Без описания'))

        location_info = "Не указано"
        if data.get('latitude') and data.get('longitude'):
            lat = data['latitude']
            lon = data['longitude']
            location_info = f'<a href="http://googleusercontent.com/maps/google.com/1{lat},{lon}">Открыть на карте (Геометка)</a>'
        elif data.get('address_text'):
            location_info = f"<b>Адрес (вручную):</b> {escape_html(data.get('address_text'))}"

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Новая заявка ({complaint_type}) от {user_name}"

        html_body = f"""
        <html>
        <body>
            <h2>🚨 Новая заявка: {complaint_type}</h2>
            <p><strong>От пользователя:</strong> {user_info}</p>
            <h3>Описание проблемы:</h3>
            <p>{description.replace(chr(10), "<br>")}</p>
"""

        if data.get('rodents') is not None:
            rodents_text = 'Да' if data.get('rodents') else 'Нет'
            html_body += f"<p><strong>Наличие грызунов:</strong> {rodents_text}</p>"

        html_body += f"""
            <h3>Контактные данные:</h3>
            <ul>
                <li><strong>Имя:</strong> {user_name}</li>
        """

        # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
        if data.get('wants_feedback') is True:
            html_body += f"""
                <li><strong><u>Обратная связь: Требуется</u></strong></li>
                <li><strong>Телефон:</strong> {user_phone}</li>
                <li><strong>Email:</strong> {user_email}</li>
            """
        else:
            html_body += "<li><i>Обратная связь не требуется</i></li>"
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---

        html_body += f"""
            </ul>
            <h3>Местоположение:</h3>
            <p>{location_info}</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        if file_content and file_name:
            file_content.seek(0)
            attachment = MIMEApplication(file_content.read(), Name=file_name)
            attachment['Content-Disposition'] = f'attachment; filename="{file_name}"'
            msg.attach(attachment)

        await asyncio.to_thread(send_email_sync, msg)
        logging.info(f"Заявка успешно отправлена на email: {RECIPIENT_EMAIL}")
    except Exception as e:
        logging.error(f"Ошибка при отправке email: {e}")


async def show_confirmation_summary(message_or_call, state: FSMContext, bot: Bot):
    # Эта функция НЕ изменилась, она уже работала правильно
    await state.set_state(ReportForm.awaiting_confirmation)
    data = await state.get_data()

    chat_id = None
    text_message_to_delete_id = None

    if isinstance(message_or_call, Message):
        chat_id = message_or_call.chat.id
    elif isinstance(message_or_call, CallbackQuery):
        chat_id = message_or_call.message.chat.id
        text_message_to_delete_id = message_or_call.message.message_id
    else:
        logging.error("Invalid object passed to show_confirmation_summary")
        return

    old_media_msg_id = data.get('media_summary_message_id')

    if text_message_to_delete_id:
        try:
            await bot.delete_message(chat_id, text_message_to_delete_id)
        except Exception:
            pass

    if old_media_msg_id:
        try:
            await bot.delete_message(chat_id, old_media_msg_id)
        except Exception:
            pass

    safe_type = escape_html(data.get('complaint_type', 'Не указан'))
    safe_description = escape_html(data.get('description', 'Не указано'))

    media_status = "❌ Не прикреплено"
    media_type = data.get('media_type')
    file_id = data.get(f'{media_type}_id')

    if file_id:
        media_status = f"✅ {'Фото' if media_type == 'photo' else 'Видео'} прикреплено (см. выше)"

    loc_status = "❌ Не указано"
    if data.get('latitude') and data.get('longitude'):
        loc_status = f"✅ Геометка: ({data['latitude']:.5f}, {data['longitude']:.5f})"
    elif data.get('address_text'):
        loc_status = f"✅ Адрес: {escape_html(data.get('address_text'))}"

    safe_name = escape_html(data.get('name', '⚠️ <b>Не указано</b>'))
    contact_status_parts = [f"<b>Имя:</b> {safe_name}"]
    wants_feedback = data.get('wants_feedback')

    if wants_feedback is True:
        user_email = data.get('email')
        user_phone = data.get('phone')
        safe_email = escape_html(user_email) if user_email else "⚠️ <b>Не указан</b>"
        safe_phone = escape_html(user_phone) if user_phone else "⚠️ <b>Не указан</b>"

        contact_status_parts.append("Обратная связь: <b>Требуется</b>")
        contact_status_parts.append(f"<b>Email:</b> {safe_email}")
        contact_status_parts.append(f"<b>Телефон:</b> {safe_phone}")

    elif wants_feedback is False:
        contact_status_parts.append("Обратная связь: <b>Не требуется</b>")
    else:
        contact_status_parts.append("<i>(Выбор обратной связи не сделан)</i>")

    contact_status = "\n".join(contact_status_parts)

    rodents_status = ""
    rodents_data = data.get('rodents')
    if rodents_data is not None:
        rodents_status = f"<b>🐹 Наличие грызунов:</b> {'Да' if rodents_data else 'Нет'}"

    summary_text_parts = [
        "<b>🔍 Пожалуйста, проверьте и подтвердите вашу заявку:</b>\n",
        f"<b>Тип:</b> {safe_type}",
        f"<b>Медиа:</b> {media_status}",
        f"<b>Описание:</b>\n{safe_description}",
    ]

    if rodents_status:
        summary_text_parts.append(rodents_status)

    summary_text_parts.extend([
        f"<b>Местоположение:</b> {loc_status}",
        "\n<b>Контакты:</b>",
        contact_status
    ])
    summary_text = "\n\n".join(summary_text_parts)

    new_media_msg = None
    if file_id:
        try:
            if media_type == 'photo':
                new_media_msg = await bot.send_photo(chat_id, file_id)
            elif media_type == 'video':
                new_media_msg = await bot.send_video(chat_id, file_id)
        except Exception as e:
            logging.error(f"Failed to send media in summary: {e}")
            summary_text += "\n\n❗️ (Не удалось загрузить превью медиа)"

    await state.update_data(
        media_summary_message_id=(new_media_msg.message_id if new_media_msg else None)
    )

    await bot.send_message(chat_id, summary_text, reply_markup=get_confirmation_kb())


async def send_final_report(call: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_chat_action(chat_id=call.from_user.id, action=ChatAction.TYPING)

    data = await state.get_data()

    user = call.from_user
    user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
    data['user_info'] = user_info

    safe_type = escape_html(data.get('complaint_type', 'Не указан').replace("🗑 ", "").replace("💨 ", ""))
    safe_name = escape_html(data.get('name', 'Не указано'))
    safe_user_info = escape_html(user_info)
    safe_phone = escape_html(data.get('phone', ''))
    safe_email = escape_html(data.get('email', ''))
    safe_description = escape_html(data.get('description', 'Не указано'))

    caption_parts = [
        f"🚨 <b>Новая заявка: {safe_type}</b>",
        f"От: {safe_user_info}",
        f"<b>Имя:</b> {safe_name}"
    ]

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    if data.get('wants_feedback') is True:
        caption_parts.append("<b>Обратная связь: <u>Требуется</u></b>")
        caption_parts.append(f"<b>Телефон:</b> {safe_phone}")
        caption_parts.append(f"<b>Email:</b> {safe_email}")
    else:
        caption_parts.append("<i>Обратная связь не требуется</i>")
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---

    caption_parts.append(f"<b>Описание:</b>\n{safe_description}")

    rodents_data = data.get('rodents')
    if rodents_data is not None:
        rodents_text = 'Да' if rodents_data else 'Нет'
        caption_parts.append(f"<b>🐹 Наличие грызунов:</b> {rodents_text}")

    location_caption_part = ""
    if data.get('latitude'):
        location_caption_part = "<b>Местоположение:</b> Геометка (см. ниже)"
    elif data.get('address_text'):
        safe_address = escape_html(data.get('address_text'))
        location_caption_part = f"<b>Адрес (вручную):</b>\n{safe_address}"

    caption_parts.append(location_caption_part)
    caption = "\n\n".join(caption_parts)

    try:
        file_content_for_email = None
        file_name_for_email = None
        media_type = data.get('media_type')
        file_id = data.get('photo_id') if media_type == 'photo' else data.get('video_id')

        if file_id:
            file_info = await bot.get_file(file_id)
            file_name_for_email = file_info.file_path.split('/')[-1]
            file_content_for_email = await bot.download_file(file_info.file_path, BytesIO())

        logging.info(f"Отправка заявки в группу {admin_group_id}")

        if media_type == 'photo':
            await bot.send_photo(chat_id=admin_group_id, photo=file_id, caption=caption)
        elif media_type == 'video':
            await bot.send_video(chat_id=admin_group_id, video=file_id, caption=caption)

        if data.get('latitude'):
            await bot.send_location(
                chat_id=admin_group_id,
                latitude=data.get('latitude'),
                longitude=data.get('longitude')
            )

        asyncio.create_task(send_email_notification(data, file_content_for_email, file_name_for_email))

    except Exception as e:
        logging.error(f"Не удалось отправить заявку в группу {admin_group_id}: {e}")
        await call.message.answer(
            "❗️ <b>Произошла ошибка</b>\n\n"
            "К сожалению, не удалось отправить вашу заявку. Пожалуйста, попробуйте снова через несколько минут.",
            reply_markup=ReplyKeyboardRemove()
        )
    finally:
        await state.clear()