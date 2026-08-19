import os
import threading
from flask import Flask
import telebot
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

TOKEN = 'ضع_التوكين_الخاص_بك_هنا'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي رابط أي فيديو وسأقوم بتحميله وإرساله لك 🚀")

@bot.message_handler(func=lambda message: True)
def process_video(message):
    url = message.text.strip()
    
    if not url.startswith("http"):
        bot.reply_to(message, "الرجاء إرسال رابط فيديو صحيح يبدأ بـ http")
        return

    status_msg = bot.reply_to(message, "جاري معالجة الرابط وتحميل الفيديو... ⏳")
    output_filename = f"video_{message.chat.id}.mp4"

    # خيارات التنزيل المحدثة (اختيار صيغة جاهزة وحجم مناسب لتفادي أخطاء FFmpeg)
    ydl_opts = {
        'format': 'b[filesize<=50M]/best[ext=mp4]/best',
        'outtmpl': output_filename,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("جاري رفع الفيديو إلى تيليجرام... 📤", chat_id=status_msg.chat.id, message_id=status_msg.message_id)

        if os.path.exists(output_filename):
            with open(output_filename, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption="تم التحميل بنجاح ✨")
            os.remove(output_filename)
            bot.delete_message(chat_id=status_msg.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("لم يتم العثور على الملف بعد التنزيل.", chat_id=status_msg.chat.id, message_id=status_msg.message_id)

    except Exception as e:
        # إظهار الخطأ الحقيقي للمستخدم لغرض التشخيص
        err_msg = str(e)
        if len(err_msg) > 150:
            err_msg = err_msg[:150] + "..."
        
        bot.edit_message_text(f"❌ حدث خطأ أثناء التحميل:\n`{err_msg}`", chat_id=status_msg.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        
        if os.path.exists(output_filename):
            os.remove(output_filename)

def start_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=start_bot, daemon=True).start()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
