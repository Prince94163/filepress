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
gdtot_api = str(None)
filepress_api = str(None)


########################################################################
@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def welcome(client, message):
    await message.reply_text(
        text = START_TXT.format(mention = message.from_user.mention)
    )
########################################################################



########################################################################
@bot.on_message(filters.command(["setapi_filepress"]) & filters.private)
async def set_api(client, message):
    global filepress_api
    try:
        filepress_api = message.command[1]
        await message.reply_text(f"You have set your api successfully as\n\n<code>{filepress_api}</code>")
    except IndexError:
        await message.reply_text(f"PUT API KEY WITH COMMAND\n\nExample:- /setapi_filepress cuigwudfgywg156235vbchbgujhfgu")



@bot.on_message(filters.command(["setapi_gdtot"]) & filters.private)
async def set_api(client, message):
    global gdtot_api
    try:
        gdtot_api = message.command[1]
        await message.reply_text(f"You have set your api successfully as\n\n<code>{gdtot_api}</code>\n\nDon't forget to add GDTOT Email by use /setgdtot_mail command")
    except IndexError:
        await message.reply_text(f"PUT API KEY WITH COMMAND\n\nExample:- /setapi_gdtot cuigwudfgywg156235vbchbgujhfgu")

@bot.on_message(filters.command(["setgdtot_mail"]) & filters.private)
async def set_mail(client, message):
    global GDTOT_EMAIL
    try:
        GDTOT_EMAIL = message.command[1]
        await message.reply_text(f"You have set your Mail successfully as\n\n<code>{GDTOT_EMAIL}</code>\n\nDon't forget to add GDTOT api by use /setapi_gdtot command")
    except IndexError:
        await message.reply_text(f"PUT API KEY WITH COMMAND\n\nExample:- /setapi_gdtot cuigwudfgywg156235vbchbgujhfgu")

########################################################################



###################### FILEPRESS ######################
FILEPRESS_DOMAIN = environ.get("FILEPRESS_DOMAIN", "filebee.xyz")
FILEPRESS_URL = f"https://{FILEPRESS_DOMAIN}/api/v1/file/add"

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
            "key": filepress_api,
            "id": file_id
        }
        headers = {}
        response = requests.post(FILEPRESS_URL, headers=headers, json=payload)
        response_text = response.text
        data = json.loads(response_text)

        fp_id = data["data"]["_id"]
        fp_url = f"https://{FILEPRESS_DOMAIN}/file/" + fp_id

        file_name = data["data"]["name"]
        file_size = data["data"]["size"]
        
        return fp_url, file_name, file_size
###################### FILEPRESS ######################

###################### GDTOT ######################
GDTOT_DOMAIN = environ.get("GDTOT_DOMAIN", "new4.gdtot.dad")
GDTOT_URL = f"https://{GDTOT_DOMAIN}/api/upload/link"

async def get_gdtot(link):
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
        "api_token": "w3q56J66Sb0AJMNG6ye73ihijB",
        "email": "imab7016@gmail.com",
        "url": file_id  # Assuming the link is a Google Drive link
    }
    headers = {}

    response = requests.post(GDTOT_URL, headers=headers, json=payload)

    if response.status_code == 200:
        response_text = response.text
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print("Error parsing JSON response:", e)
            return None

        if 'data' in data and len(data['data']) > 0:
            gd_id = data['data'][0]['id']
            gd_url = f"https://{GDTOT_DOMAIN}/file/{gd_id}"
        else:
            gd_url = None
    else:
        print("API request failed with status code", response.status_code)
        gd_url = None

    return gd_url
###################### GDTOT ######################



########################################################################
@bot.on_message(filters.regex(r'https?://[^\s]+') & filters.private)
async def link_handler(bot, message):
    link = message.matches[0].group(0)
    try:
        if link.startswith("https://drive.google.com") or link.startswith("http://drive.google.com") or link.startswith("drive.google.com"):
            fp = await get_filepress(link)
            gd = await get_gdtot(link)
            if fp[0] and gd[0] != "":
                await message.reply(f"<b>FILE NAME:-</b> <code>{fp[1]}</code>\n\n<b>FILE SIZE:-</b> <code>{fp[2]}</code>\n\n<b>FilePress: </b><code>{fp[0]}</code>\n\n<b>GDTOT: </b><code>{gd[0]}</code>")
    except Exception as e:
        await message.reply(f'Error: {e}', quote=True)
########################################################################



bot.run()
