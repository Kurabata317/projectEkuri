import json
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

class LinkButtonView(discord.ui.View):
    def __init__(self, twitter_link, x_link):
        super().__init__()
        self.add_item(discord.ui.Button(label="Twitter", url=twitter_link))
        self.add_item(discord.ui.Button(label="X", url=x_link))
        self.add_item(DeleteButton())

class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Delete", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        message_author_id = interaction.message.content.split(' ')[0][2:-1]
        if str(interaction.user.id) == message_author_id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message("You don't have permission to delete this message", ephemeral=True)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    
    for guild in bot.guilds:
        for channel in guild.text_channels:
            async for message in channel.history(limit=100):
                if message.author == bot.user and 'Delete' in message.content:
                    links = [word for word in message.content.split() if word.startswith("https://vxtwitter.com")]
                    if links:
                        twitter_link = links[0].replace("https://vxtwitter.com", "https://twitter.com")
                        x_link = links[0].replace("https://vxtwitter.com", "https://x.com")
                        view = LinkButtonView(twitter_link, x_link)
                        await message.edit(view=view)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "`" in message.content:
        return

    links = [word for word in message.content.split() if word.startswith("https://twitter.com") or word.startswith("https://x.com")]
    
    if len(links) == 1:
        await message.delete()
        
        modified_content = message.content.replace("https://twitter.com", "https://vxtwitter.com").replace("https://x.com", "https://vxtwitter.com")
        
        twitter_link = links[0].replace("https://x.com", "https://twitter.com")
        x_link = links[0].replace("https://twitter.com", "https://x.com")
        view = LinkButtonView(twitter_link, x_link)

        await message.channel.send(f'@{message.author.mention} {modified_content}', view=view)


# config.json에서 봇 토큰을 불러오는 함수
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['token']

bot.run(TOKEN)
