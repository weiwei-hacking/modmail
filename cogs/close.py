# cogs/close.py
import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path

class Close(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_path = Path(__file__).parent.parent
    
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

    @app_commands.command(name="close", description="關閉目前的客服單")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def close(self, interaction: discord.Interaction):
        try:
            # 檢查是否為客服頻道
            open_data = self.load_config('open.json')
            if not open_data:
                await interaction.response.send_message("無法讀取客服單資料。", ephemeral=True)
                return
            
            current_channel_id = str(interaction.channel_id)
            user_id = None
            
            # 尋找對應的用戶ID
            for uid, data in open_data.items():
                if data['channel_id'] == current_channel_id:
                    user_id = uid
                    break
            
            if user_id is None:
                await interaction.response.send_message("這不是客服頻道。", ephemeral=True)
                return
            
            # 載入設定檔以獲取關閉類別ID
            configs = self.load_config('configs.json')
            if not configs or 'close_category_id' not in configs:
                await interaction.response.send_message("無法讀取設定檔。", ephemeral=True)
                return
            
            # 獲取關閉類別
            close_category = interaction.guild.get_channel(int(configs['close_category_id']))
            if not close_category:
                await interaction.response.send_message("無法找到關閉類別。", ephemeral=True)
                return
            
            # 移動頻道
            await interaction.channel.edit(category=close_category)
            
            # 從open.json中移除此客服單資料
            del open_data[user_id]
            self.save_config('open.json', open_data)
            
            await interaction.response.send_message("客服單已關閉。")
            
        except Exception as e:
            print(f"Error in close command: {str(e)}")
            await interaction.response.send_message("關閉客服單時發生錯誤。", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Close(bot))