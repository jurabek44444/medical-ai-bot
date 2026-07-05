import os
import telebot
import google.generativeai as genai
from flask import Flask, request

# Kalitlarni xavfsizlik uchun server muhitidan olamiz
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_KEY")
SERVER_URL = os.environ.get("SERVER_URL") # Render beradigan havola

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_KEY)

app = Flask(__name__)

system_instruction = (
    "Sen tibbiyot va farmakologiya sohasi mutaxassisisan. "
    "Foydalanuvchi yozgan mavzuni slaydma-slayd bo'lingan prezentatsiya matni ko'rinishida yozib ber."
)
model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=system_instruction)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men tibbiy prezentatsiyalar tayyorlovchi AI botman. Mavzuni yozing:")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Xatolik yuz berdi. Birozdan so'ng urinib ko'ring.")

# Server uchun Webhook sozlamalari (Avtomatik ishlash uchun)
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=SERVER_URL + '/' + TELEGRAM_TOKEN)
    return "Bot ishlamoqda!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
