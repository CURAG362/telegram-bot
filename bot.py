import telebot
import os
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ===== ФАКЕЛЬНЫЙ ВЕБ-СЕРВЕР (без Flask) =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_web():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# ===== ТОКЕН =====
TOKEN = "8613094005:AAFsr2hDtUVsZEBIq9qVzyegkEYbjhXO3Hg"
bot = telebot.TeleBot(TOKEN)

# ===== ID ГРУПП =====
GROUP_1_ID = -1003898085095
GROUP_2_ID = -1002993547124

# ===== ПРОВЕРКА НА БОТА =====
def is_bot(user_id):
    try:
        return bot.get_chat(user_id).type == 'bot'
    except:
        return False

# ===== ПЕРЕСЫЛКА =====
@bot.message_handler(func=lambda m: True, content_types=[
    'text', 'photo', 'video', 'sticker', 'voice', 'document', 
    'audio', 'animation', 'video_note'
])
def forward(m):
    chat_id = m.chat.id
    
    if m.from_user.id == bot.get_me().id or is_bot(m.from_user.id):
        return
    
    if chat_id == GROUP_1_ID:
        target = GROUP_2_ID
        prefix = "📩 [Из твоей группы]\n\n"
    elif chat_id == GROUP_2_ID:
        target = GROUP_1_ID
        prefix = "📩 [Из группы Рей]\n\n"
    else:
        return
    
    name = m.from_user.first_name or "Пользователь"
    if m.from_user.username:
        name += f" (@{m.from_user.username})"
    
    caption = f"{prefix}👤 {name}"
    if m.caption:
        caption += f"\n\n{m.caption}"
    
    try:
        if m.text:
            bot.send_message(target, f"{caption}\n\n{m.text}")
        elif m.photo:
            bot.send_photo(target, m.photo[-1].file_id, caption=caption)
        elif m.video:
            bot.send_video(target, m.video.file_id, caption=caption)
        elif m.sticker:
            bot.send_sticker(target, m.sticker.file_id)
        elif m.voice:
            bot.send_voice(target, m.voice.file_id)
        elif m.document:
            bot.send_document(target, m.document.file_id, caption=caption)
        elif m.audio:
            bot.send_audio(target, m.audio.file_id, caption=caption)
        elif m.animation:
            bot.send_animation(target, m.animation.file_id, caption=caption)
        elif m.video_note:
            bot.send_video_note(target, m.video_note.file_id)
        else:
            bot.send_message(target, f"{caption}\n\n[⚠️ Неподдерживаемый тип]")
    except Exception as e:
        print(f"❌ {e}")

# ===== ЗАПУСК =====
if __name__ == "__main__":
    print("🔄 Бот-мост запущен!")
    bot.infinity_polling()
