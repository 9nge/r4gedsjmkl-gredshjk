import os
import logging
from datetime import datetime
from telebot import TeleBot, types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


BOT_TOKEN = "8850295547:AAF1CxSrrXa0Z0O8OnYVA8_lCM4NRj8CFrU"
ADMIN_ID = 5910026649
GROUP_ID = -1004378562071

bot = TeleBot(BOT_TOKEN)

user_data = {}

logging.basicConfig(level=logging.INFO)

PHOTO_1 = "AgACAgIAAyEFAAMBBPuOFwADLWprgtP4XbyxIkHLuG30Ag-1k3DoAAK5GmsbyYlZS8Cngm-4Ydy3AQADAgADeAADPQQ"
PHOTO_2 = "AgACAgIAAyEFAAMBBPuOFwADM2prgxhcjZfSR3RbSHFvz97sSvqAAAK7GmsbyYlZSxDQKYWYTgPhAQADAgADeAADPQQ"
PHOTO_3 = "AgACAgIAAyEFAAMBBPuOFwADLmprgtPyHJ6aYQdSuFkwSiKtdbFnAAK4GmsbyYlZS11puDPM1ZnhAQADAgADeQADPQQ"


START_TEXT = """Astra Create — уникальный сервер с техническим модом Create и его дополнениями. Города, культы и фракции — всё это ты найдёшь у нас!

Группа проекта: https://t.me/AstraA0o0

Чтобы попасть на сервер, нужно приобрести платную проходку за 99 ₽. Что она даёт?

• уникальную карточку игрока — на выбор доступны два варианта, примеры представлены ниже;

• бессрочный доступ к проекту.

Советуем приобрести проходку сейчас: по мере развития проекта её стоимость будет постепенно увеличиваться.

Вопросы? - @AstraCreate"""

PAYMENT_TEXT = """Реквизиты для оплаты:
Карта Т-Банк: 2200 7021 1797 3201
Получатель: Платон
Сумма: 99 ₽

После оплаты пришлите скриншот чека в этот чат."""

APPROVED_TEXT = """✅ Оплата подтверждена!

Добро пожаловать на сервер Astra Create!

IP:

Правила и полезные ссылки ты найдёшь в нашем Telegram-канале: https://t.me/AstraA0o0

Приятной игры!"""

REJECTED_TEXT = """❌ К сожалению, мы не нашли ваш платеж.

Пожалуйста, проверьте:
1. Правильно ли вы перевели сумму (99 ₽)
2. Правильные ли реквизиты (карта 2200 7021 1797 3201, Платон)

Если вы уверены, что оплатили - отправьте чек ещё раз или свяжитесь с @AstraCreate"""


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Купить проход", callback_data="buy_access"))
    

    bot.send_photo(
        user_id,
        PHOTO_1,
        caption=START_TEXT
    )
    

    bot.send_photo(user_id, PHOTO_2)
    bot.send_photo(user_id, PHOTO_3, reply_markup=keyboard)
    

    user_data[user_id] = {"status": "start"}



@bot.callback_query_handler(func=lambda call: call.data == "buy_access")
def handle_buy(call):
    user_id = call.from_user.id
    
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, "Введите ваш никнейм в Minecraft:")
    
    user_data[user_id]["status"] = "waiting_nick"


@bot.message_handler(func=lambda message: user_data.get(message.from_user.id, {}).get("status") == "waiting_nick")
def handle_nick(message):
    user_id = message.from_user.id
    nick = message.text.strip()
    

    user_data[user_id]["nick"] = nick
    user_data[user_id]["status"] = "waiting_payment"
    

    bot.send_message(user_id, PAYMENT_TEXT)
    bot.send_message(user_id, "📎 После оплаты пришлите скриншот чека в этот чат.")



@bot.message_handler(content_types=['photo'])
def handle_check(message):
    user_id = message.from_user.id
    

    if user_data.get(user_id, {}).get("status") != "waiting_payment":
        bot.reply_to(message, "Вы не начали процесс оплаты. Напишите /start")
        return
    

    nick = user_data[user_id].get("nick", "Неизвестный")
    

    file_id = message.photo[-1].file_id
    user_data[user_id]["check_photo"] = file_id
    user_data[user_id]["status"] = "waiting_approval"
    

    admin_keyboard = InlineKeyboardMarkup()
    admin_keyboard.add(
        InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"approve_{user_id}")
    )
    admin_keyboard.add(
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
    )
    
    admin_text = (
        f"НОВАЯ ЗАЯВКА!\n"
        f"Пользователь: {message.from_user.first_name} (@{message.from_user.username})\n"
        f"Ник: {nick}\n"
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Проверьте баланс карты и подтвердите оплату:"
    )
    

    bot.send_photo(ADMIN_ID, file_id, caption=admin_text, reply_markup=admin_keyboard)
    

    bot.send_message(user_id, "✅ Ваш чек отправлен на проверку. Ожидайте подтверждения!")



@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_") or call.data.startswith("reject_"))
def handle_admin_decision(call):
    admin_id = call.from_user.id
    

    if admin_id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ У вас нет прав для этого действия!")
        return
    

    action, user_id = call.data.split("_")
    user_id = int(user_id)
    
    if action == "approve":

        bot.answer_callback_query(call.id, "✅ Оплата подтверждена!")
        

        bot.send_message(user_id, APPROVED_TEXT)
        

        if GROUP_ID:
            nick = user_data.get(user_id, {}).get("nick", "Игрок")
            bot.send_message(
                GROUP_ID,
                f"Новый игрок **{nick}**.",
                parse_mode="Markdown"
            )
        

        user_data[user_id]["status"] = "approved"
        

        bot.edit_message_caption(
            f"✅ ОПЛАЧЕНО!\n{call.message.caption}",
            chat_id=ADMIN_ID,
            message_id=call.message.message_id
        )
        
    elif action == "reject":

        bot.answer_callback_query(call.id, "❌ Оплата отклонена")
        

        bot.send_message(user_id, REJECTED_TEXT)
        

        user_data[user_id]["status"] = "waiting_payment"
        

        bot.edit_message_caption(
            f"❌ ОТКЛОНЕНО!\n{call.message.caption}",
            chat_id=ADMIN_ID,
            message_id=call.message.message_id
        )



if __name__ == "__main__":
    print("Бот запущен!")
    bot.infinity_polling()