import discord
from discord.ext import commands
import os

with open('token.txt', 'r') as f:
    TOKEN = f.read().strip()

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='/', intents=intents)


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    

@bot.event
async def on_ready():
    os.system("cls")
    print(f'{bot.user} 上線了!')
    await bot.tree.sync()

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())