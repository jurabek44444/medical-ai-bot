import os
import telebot
import requests
from flask import Flask, request

# KALITLARNI SHU YERGA QO'YING
TELEGRAM_TOKEN = "8634010470:AAEVssJr-8Or71jnjg4DNKeYc2OkbupFOKQ"
GROQ_API_KEY = "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"
SERVER_URL = "https://medical-ai-bot-8zk8.onrender.com"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Groq API bilan ishlash funksiyasi
def ask_groq(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-70b-versatile", # Kuchli va aqlli model
        "messages": [
            {
                "role": "system",
                "content": "Sen tibbiyot va dori vositalari (farmakologiya) sohasi mutaxassisisan. Foydalanuvchi yozgan har qanday mavzuni professional darajada, slaydma-slayd bo'lingan prezentatsiya matni ko'rinishida o'zbek tilida yozib ber."
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()['choices'][0]['message']['content']

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Men TFI talabalari uchun tibbiy prezentatsiyalar tayyorlovchi AI botman. Mavzuni yozing:")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        ai_response = ask_groq(message.text)
        bot.reply_to(message, ai_response)
    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {e}")

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

if name == "main":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
