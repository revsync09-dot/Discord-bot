"""
Base embed builder.
Provides consistent embed creation across all GitHub events.
"""

import discord
from datetime import datetime
from typing import Optional, List, Dict, Any

from bot.utils.icons import Icons
from bot.utils.time import format_timestamp, now_utc


class Colors:
    """Consistent color scheme for embeds."""
    
    # GitHub brand
    GITHUB = 0x238636
    
    # States
    SUCCESS = 0x2ea043
    ERROR = 0xcf222e
    WARNING = 0xd29922
    INFO = 0x0969da
    
    # PR/Issue states
    OPEN = 0x1a7f37
    CLOSED = 0xcf222e
    MERGED = 0x8957e5
    DRAFT = 0x768390
    
    # Neutral
    NEUTRAL = 0x6e7781
    DARK = 0x24292f


class BaseEmbed(discord.Embed):
    """Base class for all GitHub embeds."""
    
    def __init__(self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: int = Colors.GITHUB,
        url: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        **kwargs
    ):
        """
        Initialize base embed.
        
        Args:
            title: Embed title
            description: Embed description
            color: Embed color
            url: Embed URL
            timestamp: Embed timestamp (defaults to now)
            **kwargs: Additional discord.Embed parameters
        """
        if timestamp is None:
            timestamp = now_utc()
        
        super().__init__(
            title=title,
            description=description,
            color=color,
            url=url,
            timestamp=timestamp,
            **kwargs
        )
    
    def set_repo_footer(self, owner: str, repo: str) -> 'BaseEmbed':
        """
        Set footer with repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
        
        Returns:
            Self for chaining
        """
        self.set_footer(text=f"{owner}/{repo}")
        return self
    
    def set_author_from_user(
        self,
        username: str,
        avatar_url: Optional[str] = None,
        url: Optional[str] = None
    ) -> 'BaseEmbed':
        """
        Set author from GitHub user.
        
        Args:
            username: GitHub username
            avatar_url: User's avatar URL
            url: User's profile URL
        
        Returns:
            Self for chaining
        """
        self.set_author(
            name=username,
            icon_url=avatar_url,
            url=url
        )
        return self
    
    def add_field_if(
        self,
        condition: bool,
        name: str,
        value: str,
        inline: bool = False
    ) -> 'BaseEmbed':
        """
        Conditionally add a field.
        
        Args:
            condition: Whether to add the field
            name: Field name
            value: Field value
            inline: Whether field is inline
        
        Returns:
            Self for chaining
        """
        if condition:
            self.add_field(name=name, value=value, inline=inline)
        return self
    
    def add_fields_from_dict(
        self,
        fields: Dict[str, str],
        inline: bool = False
    ) -> 'BaseEmbed':
        """
        Add multiple fields from dictionary.
        
        Args:
            fields: Dictionary of field names to values
            inline: Whether fields are inline
        
        Returns:
            Self for chaining
        """
        for name, value in fields.items():
            if value:  # Only add non-empty values
                self.add_field(name=name, value=value, inline=inline)
        return self
