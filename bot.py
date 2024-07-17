import json
import re
import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = 'YOUR_BOT_TOKEN'  # 봇 토큰을 여기에 입력하세요.

# 본래 메시지를 전송할 함수
async def resend_message(channel, original_author, original_content, modified_content):
    class ResendView(View):
        def __init__(self, author_id):
            super().__init__(timeout=None)
            self.author_id = author_id

        @discord.ui.button(label="Twitter", style=discord.ButtonStyle.link, url="https://twitter.com")
        async def twitter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            pass

        @discord.ui.button(label="X", style=discord.ButtonStyle.link, url="https://x.com")
        async def x_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            pass

        @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
        async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id == self.author_id:
                await interaction.message.delete()
            else:
                await interaction.response.send_message("You do not have permission to delete this message.", ephemeral=True)

    await channel.send(f"@{original_author.mention}\n{modified_content}", view=ResendView(original_author.id))

# 메시지 수정 함수
def modify_links(content):
    pattern_twitter = re.compile(r'(https://twitter\.com\S*)')
    pattern_x = re.compile(r'(https://x\.com\S*)')
    
    modified_content = pattern_twitter.sub(r'https://vxtwitter.com\1', content)
    modified_content = pattern_x.sub(r'https://vxtwitter.com\1', modified_content)
    
    return modified_content

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if ("https://twitter.com" in message.content or "https://x.com" in message.content) and "`" not in message.content:
        original_content = message.content
        modified_content = modify_links(original_content)
        await message.delete()
        await resend_message(message.channel, message.author, original_content, modified_content)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if after.author == bot.user:
        return

    if ("https://twitter.com" in after.content or "https://x.com" in after.content) and "`" not in after.content:
        original_content = after.content
        modified_content = modify_links(original_content)
        await after.delete()
        await resend_message(after.channel, after.author, original_content, modified_content)

bot.run(TOKEN)

# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)
