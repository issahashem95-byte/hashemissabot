import os
import telebot
import yt_dlp

TOKEN = '8608475401:AAEEWiaWRe41KZTls3mXoiNegCwbisKYnZk'
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

    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024,  # حد أقصى 50 ميجابايت للتوافق مع التيليجرام
        'quiet': True,
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

    except Exception as e:
        bot.edit_message_text("حدث خطأ أثناء التحميل، تأكد من صحة الرابط أو حجم الفيديو.", chat_id=status_msg.chat.id, message_id=status_msg.message_id)
        if os.path.exists(output_filename):
            os.remove(output_filename)

bot.infinity_polling()
