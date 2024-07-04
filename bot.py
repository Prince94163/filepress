from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from plugins.helper import START_TXT
import aiohttp
import requests
import json
import logging
from os import environ

logging.basicConfig(level=logging.INFO)

api_id = 24736263
api_hash = "4d53732917b73a6bb89c3b2f2f7b0902"
bot_token = "6683767504:AAFSYlmoMbfCXGAq3qHMDQwdIUUHzy7-TrM"
bot = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token,workers=50,sleep_threshold=10)
api = str(None)


########################################################################
@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def welcome(client, message):
    await message.reply_text(
        text = START_TXT.format(mention = message.from_user.mention)
    )
########################################################################



########################################################################
@bot.on_message(filters.command(["setapi"]) & filters.private)
async def set_api(client, message):
    global api
    try:
        api = message.command[1]
        await message.reply_text(f"You have set your api successfully as\n\n<code>{api}</code>")
    except IndexError:
        await message.reply_text(f"PUT API KEY WITH COMMAND\n\nExample:- /setapi cuigwudfgywg156235vbchbgujhfgu")
########################################################################



###################### FILEPRESS ######################
FILEPRESS_URL = environ.get("FILEPRESS_URL", "https://filebee.xyz/api/v1/file/add")

async def get_filepress(link):
        async def extract_file_id(url):
            file_id = None

            try:
                parts = url.split('/')
                file_id = parts[-2]  # Get the second-to-last part
                
                # If the file ID contains a query parameter, remove it
                if '?' in file_id:
                    file_id = file_id.split('?')[0]
                
                # If the file ID contains an 'open?id=' keyword, remove it
                if 'open?id=' in file_id:
                    file_id = file_id.replace('open?id=', '')

            except Exception as e:
                print("Error extracting file ID:", e)

            return file_id

        file_id = await extract_file_id(link)

        payload = {
            "key": api,
            "id": file_id
        }
        headers = {}
        response = requests.post(url, headers=headers, json=payload)
        response_text = response.text
        data = json.loads(response_text)

        fp_id = data["data"]["_id"]
        fp_url = "https://filebee.xyz/file/" + fp_id

        file_name = data["data"]["name"]
        file_size = data["data"]["size"]
        
        return fp_url, file_name, file_size
###################### FILEPRESS ######################



########################################################################
@bot.on_message(filters.regex(r'https?://[^\s]+') & filters.private)
async def link_handler(bot, message):
    link = message.matches[0].group(0)
    try:
        if link.startswith("https://drive.google.com") or link.startswith("http://drive.google.com") or link.startswith("drive.google.com"):
            fp = await get_filepress(link)
            if fp[0] != "":
                short_link = await get_shortlink(fp[0])
                await message.reply(f"<b>FILE NAME:-</b> <code>{fp[1]}</code>\n\n<b>FILE SIZE:-</b> <code>{fp[2]}</code>\n\n<b>FilePress: </b><code>{fp[0]}</code>\n\n<b>GyaniLinks: </b><code>{short_link}</code>")
    except Exception as e:
        await message.reply(f'Error: {e}', quote=True)
########################################################################



bot.run()
