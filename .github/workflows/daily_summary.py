import os
import requests
from datetime import datetime, timedelta
from github import Github

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(GITHUB_REPO)

since = datetime.utcnow() - timedelta(days=1)
commits = repo.get_commits(since=since)

if commits.totalCount == 0:
    summary = f"**Daily TBM Commit Recap ({since.strftime('%Y-%m-%d')})**\nNo commits in the last 24 hours."
else:
    summary = f"**Daily TBM Commit Recap ({since.strftime('%Y-%m-%d')})**\n"
    for commit in commits[:20]:
        msg = commit.commit.message.splitlines()[0]
        author = commit.commit.author.name if commit.commit.author else "Unknown"
        summary += f"- [{msg}]({commit.html_url}) — by **{author}**\n"

requests.post(DISCORD_WEBHOOK, json={"content": summary})
