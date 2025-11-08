# file: handlers/__init__.py
from aiogram import Router

from . import common
from . import form_filling
from . import form_editing

router = Router()
router.include_routers(
    common.router,
    form_filling.router,
    form_editing.router
)