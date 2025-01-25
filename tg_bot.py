import string
import os
import random
import motor.motor_asyncio
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import asyncio_helper

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_USER = os.environ.get("MONGO_USER", "root")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", "example")

API_TOKEN = os.environ.get("API_TOKEN")

db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST,27017,username=MONGO_USER, password=MONGO_PASSWORD)
app_db = db_client["url_shortener"]
collection = app_db["urls"]

bot = AsyncTeleBot(API_TOKEN)

@bot.message_handler(commands=['help','start'])
async def send_welcome(message):
    await bot.reply_to(message, 'Hi! I can help you to short_url')
    await bot.send_message(message.chat.id, 'Hi! I can help you to short_url')

@bot.message_handler(commands=['stat'])
async def send_stat(message):
    collection_data = collection.find({'user_id': message.from_user.id})
    async for doc in collection_data:
        await bot.send_message(message.chat.id  , f"Short URL: {doc['short_url']} | Long URL: {doc['long_url'][:25]}... | Clicks: {doc.get('clicks', '-')}  | Edit: http://localhost:8000{doc['short_url']}/{message.from_user.id}/stats")
        #await bot.reply_to(message)

@bot.message_handler(func=lambda message: True)
async def echo(message):
    if message.text.startswith('https://') or message.text.startswith('http://'):
        short_url = "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(5)]
        )
        await collection.insert_one({'short_url': short_url, "long_url": message.text, "user_id": message.from_user.id})
        await bot.reply_to(message, short_url)


if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())