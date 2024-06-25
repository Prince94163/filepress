import requests
import json

url = "https://ddflix.xyz/api/v1/file/add"
api = "ludNTKhd7piX1xvnrJlJ7XXfIOtmsYj2MmEmP9/6xSI="

async def get_ddflix(link):
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

        dd_id = data["data"]["_id"]
        dd_url = "https://ddflix.xyz/file/" + dd_id

        file_name = data["data"]["name"]
        file_size = data["data"]["size"]
        
        return dd_url, file_name, file_size     
