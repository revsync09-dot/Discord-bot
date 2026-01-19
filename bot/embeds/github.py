"""
GitHub-specific embed builders.
Embeds for pull requests, issues, commits, etc.
"""

import discord
from typing import Optional, Dict, Any, List
from datetime import datetime

from bot.embeds.base import BaseEmbed, Colors
from bot.utils.icons import Icons
from bot.utils.formatting import (
    truncate, bold, code, link, format_repo_name,
    format_user, format_commit_sha, format_branch, pluralize
)
from bot.utils.time import format_relative


class PullRequestEmbed(BaseEmbed):
    """Embed for pull request events."""
    
    def __init__(self, pr_data: Dict[str, Any], action: str):
        """
        Create PR embed.
        
        Args:
            pr_data: Pull request data from webhook
            action: Action type (opened, closed, merged, etc.)
        """
        pr = pr_data['pull_request']
        repo = pr_data['repository']
        sender = pr_data['sender']
        
        # Determine color and title prefix
        if action == 'opened':
            color = Colors.OPEN
            icon = Icons.PR_OPEN
        elif action == 'closed' and pr.get('merged'):
            color = Colors.MERGED
            icon = Icons.PR_MERGED
            action = 'merged'
        elif action == 'closed':
            color = Colors.CLOSED
            icon = Icons.PR_CLOSED
        else:
            color = Colors.INFO
            icon = Icons.PR_OPEN
        
        title = f"{icon} Pull Request #{pr['number']} {action}"
        description = f"**{pr['title']}**\n\n{truncate(pr['body'] or 'No description', 200)}"
        
        super().__init__(
            title=title,
            description=description,
            color=color,
            url=pr['html_url']
        )
        
        # Add fields
        self.add_field(
            name="Repository",
            value=format_repo_name(repo['owner']['login'], repo['name']),
            inline=True
        )
        
        self.add_field(
            name="Author",
            value=format_user(pr['user']['login'], pr['user']['html_url']),
            inline=True
        )
        
        self.add_field(
            name="Branch",
            value=f"{format_branch(pr['head']['ref'])} → {format_branch(pr['base']['ref'])}",
            inline=True
        )
        
        if pr.get('draft'):
            self.add_field(name="Status", value="🔄 Draft", inline=True)
        
        # Stats
        stats = []
        if 'additions' in pr:
            stats.append(f"+{pr['additions']}")
        if 'deletions' in pr:
            stats.append(f"-{pr['deletions']}")
        if 'changed_files' in pr:
            stats.append(pluralize(pr['changed_files'], 'file'))
        
        if stats:
            self.add_field(name="Changes", value=" • ".join(stats), inline=True)
        
        self.set_author_from_user(
            sender['login'],
            sender['avatar_url'],
            sender['html_url']
        )
        
        self.set_repo_footer(repo['owner']['login'], repo['name'])


class IssueEmbed(BaseEmbed):
    """Embed for issue events."""
    
    def __init__(self, issue_data: Dict[str, Any], action: str):
        """
        Create issue embed.
        
        Args:
            issue_data: Issue data from webhook
            action: Action type (opened, closed, reopened, etc.)
        """
        issue = issue_data['issue']
        repo = issue_data['repository']
        sender = issue_data['sender']
        
        # Determine color and icon
        if action == 'opened' or action == 'reopened':
            color = Colors.OPEN
            icon = Icons.ISSUE_OPEN
        elif action == 'closed':
            color = Colors.CLOSED
            icon = Icons.ISSUE_CLOSED
        else:
            color = Colors.INFO
            icon = Icons.ISSUE_OPEN
        
        title = f"{icon} Issue #{issue['number']} {action}"
        description = f"**{issue['title']}**\n\n{truncate(issue['body'] or 'No description', 200)}"
        
        super().__init__(
            title=title,
            description=description,
            color=color,
            url=issue['html_url']
        )
        
        # Add fields
        self.add_field(
            name="Repository",
            value=format_repo_name(repo['owner']['login'], repo['name']),
            inline=True
        )
        
        self.add_field(
            name="Author",
            value=format_user(issue['user']['login'], issue['user']['html_url']),
            inline=True
        )
        
        # Labels
        if issue.get('labels'):
            labels = [f"\`{label['name']}\`" for label in issue['labels'][:5]]
            self.add_field(
                name="Labels",
                value=" ".join(labels),
                inline=False
            )
        
        self.set_author_from_user(
            sender['login'],
            sender['avatar_url'],
            sender['html_url']
        )
        
        self.set_repo_footer(repo['owner']['login'], repo['name'])


class CommitEmbed(BaseEmbed):
    """Embed for commit/push events."""
    
    def __init__(self, push_data: Dict[str, Any]):
        """
        Create commit embed.
        
        Args:
            push_data: Push data from webhook
        """
        repo = push_data['repository']
        commits = push_data['commits']
        pusher = push_data['pusher']
        ref = push_data['ref'].split('/')[-1]  # Get branch name
        
        commit_count = len(commits)
        icon = Icons.COMMIT
        
        title = f"{icon} {pluralize(commit_count, 'commit')} pushed to {format_branch(ref)}"
        
        # Build commit list
        commit_list = []
        for commit in commits[:5]:  # Show max 5 commits
            sha = format_commit_sha(commit['id'])
            message = truncate(commit['message'].split('\n')[0], 50)
            author = commit['author']['name']
            commit_list.append(f"{sha} {message} - {author}")
        
        if commit_count > 5:
            commit_list.append(f"... and {commit_count - 5} more")
        
        description = "\n".join(commit_list)
        
        super().__init__(
            title=title,
            description=description,
            color=Colors.INFO,
            url=push_data['compare']
        )
        
        self.add_field(
            name="Repository",
            value=format_repo_name(repo['owner']['login'], repo['name']),
            inline=True
        )
        
        self.add_field(
            name="Pusher",
            value=code(pusher['name']),
            inline=True
        )
        
        self.set_repo_footer(repo['owner']['login'], repo['name'])


class ReleaseEmbed(BaseEmbed):
    """Embed for release events."""
    
    def __init__(self, release_data: Dict[str, Any], action: str):
        """
        Create release embed.
        
        Args:
            release_data: Release data from webhook
            action: Action type (published, created, etc.)
        """
        release = release_data['release']
        repo = release_data['repository']
        
        icon = Icons.TAG
        title = f"{icon} Release {release['tag_name']} {action}"
        description = f"**{release['name'] or release['tag_name']}**\n\n{truncate(release['body'] or 'No description', 300)}"
        
        super().__init__(
            title=title,
            description=description,
            color=Colors.SUCCESS,
            url=release['html_url']
        )
        
        self.add_field(
            name="Repository",
            value=format_repo_name(repo['owner']['login'], repo['name']),
            inline=True
        )
        
        self.add_field(
            name="Tag",
            value=code(release['tag_name']),
            inline=True
        )
        
        if release.get('prerelease'):
            self.add_field(name="Type", value="🔶 Pre-release", inline=True)
        
        self.set_repo_footer(repo['owner']['login'], repo['name'])
