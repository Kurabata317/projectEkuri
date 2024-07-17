import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 메시지 조건 확인 함수
def is_valid_message(content):
    if '```' in content:
        return False
    links = [word for word in content.split() if word.startswith("https://twitter.com") or word.startswith("https://x.com")]
    return len(links) == 1

# 메시지의 링크를 수정하는 함수
def modify_link(content):
    return content.replace("https://twitter.com", "https://vxtwitter.com").replace("https://x.com", "https://vxtwitter.com")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    # 보는 중 상태 설정
    activity = discord.Activity(type=discord.ActivityType.watching, name="대책위원회 3장 챕터4 보는 중")
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if is_valid_message(message.content):
        await message.delete()
        modified_content = modify_link(message.content)
        sent_message = await message.channel.send(f'{message.author.mention} {modified_content}')

        original_link = [word for word in message.content.split() if word.startswith("https://twitter.com") or word.startswith("https://x.com")][0]
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Twitter", style=discord.ButtonStyle.link, url=original_link))
        view.add_item(discord.ui.Button(label="X", style=discord.ButtonStyle.link, url=original_link.replace("twitter.com", "x.com")))
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

# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)
