import telebot
import threading
import time
import datetime
from telebot import types

TOKEN = '7782555253:AAGVtM9WSNLrBpGAXLIX22q3dQOqqDH73oI'
bot = telebot.TeleBot(TOKEN)

keywords = {
    "你好": "你好呀！👋",
    "hi": "Hello! 😃",
    "早上好": "早安☀️祝你今天心情好！",
    "晚安": "晚安🌙做个好梦～",
    "干嘛": "想你了呀～🥰"
}

activity = {}

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        name = new_member.first_name or "新朋友"
        welcome_text = f"🎉 欢迎 {name} 加入本群！记得阅读群规哦～"
        bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['menu'])
def send_menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📊 活跃榜", callback_data="rank")
    btn2 = types.InlineKeyboardButton("🕓 当前时间", callback_data="time")
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, "请选择一个操作：", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "rank":
        sorted_activity = sorted(activity.values(), key=lambda x: x['count'], reverse=True)
        rank_text = "🏆 活跃榜 🏆\n\n"
        for i, user in enumerate(sorted_activity[:10], start=1):
            rank_text += f"{i}. {user['name']} - {user['count']}条消息\n"
        bot.send_message(call.message.chat.id, rank_text)
    elif call.data == "time":
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bot.send_message(call.message.chat.id, f"🕓 当前时间：{now}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "无名氏"
    text = message.text.lower()

    print("🆔 Chat ID:", message.chat.id)

    if user_id not in activity:
        activity[user_id] = {'name': username, 'count': 0}
    activity[user_id]['count'] += 1

    for keyword, reply in keywords.items():
        if keyword in text:
            bot.reply_to(message, reply)
            return

    if text == "/rank":
        sorted_activity = sorted(activity.values(), key=lambda x: x['count'], reverse=True)
        rank_text = "🏆 活跃榜 🏆\n\n"
        for i, user in enumerate(sorted_activity[:10], start=1):
            rank_text += f"{i}. {user['name']} - {user['count']}条消息\n"
        bot.reply_to(message, rank_text)

# ❌ 定时发消息功能完全删除（确保不再报错）

print("Bot is running...")
bot.infinity_polling()
