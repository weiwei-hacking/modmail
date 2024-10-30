# cogs/setup.py
import discord
from discord.ext import commands
from discord import app_commands
import json

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def load_config(self):
        with open('configs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def save_config(self, config):
        with open('configs.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

    @app_commands.command(name="setup", description="建立私信客服功能")
    @app_commands.default_permissions(administrator=True)  # 設定需要管理員權限
    @app_commands.checks.has_permissions(administrator=True)  # 再次確認權限
    async def setup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = self.load_config()
            
            # 設定伺服器 ID
            config["guild_id"] = str(interaction.guild_id)
            
            # 創建身分組
            support_role = await interaction.guild.create_role(
                name="客服人員",
                color=discord.Color.blue(),
                reason="Ticket System Setup"
            )
            config["mention"] = str(support_role.id)
            
            # 設定分類的權限
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                support_role: discord.PermissionOverwrite(view_channel=True),
                interaction.guild.me: discord.PermissionOverwrite(view_channel=True)
            }
            
            # 創建開啟分類
            open_category = await interaction.guild.create_category(
                name="客服開啟",
                overwrites=overwrites
            )
            config["open_category_id"] = str(open_category.id)
            
            # 創建關閉分類
            close_category = await interaction.guild.create_category(
                name="客服關閉",
                overwrites=overwrites
            )
            config["close_category_id"] = str(close_category.id)
            
            # 儲存設定
            self.save_config(config)
            
            await interaction.followup.send(
                "設定完成！\n"
                f"已創建客服人員身分組: {support_role.mention}\n"
                f"已創建開啟分類: {open_category.name}\n"
                f"已創建關閉分類: {close_category.name}\n",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"設定過程中發生錯誤：{str(e)}", ephemeral=True)

    @setup.error
    async def setup_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("你需要管理員權限才能使用此指令！", ephemeral=True)
        else:
            await interaction.response.send_message(f"發生錯誤：{str(error)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetupCog(bot))