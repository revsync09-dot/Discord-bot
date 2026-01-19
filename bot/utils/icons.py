"""
Monochrome icon system. 
Consistent, professional icons for all embeds.
No emoji spam allowed.
"""


class Icons:
    """Centralized icon definitions. Monochrome only."""
    
    # Status
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    
    # GitHub Events
    PUSH = "↑"
    PULL_REQUEST = "⇄"
    ISSUE = "●"
    RELEASE = "★"
    STAR = "☆"
    FORK = "⑂"
    
    # Actions
    ADD = "+"
    REMOVE = "−"
    EDIT = "✎"
    DELETE = "✗"
    
    # Navigation
    NEXT = "→"
    PREVIOUS = "←"
    CLOSE = "✕"
    HOME = "⌂"
    
    # GitHub Specific
    COMMIT = "◆"
    BRANCH = "⎇"
    TAG = "⊕"
    MERGED = "⊗"
    CLOSED = "○"
    OPEN = "●"
    
    # Bot
    GITHUB = "⚙"
    DISCORD = "◈"
    SETTINGS = "⚙"
    HELP = "?"
    
    @staticmethod
    def get_event_icon(event_type: str) -> str:
        """Get icon for GitHub event type."""
        mapping = {
            "push": Icons.PUSH,
            "pull_request": Icons.PULL_REQUEST,
            "issue": Icons.ISSUE,
            "issues": Icons.ISSUE,
            "release": Icons.RELEASE,
            "star": Icons.STAR,
            "fork": Icons.FORK,
        }
        return mapping.get(event_type.lower(), Icons.GITHUB)
    
    @staticmethod
    def get_pr_state_icon(state: str) -> str:
        """Get icon for pull request state."""
        mapping = {
            "open": Icons.OPEN,
            "closed": Icons.CLOSED,
            "merged": Icons.MERGED,
        }
        return mapping.get(state.lower(), Icons.PULL_REQUEST)
    
    @staticmethod
    def get_issue_state_icon(state: str) -> str:
        """Get icon for issue state."""
        mapping = {
            "open": Icons.OPEN,
            "closed": Icons.CLOSED,
        }
        return mapping.get(state.lower(), Icons.ISSUE)