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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

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
        
        # 원본 메시지 삭제
        await message.delete()

        # 사용자 멘션과 함께 새로운 메시지 전송
        new_message_content = f'{message.author.mention}\n{message.content.replace(original_url, vx_url)}'
        new_message = await message.channel.send(new_message_content)
        await add_buttons_to_message(new_message, message.author.id)

async def add_buttons_to_message(message, author_id):
    # 새 View 객체 생성
    view = discord.ui.View()

    # 메시지 내용에서 모든 Twitter URL 매칭 찾기
    matches = twitter_url_pattern.finditer(message.content)
    count = 1  # 버튼 레이블을 위한 카운터

    for match in matches:
        username_and_path = match.group(2)  # 사용자 이름 및 경로 추출

        # Twitter 링크 버튼 생성
        twitter_button = discord.ui.Button(
            label=f"Twitter({count})",
            url=f"https://twitter.com/{username_and_path}",
            style=discord.ButtonStyle.link
        )

        # X 링크 버튼 생성
        x_button = discord.ui.Button(
            label=f"X({count})",
            url=f"https://x.com/{username_and_path}",
            style=discord.ButtonStyle.link
        )

        # View에 버튼 추가
        view.add_item(twitter_button)
        view.add_item(x_button)

        count += 1  # 버튼 카운터 증가

    # 삭제 버튼 콜백 함수 정의
    async def delete_message(interaction):
        if interaction.user.id == author_id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message("이 메시지를 삭제할 권한이 없습니다.", ephemeral=True)

    # 삭제 버튼 생성 및 콜백 설정
    delete_button = discord.ui.Button(
        label="Delete",
        style=discord.ButtonStyle.danger,
    )
    delete_button.callback = delete_message

    # View에 삭제 버튼 추가
    view.add_item(delete_button)

    # View를 메시지에 적용
    await message.edit(view=view)

# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)
