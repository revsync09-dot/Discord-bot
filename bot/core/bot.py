"""
Core Discord bot implementation.
Handles startup, command registration, and lifecycle management.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import asyncio

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)


class GitHubNotifyBot(commands.Bot):
    """
    Main bot class.
    Manages Discord connection, command registration, and integration with services.
    """
    
    def __init__(self):
        config = get_config()
        
        # Intents
        intents = discord.Intents.default()
        intents.message_content = False  # We use slash commands only
        intents.guilds = True
        intents.members = True  # For permission checks
        
        super().__init__(
            command_prefix="!",  # Unused, but required
            intents=intents,
            application_id=config.application_id
        )
        
        self.config = config
        self.initial_extensions = [
            "bot.commands.help",
            "bot.commands.github",
            "bot.commands.admin"
        ]
        
        # Service references (injected after startup)
        self.github_service = None
        self.subscription_service = None
        self.embed_service = None
        
        # Webhook server reference
        self.webhook_server = None
    
    async def setup_hook(self):
        """
        Called when the bot is starting up.
        Load extensions and prepare services.
        """
        logger.info("Starting bot setup...")
        
        # Load extensions (cogs)
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}", exc_info=True)
        
        # Sync commands if configured
        if self.config.sync_commands_on_ready:
            logger.info("Syncing application commands...")
            try:
                synced = await self.tree.sync()
                logger.info(f"Synced {len(synced)} command(s)")
            except Exception as e:
                logger.error(f"Failed to sync commands: {e}", exc_info=True)
        
        logger.info("Bot setup complete")
    
    async def on_ready(self):
        """Called when the bot is connected and ready."""
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Set presence
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="GitHub events"
            ),
            status=discord.Status.online
        )
        
        logger.info("Bot is ready!")
    
    async def on_guild_join(self, guild: discord.Guild):
        """Called when the bot joins a new guild."""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Store guild in database
        if self.subscription_service:
            try:
                await self.subscription_service.register_guild(guild)
            except Exception as e:
                logger.error(f"Failed to register guild {guild.id}: {e}", exc_info=True)
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Called when the bot is removed from a guild."""
        logger.info(f"Removed from guild: {guild.name} (ID: {guild.id})")
        
        # Optional: Clean up guild data
        # (Keep subscriptions for potential re-join)
    
    async def on_command_error(self, ctx, error):
        """Global error handler for prefix commands (not used in slash-only bot)."""
        pass
    
    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """Global error handler for application commands."""
        logger.error(
            f"Command error in {interaction.command.name if interaction.command else 'unknown'}: {error}",
            exc_info=True
        )
        
        # Import here to avoid circular dependency
        from ..embeds.error_embed import create_error_embed
        
        embed = create_error_embed(
            title="Command Error",
            description="An unexpected error occurred while executing this command."
        )
        
        # Send error message
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}", exc_info=True)
    
    async def close(self):
        """Cleanup before shutdown."""
        logger.info("Shutting down bot...")
        
        # Stop webhook server
        if self.webhook_server:
            logger.info("Stopping webhook server...")
            # Server shutdown handled in main.py
        
        await super().close()
        logger.info("Bot shutdown complete")
    
    def inject_services(
        self,
        github_service,
        subscription_service,
        embed_service
    ):
        """
        Inject service dependencies after initialization.
        Called from main.py after services are created.
        """
        self.github_service = github_service
        self.subscription_service = subscription_service
        self.embed_service = embed_service
        
        logger.info("Services injected successfully")
