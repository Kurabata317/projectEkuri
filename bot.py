import discord
import re
import json
import os
from discord.ext import commands
from discord.ui import Button, View

# 봇에 사용할 권한 인텐트 설정
intents = discord.Intents.default()
intents.messages = True  # 메시지 이벤트를 받을 수 있도록 설정
intents.message_content = True  # 메시지 내용에 접근할 수 있도록 설정
intents.message_edit = True  # 메시지 수정 이벤트를 받을 수 있도록 설정

bot = commands.Bot(command_prefix='!', intents=intents)

# 트위터 URL 정규 표현식
twitter_url_pattern = re.compile(r"https?://(?:www\.)?(twitter|x)\.com/(\S+)")
button_message_data_file = 'button_message_data.json'

# 데이터를 파일에 저장하는 함수
def save_button_message_data(data):
    with open(button_message_data_file, 'w') as f:
        json.dump(data, f)

# 파일에서 데이터를 불러오는 함수
def load_button_message_data():
    if os.path.exists(button_message_data_file):
        with open(button_message_data_file, 'r') as f:
            return json.load(f)
    return {}

button_message_data = load_button_message_data()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # 봇이 시작될 때 기존 메시지에 대해 버튼을 다시 설정
    for message_id, data in button_message_data.items():
        channel_id, message_id = map(int, message_id.split('-'))
        channel = bot.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)
                await add_buttons_to_message(message, data['author_id'], data['username_and_path'], initialize=False)
            except discord.NotFound:
                pass  # 메시지를 찾을 수 없는 경우 무시

@bot.event
async def on_message(message):
    # 메시지가 봇 자신으로부터 온 것이라면 무시
    if message.author == bot.user:
        return

    await handle_twitter_links(message)

@bot.event
async def on_message_edit(before, after):
    # 메시지가 봇 자신으로부터 온 것이라면 무시
    if after.author == bot.user:
        return

    await handle_twitter_links(after)

async def handle_twitter_links(message):
    # 링크가 백틱 사이에 있는지 확인
    if any(part.startswith("`") and part.endswith("`") for part in re.split(r'(`[^`]*`)', message.content)):
        return

    # 메시지에서 트위터 링크 찾기
    matches = twitter_url_pattern.finditer(message.content)
    for match in matches:
        original_url = match.group(0)
        username_and_path = match.group(2)
        
        # 각 링크 생성
        vx_url = f"https://vxtwitter.com/{username_and_path}"
        
        # 원본 메시지 삭제
        await message.delete()

        # 사용자 멘션과 함께 새로운 메시지 전송
        new_message_content = f'{message.author.mention}\n{message.content.replace(original_url, vx_url)}'
        new_message = await message.channel.send(new_message_content)
        await add_buttons_to_message(new_message, message.author.id, username_and_path)

        # 메시지와 저자의 ID를 저장
        button_message_data[f'{message.channel.id}-{new_message.id}'] = {
            'author_id': message.author.id,
            'username_and_path': username_and_path
        }
        save_button_message_data(button_message_data)

async def add_buttons_to_message(message, author_id, username_and_path, initialize=True):
    view = View()

    twitter_url = f"https://twitter.com/{username_and_path}"
    x_url = f"https://x.com/{username_and_path}"

    # 링크 버튼 생성
    twitter_button = Button(label="Twitter", url=twitter_url, style=discord.ButtonStyle.link)
    x_button = Button(label="X", url=x_url, style=discord.ButtonStyle.link)
    
    # 삭제 버튼 생성
    async def delete_message(interaction):
        if interaction.user.id == author_id:
            await interaction.message.delete()
            del button_message_data[f'{message.channel.id}-{message.id}']
            save_button_message_data(button_message_data)
        else:
            await interaction.response.send_message("이 메시지를 삭제할 권한이 없습니다.", ephemeral=True)
    
    delete_button = Button(label="Delete", style=discord.ButtonStyle.danger)
    delete_button.callback = delete_message
    
    # 링크 버튼 뷰에 추가
    view.add_item(twitter_button)
    view.add_item(x_button)
    view.add_item(delete_button)

    # 초기화 여부에 따라 메시지 수정
    if initialize:
        await message.edit(view=view)
    else:
        await message.edit(view=view, content=message.content)  # 기존 내용을 유지하며 뷰만 갱신

# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)