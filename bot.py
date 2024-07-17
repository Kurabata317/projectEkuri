import json
import discord
from discord.ext import commands
from discord.ui import Button, View
import re

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = 'YOUR_BOT_TOKEN'  # 봇 토큰을 여기에 입력하세요.

# 본래 메시지를 전송할 함수
async def resend_message(channel, original_author, modified_content, link_info):
    class ResendView(View):
        def __init__(self, author_id, twitter_url, x_url):
            super().__init__(timeout=None)
            self.author_id = author_id

            if twitter_url:
                self.add_item(Button(label="Twitter", url=twitter_url, style=discord.ButtonStyle.link))
            if x_url:
                self.add_item(Button(label="X", url=x_url, style=discord.ButtonStyle.link))
            self.add_item(Button(label="Delete", style=discord.ButtonStyle.danger, custom_id="delete_button"))

        @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
        async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id == self.author_id:
                await interaction.message.delete()
            else:
                await interaction.response.send_message("You do not have permission to delete this message.", ephemeral=True)

    twitter_url = link_info.get('tw')
    x_url = link_info.get('x')
    
    await channel.send(f"@{original_author.mention}\n{modified_content}", view=ResendView(original_author.id, twitter_url, x_url))

# 메시지 수정 함수 (정규식 이용)
def modify_links(content):
    pattern = re.compile(r"https?://(?:www\.)?(twitter|x)\.com/(\S+)")
    
    link_info = {'tw': None, 'x': None, 'vx': None}

    def replace_link(match):
        domain = match.group(1)
        path = match.group(2)
        original_link = f"https://{domain}.com/{path}"
        if domain == "twitter":
            link_info['tw'] = original_link
        elif domain == "x":
            link_info['x'] = original_link
        
        vxtwitter_link = f"https://vxtwitter.com/{path}"
        if not link_info['vx']:
            link_info['vx'] = vxtwitter_link
        return vxtwitter_link

    modified_content = pattern.sub(replace_link, content)
    
    return modified_content, link_info

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if ("https://twitter.com" in message.content or "https://x.com" in message.content) and "`" not in message.content:
        original_content = message.content
        modified_content, link_info = modify_links(original_content)
        await message.delete()
        await resend_message(message.channel, message.author, modified_content, link_info)
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if after.author == bot.user:
        return

    if ("https://twitter.com" in after.content or "https://x.com" in after.content) and "`" not in after.content:
        original_content = after.content
        modified_content, link_info = modify_links(original_content)
        await after.delete()
        await resend_message(after.channel, after.author, modified_content, link_info)

# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)
