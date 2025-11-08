# file: states.py
from aiogram.fsm.state import State, StatesGroup

class ReportForm(StatesGroup):
    awaiting_type = State()
    awaiting_media = State()
    awaiting_description = State()
    awaiting_location_choice = State()
    awaiting_location_geo = State()
    awaiting_location_address = State()
    awaiting_name = State()
    awaiting_feedback_choice = State()
    awaiting_contact_email = State()
    awaiting_contact_phone = State()
    awaiting_confirmation = State()