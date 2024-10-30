# cogs/dm_handler.py
import discord
from discord.ext import commands
import json
import os
from pathlib import Path

class DMHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = Path(__file__).parent.parent
        self.check_json_files()
        
    def check_json_files(self):
        # 檢查並創建 open.json
        open_path = self.base_path / 'open.json'
        if not open_path.exists():
            with open(open_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)

    def load_config(self, file_name):
        file_path = self.base_path / file_name
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {file_name}: {str(e)}")
            return None
    
    def save_config(self, file_name, data):
        file_path = self.base_path / file_name
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {file_name}: {str(e)}")
            return False

    async def create_ticket_channel(self, guild, user):
        try:
            # 載入設定
            configs = self.load_config('configs.json')
            if not configs:
                print("Could not load configs.json")
                return None
                
            open_category_id = int(configs['open_category_id'])
            category = guild.get_channel(open_category_id)
            
            if not category:
                print(f"Could not find category with ID {open_category_id}")
                return None
                
            # 創建文字頻道
            channel = await guild.create_text_channel(
                name=f"{user.name}",
                category=category,
                topic=f"User ID: {user.id}"
            )
            
            # 更新 open.json
            open_data = self.load_config('open.json') or {}
            open_data[str(user.id)] = {
                "channel_id": str(channel.id)
            }
            if not self.save_config('open.json', open_data):
                print("Failed to save open.json")
            
            # 發送提及消息
            if 'mention' in configs:
                role = guild.get_role(int(configs['mention']))
                if role:
                    await channel.send(f"{user.mention} 開啟了客服單，請 {role.mention} 受理該客服單")
            
            return channel
        except Exception as e:
            print(f"Error in create_ticket_channel: {str(e)}")
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        # 忽略機器人訊息
        if message.author.bot:
            return
            
        # 處理私訊
        if isinstance(message.channel, discord.DMChannel):
            try:
                # 檢查是否已有開啟的頻道
                open_data = self.load_config('open.json') or {}
                user_id = str(message.author.id)
                
                # 如果是新的私訊
                if user_id not in open_data:
                    # 創建頻道
                    configs = self.load_config('configs.json')
                    if not configs or not configs.get('guild_id'):
                        print("Could not load guild_id from configs.json")
                        return
                        
                    guild = self.bot.get_guild(int(configs['guild_id']))
                    if guild:
                        channel = await self.create_ticket_channel(guild, message.author)
                        if channel:
                            # 發送使用者訊息到頻道
                            await channel.send(f"**{message.author.name}** -> {message.content}")
                            
                            # 如果有附件，也發送
                            for attachment in message.attachments:
                                await channel.send(attachment.url)
                    else:
                        print(f"Could not find guild with ID {configs['guild_id']}")
                
                # 如果已有開啟的頻道
                else:
                    channel_id = open_data[user_id]['channel_id']
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        # 發送訊息到頻道
                        await channel.send(f"**{message.author.name}**: {message.content}")
                        
                        # 如果有附件，也發送
                        for attachment in message.attachments:
                            await channel.send(attachment.url)
                    else:
                        print(f"Could not find channel with ID {channel_id}")
            except Exception as e:
                print(f"Error processing DM: {str(e)}")
        
        # 處理頻道訊息
        elif message.guild:
            try:
                open_data = self.load_config('open.json')
                if not open_data:
                    return
                    
                # 檢查此頻道是否是客服頻道
                for user_id, data in open_data.items():
                    if data['channel_id'] == str(message.channel.id):
                        # 找到對應的使用者
                        user = await self.bot.fetch_user(int(user_id))
                        if user:
                            # 發送訊息給使用者
                            await user.send(f"**{message.author.name}**: {message.content}")
                            
                            # 如果有附件，也發送
                            for attachment in message.attachments:
                                await user.send(attachment.url)
                        break
            except Exception as e:
                print(f"Error processing guild message: {str(e)}")

async def setup(bot):
    await bot.add_cog(DMHandler(bot))