from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
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
filepress_api = "ludNTKhd7piX1xvnrJlJ7XXfIOtmsYj2MmEmP9/6xSI="
ADMINS = 1228255863
GOOGLE_API_KEY = 'AIzaSyBVWzuufxMmsQPpySfeKcTiZlcfd81NX0M'
FOLDER_ID = '1hSAEz0DCZZG3cuomXCiA3GJIXWi6ZCsV'


########################################################################
@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def welcome(client, message):
    message.reply_text(
        text = START_TXT.format(mention = message.from_user.mention)
    )
########################################################################


########################################################################
@bot.on_message(filters.command(["setapi"]) & filters.private)
async def set_api(client, message):
    global api
    try:
        api = message.command[1]
        message.reply_text(f"You have set your api successfully as\n\n<code>{api}</code>")
    except IndexError:
        message.reply_text(f"PUT API KEY WITH COMMAND\n\nExample:- /setapi cuigwudfgywg156235vbchbgujhfgu")
########################################################################



###################### FILEPRESS ######################
FILEPRESS_URL = environ.get("FILEPRESS_URL", "https://filebee.xyz/api/v1/file/add")

def get_filepress(link):
        def extract_file_id(url):
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

        file_id = extract_file_id(link)

        payload = {
            "key": filepress_api,
            "id": file_id
        }
        headers = {}
        response = requests.post(FILEPRESS_URL, headers=headers, json=payload)
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
            fp = get_filepress(link)
            if fp[0] != "":
                short_link = await get_shortlink(fp[0])
                await message.reply(f"<b>FILE NAME:-</b> <code>{fp[1]}</code>\n\n<b>FILE SIZE:-</b> <code>{fp[2]}</code>\n\n<b>FilePress: </b><code>{fp[0]}</code>\n\n<b>GyaniLinks: </b><code>{short_link}</code>")
    except Exception as e:
        await message.reply(f'Error: {e}', quote=True)
########################################################################



########################################################################
def shorten_url(url):
    try:
        api_url = 'https://tinyurl.com/api-create.php'
        params = {'url': url}
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return url  # Return original URL if shortening fails
    except requests.exceptions.RequestException as e:
        print(f"Error shortening URL: {e}")
        return url
    
def shorten_file_name(file_name, max_length=10):
    if len(file_name) > max_length:
        return file_name[:max_length] + '...'
    else:
        return file_name    

def get_folder_id(parent_folder_id, folder_name):
    try:
        params = {
            'q': f"'{parent_folder_id}' in parents and name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'",
            'fields': 'files(id, name)',
            'key': GOOGLE_API_KEY
        }
        
        response = requests.get('https://www.googleapis.com/drive/v3/files', params=params)
        response.raise_for_status()  # Raise an exception for bad responses
        
        data = response.json()
        folders = data.get('files', [])
        
        if folders:
            return folders[0]['id']  # Return the ID of the first matching folder
        else:
            return None  # Folder not found
    
    except requests.exceptions.RequestException as e:
        print(f"Error searching for folder '{folder_name}' in Google Drive: {e}")
        return None

# Function to search Google Drive files recursively within a folder
def search_files(query, parent_folder_id):
    try:
        # Initialize a list to store results
        result_lines = []

        # Helper function to recursively search folders
        def recursive_search(folder_id):
            try:
                # Search for folders and files within the specified folder
                params = {
                    'q': f"'{folder_id}' in parents",
                    'fields': 'files(id, name, webViewLink, mimeType)',
                    'key': GOOGLE_API_KEY
                }
                
                response = requests.get('https://www.googleapis.com/drive/v3/files', params=params)
                response.raise_for_status()  # Raise an exception for bad responses
                
                data = response.json()
                items = data.get('files', [])
                
                for item in items:
                    if item['mimeType'] == 'application/vnd.google-apps.folder':
                        # Recursively search subfolders
                        recursive_search(item['id'])
                    else:
                        # It's a file, check if it contains the query
                        if query.lower() in item.get('name', '').lower():
                            file_name = item.get('name', 'Unknown Name')
                            short_file_name = shorten_file_name(file_name, 15)
                            web_view_link = item.get('webViewLink', 'No webViewLink available')
                            short_web_view_link = shorten_url(web_view_link)
                            fp_view_link = get_filepress(web_view_link)
                            result_lines.append(f"{file_name}: {fp_view_link[0]}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error searching Google Drive: {e}")
        
        # Start recursive search from the root folder (parent_folder_id)
        recursive_search(parent_folder_id)

        if not result_lines:
            return 'No files found.'
        
        # Join results into a single string
        result = '\n'.join(result_lines)
        
        # Check if the result is too long for Telegram
        max_message_length = 4096  # Telegram message length limit
        if len(result) > max_message_length:
            # Split result into chunks that fit within Telegram's limit
            result_chunks = result[:max_message_length - 6] + '...' 
            return result_chunks
        else:
            return result
    
    except requests.exceptions.RequestException as e:
        print(f"Error searching Google Drive: {e}")
        return 'Failed to fetch Google Drive files. Please try again later.'



# Command handler for /search command
@bot.on_message(filters.command('search'))
def search_command(client, message: Message):
    if len(message.command) < 2:
        message.reply_text('Please provide a query to search for.')
        return
    
    query = ' '.join(message.command[1:])
    root_folder_id = '1hSAEz0DCZZG3cuomXCiA3GJIXWi6ZCsV'
    result = search_files(query, root_folder_id)
    message.reply_text(result)    

########################################################################


bot.run()
