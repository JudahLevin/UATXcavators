import os, sys, argparse, datetime as dt, requests, textwrap

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
GITHUB_TOKEN = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")  # e.g. owner/name

if not DISCORD_WEBHOOK:
    sys.exit("Missing DISCORD_WEBHOOK_URL secret.")
if not GITHUB_TOKEN:
    sys.exit("Missing GITHUB_TOKEN (or GH_PAT).")

parser = argparse.ArgumentParser()
parser.add_argument("--hours", type=float, default=6.0, help="Look back this many hours")
parser.add_argument("--branch", type=str, default="main")
args = parser.parse_args()

now = dt.datetime.utcnow()
since = now - dt.timedelta(hours=args.hours)
# ISO format for GitHub API
since_iso = since.replace(microsecond=0).isoformat() + "Z"
until_iso = now.replace(microsecond=0).isoformat() + "Z"

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "commit-digest"
}

def fetch_commits(repo, branch, since_iso, until_iso, per_page=100, max_pages=5):
    all_items = []
    for page in range(1, max_pages+1):
        params = {
            "sha": branch,
            "since": since_iso,
            "until": until_iso,
            "per_page": per_page,
            "page": page
        }
        r = requests.get(f"https://api.github.com/repos/{repo}/commits",
                         headers=headers, params=params, timeout=30)
        r.raise_for_status()
        items = r.json()
        if not items:
            break
        all_items.extend(items)
        if len(items) < per_page:
            break
    return all_items

def is_merge(commit):
    # parents length > 1 is a merge commit
    return len(commit.get("parents", [])) > 1

def format_commits(repo, branch, items):
    lines = []
    for c in items:
        sha = c.get("sha", "")[:7]
        commit = c.get("commit", {})
        msg = (commit.get("message", "") or "").splitlines()[0][:200]
        author = (commit.get("author", {}) or {}).get("name", "unknown")
        ts = (commit.get("author", {}) or {}).get("date", "")
        url = c.get("html_url", "")
        lines.append(f"[`{sha}`] {msg} — {author} ({ts})\n{url}")

    header = f"**{repo}** — branch **{branch}**\nCommits from last {args.hours:g}h: {len(lines)} found."
    content = header + ("\n\n" + "\n\n".join(lines) if lines else "\n\n*(no commits in this window)*")
    return content

def post_to_discord(content):
    # Chunk to under 2000 chars
    MAX = 1900
    parts = [content[i:i+MAX] for i in range(0, len(content), MAX)] or [content]
    for i, part in enumerate(parts, 1):
        if len(parts) > 1:
            part = f"{part}\n\n(part {i}/{len(parts)})"
        r = requests.post(DISCORD_WEBHOOK, json={"content": part}, timeout=30)
        r.raise_for_status()

# 1) Get commits
items = fetch_commits(REPO, args.branch, since_iso, until_iso)

# 2) Optional: filter out merge commits for readability
items = [c for c in items if not is_merge(c)]

# 3) Sort oldest→newest (Discord reads better this way)
items.sort(key=lambda c: (c.get("commit", {}).get("author", {}) or {}).get("date", ""))

# 4) Build message & post
content = format_commits(REPO, args.branch, items)
post_to_discord(content)
print("Posted to Discord.")
