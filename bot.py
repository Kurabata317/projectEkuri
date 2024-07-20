import json
import re
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 정규식 패턴
pattern = r"(?<!`)(https://twitter\.com/|https://x\.com/)[a-zA-Z_0-9]+/status/[^`]*(?<!`)$"

# 메시지 조건 확인 함수
def is_valid_message(content, return_type):
    if content.startswith('// ignore'):
        return False

    findcount = 0

    link = None
    for word in content.split():
        if re.fullmatch(pattern, word):
            wdsp = word.split("https://")
            findcount = findcount + 1
            
            if findcount == 1:
                link = "https://" + wdsp[1]

    if findcount == 1:
        if return_type == "s":
            return link
        else:
            return True
    else:
        if return_type == "s":
            return None
        else:
            return False

# 메시지의 링크를 수정하는 함수
def modify_link(content):
    # 문자열을 단어 단위로 분리
    words = content.split()
    return_content = content

    for word in words:
        if re.fullmatch(pattern, word):
            # 트위터 링크라면 변경
            conv_word = word.replace("https://twitter.com", "https://vxtwitter.com").replace("https://x.com", "https://vxtwitter.com")

            migihidari = content.split("https://")
            if content.startswith(("스포)", "!스포", "!s", "s_")) and(
                len(migihidari) == 2 and migihidari[0].count("||") % 2 == 1 and migihidari[1].count("||") % 2 == 1
            ) == False:
                # 스포 시 링크 가리기
                conv_word = "||"+conv_word+"||"
                
            return_content = return_content.replace(word, conv_word)
    
    return return_content

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    # 보는 중 상태 설정
    activity = discord.Activity(type=discord.ActivityType.watching, name="대책위원회 3장 챕터4")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 메시지 내용이 JSON 응답 키 중 하나와 일치하는지 확인
    response = responses.get(message.content)
    if response:
        await message.channel.send(response)
        
    elif is_valid_message(message.content, "b"):
        await message.delete()
        modified_content = modify_link(message.content)
        sent_message = await message.channel.send(f'{message.author.mention}\n{modified_content}')

        original_link = is_valid_message(message.content, "s")
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Open", style=discord.ButtonStyle.link, url=original_link.replace("x.com", "twitter.com")))
        view.add_item(discord.ui.Button(label="Delete", style=discord.ButtonStyle.danger, custom_id=f"delete_{sent_message.id}"))

        await sent_message.edit(view=view)
        
@bot.event
async def on_interaction(interaction):
    if interaction.data['custom_id'].startswith("delete_"):
        message_id = int(interaction.data['custom_id'].split("_")[1])
        message = await interaction.channel.fetch_message(message_id)
        if message.mentions[0].id == interaction.user.id:
            await message.delete()
            await interaction.response.send_message("메시지가 삭제되었습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("권한이 없습니다.", ephemeral=True)

# JSON 파일에서 대화 내역 별 응답을 로드
with open('responses.json', 'r', encoding='utf-8') as f:
    responses = json.load(f)

# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)
