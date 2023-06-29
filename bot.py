from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.helper import START_TXT
import aiohttp
from plugins.filepress import get_filepress

api_id = 13115322
api_hash = "f28fbd1367ddda2e6f863c3129323743"
bot_token = "5921362645:AAEOVznXBTwqx6XaASwN855j1rKmlN19Ef8"
bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token,workers=50,sleep_threshold=10)

@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def welcome(client, message):
    await message.reply_text(
        text = START_TXT.format(mention = message.from_user.mention)
    )

@bot.on_message(filters.command(["setapi"]) & filters.private)
async def set_api(client, message):
    global api
    try:
        api = message.command[1]
        await message.reply_text(f"You have set your api successfully as\n\n<code>{api}</code>")
    except IndexError:
        await message.reply_text(f"Sorry, I couldn't process your request")

@bot.on_message(filters.regex(r'https?://[^\s]+') & filters.private)
async def link_handler(bot, message):
    link = message.matches[0].group(0)
    try:
        if link.startswith("https://drive.google.com") or link.startswith("http://drive.google.com") or link.startswith("drive.google.com"):
            fp = await get_filepress(link)
            if fp[0] != "":
                short_link = await get_shortlink(fp[0])
                await message.reply(f"📂 <code>{fp[1]}</code>\n\n<b>FilePress: </b><code>{fp[0]}</code>\n\n<b>GyaniLinks: </b><code>{short_link}</code>")
        else:
            short_link = await get_shortlink(link)
            await message.reply(f"Generated Shortened GyaniLinks:\n\n<code>{short_link}</code>")
    except Exception as e:
        await message.reply(f'Error: {e}', quote=True)

async def get_shortlink(link):
    url = 'https://gyanilinks.com/api'
    params = {'api': api, 'url': link, 'format': 'text'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, raise_for_status=True) as response:
            short_link = await response.text()
            return short_link.strip()

app = Bot()
app.run()
