from dotenv import load_dotenv
import os
import io
import requests
import discord

load_dotenv()

token = os.environ.get('TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if 'https://medal.tv/' in message.content:
            print(f'Found medal link: {message.content}')
            file = download_medal_clip(message.content)
            if file:
                print(f'Sending medal clip from {message.author}.')
                await message.channel.send(file=discord.File(file, 'output.mp4'))
           
        
        # print(f'Message from {message.author}: {message.content}')

def download_medal_clip(url) -> io.BytesIO:
        url = url.strip()
        if not url:
            print('Invalid URL')
            return
        if 'medal' not in url:
            if '/' not in url:
                url = 'https://medal.tv/clips/' + url
            else:
                print('Invalid URL')
                return

        url = url.replace('?theater=true', '')

        try:
            res = requests.get(url)
            html = res.text
            file_url = html.split('"contentUrl":"')[1].split('","')[0] if '"contentUrl":"' in html else None

            if file_url:
                file = io.BytesIO()

                with requests.get(file_url, stream=True) as response:
                    response.raise_for_status()

                    for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1 MB chunks
                        if chunk:
                           file.write(chunk)
                file.seek(0) # Go back to the start of the file as to read from it in the correct order
                return file
            else:
                print('Error: Most likely, direct link download does not exist')
                return None
        except requests.RequestException as e:
            print(f'Error: {e}')
            return None
 


intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = MyClient(intents=intents)
client.run(token)
