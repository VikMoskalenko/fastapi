from random import random
import collection
import telebot
import asyncio


API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['help','start'])
async def send_welcome(message):
    await bot.reply_to(message, 'Hi! I can help you to short_url')
    await bot.send_message(message.chat.id, 'Hi! I can help you to short_url')

@bot.message_handler(commands=['stat'])
async def send_stat(message):
    collection_data = collection.find({'user_id': message.from_user.id})
    async for doc in collection_data:
        await bot.send_message(message.chat.id  , f"Short URL: {doc['short_url']} | Long URL: {doc['long_url'][:25]}...  ")
        #await bot.reply_to(message)

@bot.message_handler(func=lambda message: True)
async def echo(message):
    if message.text.startswith('https://') or message.text.startswith('http://'):
        short_url = "".join(
            [random.choice(string.ascii_letters + string.digits) for n in range(5)]
        )
        await collection.insert_one({'short_url': short_url, "long_url": message.text, "user_id": message.from_user.id})
        await bot.reply_to(message, short_url)




asyncio.polling()