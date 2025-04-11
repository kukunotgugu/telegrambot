import telebot
import threading
import time

# 你的 Bot Token
TOKEN = '7782555253:AAGVtM9WSNLrBpGAXLIX22q3dQOqqDH73oI'

bot = telebot.TeleBot(TOKEN)

# 设置关键词自动回复
keywords = {
    "你好": "你好呀！👋",
    "hi": "Hello! 😃",
    "早上好": "早安☀️祝你今天心情好！",
    "晚安": "晚安🌙做个好梦～",
    "干嘛": "想你了呀～🥰"
}

# 活跃度记录
activity = {}

# 欢迎新成员
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        name = new_member.first_name or "新朋友"
        welcome_text = f"🎉 欢迎 {name} 加入本群！记得阅读群规哦～"
        bot.send_message(message.chat.id, welcome_text)

# 处理普通消息
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "无名氏"
    text = message.text.lower()

    # 更新活跃度
    if user_id not in activity:
        activity[user_id] = {'name': username, 'count': 0}
    activity[user_id]['count'] += 1

    # 关键词自动回复
    for keyword, reply in keywords.items():
        if keyword in text:
            bot.reply_to(message, reply)
            return

    # 查看活跃榜
    if text == "/rank":
        sorted_activity = sorted(activity.values(), key=lambda x: x['count'], reverse=True)
        rank_text = "🏆 活跃榜 🏆\n\n"
        for i, user in enumerate(sorted_activity[:10], start=1):
            rank_text += f"{i}. {user['name']} - {user['count']}条消息\n"
        bot.reply_to(message, rank_text)

# 定时发送消息
def scheduled_message():
    while True:
        try:
            chat_id = -1001234567890  # ⬅️ 把这个换成你自己群的ID！
            bot.send_message(chat_id, "⏰ 提醒：大家记得活跃聊天哦！保持正能量！💬")
            
            time.sleep(3 * 3600)  # 3小时一次（3x3600秒）
        except Exception as e:
            print(f"Error in scheduled_message: {e}")

# 开启定时发送线程
threading.Thread(target=scheduled_message, daemon=True).start()

# 启动bot
print("Bot is running...")
bot.infinity_polling()
