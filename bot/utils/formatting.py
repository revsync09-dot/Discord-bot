"""
Text formatting utilities.
Consistent formatting across all embeds.
"""

from typing import Optional, List
import re


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def bold(text: str) -> str:
    """Make text bold."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Make text italic."""
    return f"*{text}*"


def code(text: str) -> str:
    """Format as inline code."""
    return f"`{text}`"


def code_block(text: str, language: str = "") -> str:
    """Format as code block."""
    return f"```{language}\n{text}\n```"


def quote(text: str) -> str:
    """Format as quote."""
    return f"> {text}"


def link(text: str, url: str) -> str:
    """Create a hyperlink."""
    return f"[{text}]({url})"


def sanitize_markdown(text: str) -> str:
    """
    Escape Discord markdown characters.
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    """
    escape_chars = ['*', '_', '`', '~', '|', '>', '#']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
    return text


def format_list(items: List[str], prefix: str = "•") -> str:
    """
    Format a list of items.
    
    Args:
        items: List of items
        prefix: Prefix for each item
    
    Returns:
        Formatted list
    """
    return "\n".join([f"{prefix} {item}" for item in items])


def format_repo_name(owner: str, repo: str) -> str:
    """Format repository name."""
    return bold(f"{owner}/{repo}")


def format_user(username: str, url: Optional[str] = None) -> str:
    """Format GitHub username."""
    if url:
        return link(f"@{username}", url)
    return code(f"@{username}")


def format_commit_sha(sha: str, short: bool = True) -> str:
    """Format commit SHA."""
    display = sha[:7] if short else sha
    return code(display)


def format_branch(branch: str) -> str:
    """Format branch name."""
    return code(branch)


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Pluralize a word based on count.
    
    Args:
        count: Number of items
        singular: Singular form
        plural: Plural form (defaults to singular + 's')
    
    Returns:
        Pluralized string
    """
    if count == 1:
        return f"{count} {singular}"
    
    plural = plural or f"{singular}s"
    return f"{count} {plural}"


def extract_github_repo(text: str) -> Optional[tuple[str, str]]:
    """
    Extract owner/repo from various GitHub URL formats.
    
    Args:
        text: Text containing GitHub URL or owner/repo
    
    Returns:
        Tuple of (owner, repo) or None
    """
    # Match owner/repo format
    match = re.match(r'^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)$', text)
    if match:
        return match.group(1), match.group(2)
    
    # Match GitHub URL
    match = re.search(r'github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)', text)
    if match:
        return match.group(1), match.group(2)
    
    return None
