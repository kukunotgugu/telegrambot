
import os
import telebot
import datetime
from telebot import types

# 从环境变量读取 Telegram Token（Railway 设置的变量名）
TOKEN = os.getenv("TOKEN")
print(f"当前使用的 TOKEN: {TOKEN}")
bot = telebot.TeleBot(TOKEN)

# Default config
config = {
    "welcome": "🎉 欢迎加入本群！记得阅读群规～",
    "keywords": {
        "你好": "你好呀！👋",
        "hi": "Hello! 😃",
        "早上好": "早安☀️祝你今天心情好！",
        "晚安": "晚安🌙做个好梦～",
        "干嘛": "想你了呀～🥰"
    }
}

activity = {}

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    name = message.new_chat_members[0].first_name or "新朋友"
    welcome_text = config.get("welcome", "欢迎来到本群～")
    bot.send_message(message.chat.id, f"{welcome_text}\n👤 {name}")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 设置欢迎语", callback_data="set_welcome"))
    markup.add(types.InlineKeyboardButton("🔁 添加关键词自动回复", callback_data="set_reply"))
    markup.add(types.InlineKeyboardButton("📄 查看当前设定", callback_data="view_config"))
    markup.add(types.InlineKeyboardButton("🗑️ 删除关键词", callback_data="delete_reply"))
    bot.send_message(message.chat.id, "🔧 请选择操作：", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "set_welcome":
        bot.send_message(call.message.chat.id, "📝 请输入新的欢迎语：")
        bot.register_next_step_handler(call.message, save_welcome)
    elif call.data == "set_reply":
        bot.send_message(call.message.chat.id, "🔁 请输入格式：关键词=回复内容")
        bot.register_next_step_handler(call.message, save_reply)
    elif call.data == "view_config":
        view_config(call.message)
    elif call.data == "delete_reply":
        bot.send_message(call.message.chat.id, "🗑️ 请输入要删除的关键词：")
        bot.register_next_step_handler(call.message, delete_reply)

def save_welcome(message):
    config["welcome"] = message.text
    bot.send_message(message.chat.id, "✅ 欢迎语已更新！")

def save_reply(message):
    try:
        keyword, reply = message.text.split("=", 1)
        config["keywords"][keyword.strip()] = reply.strip()
        bot.send_message(message.chat.id, f"✅ 添加自动回复：{keyword.strip()} ➜ {reply.strip()}")
    except:
        bot.send_message(message.chat.id, "❌ 格式错误，请用 关键词=回复内容")

def delete_reply(message):
    keyword = message.text.strip()
    if keyword in config["keywords"]:
        del config["keywords"][keyword]
        bot.send_message(message.chat.id, f"✅ 已删除关键词：{keyword}")
    else:
        bot.send_message(message.chat.id, f"❌ 找不到关键词：{keyword}")

@bot.message_handler(commands=['viewconfig'])
def view_config(message):
    welcome = config.get("welcome", "未设置欢迎语")
    keyword_lines = [f"{k} ➜ {v}" for k, v in config["keywords"].items()]
    keyword_text = "\n".join(keyword_lines) if keyword_lines else "无自动回复设置"
    full_text = f"📄 当前设定：\n\n📝 欢迎语：\n{welcome}\n\n🔁 自动回复关键词：\n{keyword_text}"
    bot.send_message(message.chat.id, full_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "无名氏"
    text = message.text.lower()

    if user_id not in activity:
        activity[user_id] = {'name': username, 'count': 0}
    activity[user_id]['count'] += 1

    for keyword, reply in config["keywords"].items():
        if keyword in text:
            bot.reply_to(message, reply)
            return

    if text == "/rank":
        sorted_activity = sorted(activity.values(), key=lambda x: x['count'], reverse=True)
        rank_text = "🏆 活跃榜 🏆\n\n"
        for i, user in enumerate(sorted_activity[:10], start=1):
            rank_text += f"{i}. {user['name']} - {user['count']}条消息\n"
        bot.reply_to(message, rank_text)

print("Bot is running...")
bot.infinity_polling()
