import telebot
import os
import json
import time
from datetime import datetime

# ===== ТОКЕН БОТА =====
TOKEN = "8613094005:AAFsr2hDtUVsZEBIq9qVzyegkEYbjhXO3Hg"
bot = telebot.TeleBot(TOKEN)

# ===== ID ГРУПП =====
GROUP_1_ID = -1003898085095  # ID твоей группы  # ID твоей группы
GROUP_2_ID = -1002993547124  # ID группы "Рей"

# ===== ФАЙЛЫ ДЛЯ ХРАНЕНИЯ =====
USER_FILE = "users.json"
STATS_FILE = "stats.json"

def load_json(file):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

users = load_json(USER_FILE)
stats = load_json(STATS_FILE)

# ===== ПРОВЕРКА НА БОТА =====
def is_bot(user_id):
    try:
        user = bot.get_chat(user_id)
        return user.type == 'bot'
    except:
        return False

# ===== ОСНОВНАЯ ФУНКЦИЯ ПЕРЕСЫЛКИ =====
@bot.message_handler(func=lambda m: True, content_types=[
    'text', 'photo', 'video', 'sticker', 'voice', 'document', 
    'audio', 'animation', 'video_note'
])
def forward_message(m):
    chat_id = m.chat.id
    
    # Игнорируем самого бота
    if m.from_user.id == bot.get_me().id:
        return
    
    # Игнорируем других ботов
    if is_bot(m.from_user.id):
        return
    
    # Определяем, откуда и куда пересылать
    if chat_id == GROUP_1_ID:
        target_chat = GROUP_2_ID
        prefix = "📩 [Из твоей группы]\n\n"
    elif chat_id == GROUP_2_ID:
        target_chat = GROUP_1_ID
        prefix = "📩 [Из группы Рей]\n\n"
    else:
        return
    
    # Сохраняем статистику
    user_id = str(m.from_user.id)
    if user_id not in stats:
        stats[user_id] = {"messages": 0, "first_seen": str(datetime.now())}
    stats[user_id]["messages"] += 1
    save_json(STATS_FILE, stats)
    
    # Получаем имя отправителя
    name = m.from_user.first_name or "Пользователь"
    if m.from_user.username:
        name += f" (@{m.from_user.username})"
    
    # Формируем подпись
    caption = f"{prefix}👤 {name}"
    if m.caption:
        caption += f"\n\n{m.caption}"
    
    # Определяем тип сообщения и отправляем
    try:
        if m.text:
            bot.send_message(target_chat, f"{caption}\n\n{m.text}")
        
        elif m.photo:
            bot.send_photo(target_chat, m.photo[-1].file_id, caption=caption)
        
        elif m.video:
            bot.send_video(target_chat, m.video.file_id, caption=caption)
        
        elif m.sticker:
            bot.send_sticker(target_chat, m.sticker.file_id)
        
        elif m.voice:
            bot.send_voice(target_chat, m.voice.file_id)
        
        elif m.document:
            bot.send_document(target_chat, m.document.file_id, caption=caption)
        
        elif m.audio:
            bot.send_audio(target_chat, m.audio.file_id, caption=caption)
        
        elif m.animation:
            bot.send_animation(target_chat, m.animation.file_id, caption=caption)
        
        elif m.video_note:
            bot.send_video_note(target_chat, m.video_note.file_id)
        
        else:
            bot.send_message(target_chat, f"{caption}\n\n[⚠️ Неподдерживаемый тип]")
        
        print(f"✅ Переслано в {target_chat}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        bot.send_message(target_chat, f"{caption}\n\n[❌ Ошибка отправки]")

# ===== КОМАНДЫ =====
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, 
        "🤖 **Бот-мост работает!**\n\n"
        "📩 Сообщения пересылаются между группами\n"
        "⚠️ Сообщения от других ботов игнорируются\n\n"
        "📌 /groupid — ID этой группы\n"
        "📌 /stats — моя статистика\n"
        "📌 /top — топ пользователей"
    )

@bot.message_handler(commands=['groupid'])
def group_id(m):
    bot.reply_to(m, f"🆔 ID этой группы:\n`{m.chat.id}`")

@bot.message_handler(commands=['stats'])
def stats_cmd(m):
    user_id = str(m.from_user.id)
    if user_id in stats:
        data = stats[user_id]
        bot.reply_to(m, 
            f"📊 **Твоя статистика**\n\n"
            f"💬 Сообщений: {data['messages']}\n"
            f"📅 Первый раз: {data['first_seen']}"
        )
    else:
        bot.reply_to(m, "📊 Ты ещё не писал(а) сообщений!")

@bot.message_handler(commands=['top'])
def top_cmd(m):
    if not stats:
        bot.reply_to(m, "📊 Нет статистики")
        return
    
    sorted_users = sorted(stats.items(), key=lambda x: x[1]['messages'], reverse=True)[:5]
    text = "🏆 **Топ пользователей:**\n\n"
    
    for i, (user_id, data) in enumerate(sorted_users, 1):
        try:
            user = bot.get_chat(int(user_id))
            name = user.first_name or "Unknown"
        except:
            name = "Unknown"
        
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {name} — {data['messages']} сообщений\n"
    
    bot.reply_to(m, text)

@bot.message_handler(commands=['ping'])
def ping(m):
    bot.reply_to(m, "🏓 Понг! Бот работает!")

@bot.message_handler(commands=['help'])
def help_cmd(m):
    bot.reply_to(m,
        "📋 **Доступные команды:**\n\n"
        "/start — Главное меню\n"
        "/groupid — ID этой группы\n"
        "/stats — Твоя статистика\n"
        "/top — Топ пользователей\n"
        "/ping — Проверка бота\n"
        "/help — Помощь\n\n"
        "📩 Бот автоматически пересылает сообщения между группами."
    )

# ===== ЗАПУСК =====
if __name__ == "__main__":
    print("🔄 Бот-мост запущен!")
    print(f"📌 Группа 1 ID: {GROUP_1_ID}")
    print(f"📌 Группа 2 ID: {GROUP_2_ID}")
    print("📩 Пересылает: текст, фото, видео, стикеры, голосовые, документы")
    print("⏳ Ожидание сообщений...")
    bot.infinity_polling()