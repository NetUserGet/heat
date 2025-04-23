from dotenv import load_dotenv
from sys import exit
import os
import io
import requests
import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content
        
        if 'https://medal.tv/' in content:
            # Splits by whitespace then checks which item contains the medal link, only downside being that it breaks on the first link it sees.
            for item in content.split(" "):
                if 'https://medal.tv/' in item:
                    link = item
                    break;

            print(f'Found medal link: {link}')
            file = download_medal_clip(link)
            if file:
                print(f'Sending medal clip from {message.author}.')
                try:
                    await message.channel.send(file=discord.File(file, 'output.mp4'))
                    file.close()
                except discord.HTTPException as e:
                    await message.channel.send(f'Could not upload file due to {e}!')
                    file.close()
           
        
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
 

if __name__ == '__main__':
    
    if os.path.exists('.env') == False:
        print('No .env file found, creating .env file')
        try:
            with open('.env', 'w') as f:
                f.write("TOKEN=TOKENGOESHERE")
        except OSError as e:
            print(f'Cannot write .env file, because {e}!')
            exit(1)
        print('Paste your token where "TOKENGOESHERE" is then run main.py again to start the bot.')
        exit(1)

    load_dotenv()
    
    token = os.environ.get('TOKEN')


    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    
    client = MyClient(intents=intents)
    client.run(token)
