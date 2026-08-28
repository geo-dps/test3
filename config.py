
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import KeyboardButtonRequestUsers

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Мой огонёк",callback_data="status")],
        [InlineKeyboardButton(text="👤 Выбрать контакт",callback_data="choose")],
        [InlineKeyboardButton(text="📨 Пригласить на огонёк",callback_data="invite")],
        [InlineKeyboardButton(text="🔕 Уведомления",callback_data="notifications")],
    ])

def choose_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text="👤 Выбрать человека",
            request_users=KeyboardButtonRequestUsers(
                request_id=1001,
                user_is_bot=False,
                max_quantity=1
            ))
    ]],resize_keyboard=True,one_time_keyboard=True)

def contact_buttons(rows):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=(r["name"] or f"ID {r['contact_id']}")[:35],
                              callback_data=f"pick:{r['contact_id']}")]
        for r in rows
    ])

def streak_text(name, days, owner_spoke=False, contact_spoke=False):
    if owner_spoke and contact_spoke:
        state="🔥 Огонёк горит"
    elif owner_spoke or contact_spoke:
        state="⏳ Ждём второго"
    else:
        state="⚪ Сегодня ещё не началось"
    return (f"🔥 <b>ОГОНЁК</b>\n\n"
            f"С контактом: <b>{name}</b>\n"
            f"Серия: <b>{days} {'день' if days==1 else 'дня' if days<5 else 'дней'}</b>\n"
            f"Статус: {state}\n\n"
            f"Вы: {'✅' if owner_spoke else '❌'}\n"
            f"Контакт: {'✅' if contact_spoke else '❌'}\n\n"
            f"<i>День засчитывается только если вы оба написали сегодня.</i>")
