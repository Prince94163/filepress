from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.helper import START_TXT
import aiohttp
from plugins.filepress import get_filepress
from plugins.gdflix import get_ddflix

api_id = 24736263
api_hash = "4d53732917b73a6bb89c3b2f2f7b0902"
bot_token = "6683767504:AAFSYlmoMbfCXGAq3qHMDQwdIUUHzy7-TrM"
bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token,workers=50,sleep_threshold=10)

@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def welcome(client, message):
    await message.reply_text(
        text = START_TXT.format(mention = message.from_user.mention)
    )

@bot.on_message(filters.command(["setapi_filepress"]) & filters.private)
async def set_api_fp(client, message):
    global filepress_api
    try:
        filepress_api = message.command[1]
        await message.reply_text(f"You have set your api successfully as\n\n<code>{api}</code>")
    except IndexError:
        await message.reply_text(f"Sorry, I couldn't process your request")

@bot.on_message(filters.command(["setapi_gdflix"]) & filters.private)
async def set_api_gd(client, message):
    global api_gdflix
    try:
        api_gdflix = message.command[2]
        await message.reply_text(f"You have set your api successfully as\n\n<code>{api}</code>")
    except IndexError:
        await message.reply_text(f"Sorry, I couldn't process your request")

@bot.on_message(filters.regex(r'https?://[^\s]+') & filters.private)
async def link_handler(bot, message):
    link = message.matches[0].group(0)
    try:
        if link.startswith("https://drive.google.com") or link.startswith("http://drive.google.com") or link.startswith("drive.google.com"):
            fp = await get_filepress(link)
            gd = await get_ddflix(link)
            if fp[0] and gd[0] != "":
                short_link = await get_shortlink(fp[0])
                await message.reply(f"📂 <code>{fp[1]}</code>\n\n<b>FilePress: </b><code>{fp[0]}</code>\n\n<b>GDFlix: </b><code>{gd[0]}</code>\n\n<b>GyaniLinks: </b><code>{short_link}</code>")
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

bot.run()
