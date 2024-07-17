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
    global button_message_data  # 전역 변수로 선언된 button_message_data를 사용합니다.
    
    to_delete = []  # 삭제할 아이템을 저장할 리스트를 만듭니다.
    
    # 반복문 안에서 삭제를 진행하지 않고, 삭제할 아이템을 리스트에 추가합니다.
    for message_id, author_id in button_message_data.items():
        # 삭제 조건을 여기에 추가합니다.
        to_delete.append(message_id)
    
    # 반복문이 끝나면 to_delete에 저장된 아이템을 삭제합니다.
    for message_id in to_delete:
        del button_message_data[message_id]
        save_button_message_data(button_message_data)


@bot.event
async def on_message(message):
    # 메시지가 봇 자신으로부터 온 것이라면 무시
    if message.author == bot.user:
        return

    # 메시지를 콘솔에 출력
    # print(f'Message from {message.author}: {message.content}')
    
    # 메시지에서 트위터 링크 찾기
    matches = twitter_url_pattern.finditer(message.content)
    for match in matches:
        original_url = match.group(0)
        username_and_path = match.group(2)
        
        # 각 링크 생성
        vx_url = f"https://vxtwitter.com/{username_and_path}"
        # twitter_url = f"https://twitter.com/{username_and_path}"
        # x_url = f"https://x.com/{username_and_path}"
        
        # 원본 메시지 삭제
        await message.delete()

        # 사용자 멘션과 함께 새로운 메시지 전송
        new_message_content = f'{message.author.mention}\n{message.content.replace(original_url, vx_url)}'
        new_message = await message.channel.send(new_message_content)
        await add_buttons_to_message(new_message, message.author.id)

        # 메시지와 저자의 ID를 저장
        button_message_data[f'{message.channel.id}-{new_message.id}'] = message.author.id
        save_button_message_data(button_message_data)
        # print(f'Sent edited message from {message.author}: {new_message_content}')

async def add_buttons_to_message(message, author_id):
    view = discord.ui.View()

    matches = twitter_url_pattern.finditer(message.content)
    buttons = []  # 버튼을 담을 리스트
    
    for match in matches:
        username_and_path = match.group(2)  # 사용자 이름 및 경로 추출
    
        # 링크 버튼 생성
        twitter_button = discord.ui.Button(
            label="Twitter",
            url=f"https://twitter.com/{username_and_path}",
            style=discord.ButtonStyle.link
        )
        x_button = discord.ui.Button(
            label="X",
            url=f"https://x.com/{username_and_path}",
            style=discord.ButtonStyle.link
        )
        
        buttons.append(twitter_button)
        buttons.append(x_button)
    
    # 삭제 버튼 생성 및 콜백 함수 설정
    async def delete_message(interaction):
        if interaction.user.id == author_id:
            await interaction.message.delete()
            # 삭제 버튼을 누르면 해당 메시지와 관련된 데이터 삭제
            del button_message_data[f'{message.channel.id}-{message.id}']
            save_button_message_data(button_message_data)
        else:
            await interaction.response.send_message("이 메시지를 삭제할 권한이 없습니다.", ephemeral=True)
    
    delete_button = discord.ui.Button(
        label="Delete",
        style=discord.ButtonStyle.danger,
    )
    delete_button.callback = delete_message
    
    buttons.append(delete_button)
    
    # 버튼 리스트를 한 번에 view에 추가
    view.add_items(*buttons)

    # 메시지에 뷰 적용
    await message.edit(view=view)


# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)