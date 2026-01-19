"""
Permission system for bot commands.
Validates Discord permissions and custom role-based access.
"""

from typing import Optional, Callable, Any
from functools import wraps
import discord
from discord import app_commands, Interaction

from .logger import get_logger

logger = get_logger(__name__)


class PermissionLevel:
    """Permission level constants."""
    
    USER = 0
    MODERATOR = 1
    ADMIN = 2
    OWNER = 3


class PermissionError(Exception):
    """Raised when permission check fails."""
    pass


def has_permissions(**perms) -> Callable:
    """
    Decorator to check Discord permissions.
    
    Args:
        **perms: Discord permission flags (e.g., manage_channels=True)
    
    Example:
        @has_permissions(manage_channels=True, manage_webhooks=True)
        async def admin_command(interaction: Interaction):
            ...
    """
    
    async def predicate(interaction: Interaction) -> bool:
        if not interaction.guild:
            raise PermissionError("This command can only be used in a server.")
        
        # Get member permissions
        member = interaction.user
        if not isinstance(member, discord.Member):
            raise PermissionError("Could not retrieve member information.")
        
        permissions = member.guild_permissions
        
        # Check each required permission
        missing = []
        for perm, value in perms.items():
            if getattr(permissions, perm, None) != value:
                missing.append(perm)
        
        if missing:
            missing_perms = ", ".join(missing)
            raise PermissionError(
                f"You are missing the following permissions: {missing_perms}"
            )
        
        return True
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            try:
                await predicate(interaction)
                return await func(interaction, *args, **kwargs)
            except PermissionError as e:
                logger.warning(
                    f"Permission denied for {interaction.user} in {interaction.guild}: {e}"
                )
                
                from ..embeds.error_embed import create_error_embed
                embed = create_error_embed(
                    title="Permission Denied",
                    description=str(e)
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        return wrapper
    
    return decorator


def is_admin() -> Callable:
    """
    Decorator to check if user has administrator permissions.
    Shorthand for @has_permissions(administrator=True)
    """
    return has_permissions(administrator=True)


def is_owner() -> Callable:
    """
    Decorator to check if user is the bot owner.
    Uses application owner from Discord.
    """
    
    async def predicate(interaction: Interaction) -> bool:
        app_info = await interaction.client.application_info()
        
        # Check if team or individual owner
        if app_info.team:
            is_owner_user = interaction.user.id in [m.id for m in app_info.team.members]
        else:
            is_owner_user = interaction.user.id == app_info.owner.id
        
        if not is_owner_user:
            raise PermissionError("This command is restricted to bot owners only.")
        
        return True
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            try:
                await predicate(interaction)
                return await func(interaction, *args, **kwargs)
            except PermissionError as e:
                logger.warning(
                    f"Owner check failed for {interaction.user}: {e}"
                )
                
                from ..embeds.error_embed import create_error_embed
                embed = create_error_embed(
                    title="Access Denied",
                    description=str(e)
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        return wrapper
    
    return decorator


def guild_only() -> Callable:
    """
    Decorator to ensure command is only used in guilds (not DMs).
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            if not interaction.guild:
                logger.warning(
                    f"Guild-only command attempted in DM by {interaction.user}"
                )
                
                from ..embeds.error_embed import create_error_embed
                embed = create_error_embed(
                    title="Server Only",
                    description="This command can only be used in a server, not in DMs."
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            return await func(interaction, *args, **kwargs)
        
        return wrapper
    
    return decorator


async def check_bot_permissions(
    channel: discord.TextChannel,
    *permissions: str
) -> tuple[bool, list[str]]:
    """
    Check if bot has specific permissions in a channel.
    
    Args:
        channel: The channel to check permissions in
        *permissions: Permission names to check (e.g., 'send_messages', 'embed_links')
    
    Returns:
        Tuple of (has_all_permissions, list_of_missing_permissions)
    """
    bot_member = channel.guild.me
    bot_permissions = channel.permissions_for(bot_member)
    
    missing = []
    for perm in permissions:
        if not getattr(bot_permissions, perm, False):
            missing.append(perm)
    
    return (len(missing) == 0, missing)