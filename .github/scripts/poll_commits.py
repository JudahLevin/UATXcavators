# .github/scripts/poll_commits.py
import os, sys, argparse, datetime as dt, requests
from typing import List, Dict

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
GITHUB_TOKEN = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
REPO = os.environ.get("GITHUB_REPOSITORY")  # e.g., owner/name

if not DISCORD_WEBHOOK:
    sys.exit("Missing DISCORD_WEBHOOK_URL secret.")
if not GITHUB_TOKEN:
    sys.exit("Missing GITHUB_TOKEN (or GH_PAT).")

parser = argparse.ArgumentParser()
parser.add_argument("--hours", type=float, default=6.0)
parser.add_argument("--branch", type=str, default="main")
args = parser.parse_args()

now = dt.datetime.utcnow()
since = now - dt.timedelta(hours=args.hours)
since_iso = since.replace(microsecond=0).isoformat() + "Z"
until_iso = now.replace(microsecond=0).isoformat() + "Z"

gh_headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "commit-digest"
}

def fetch_commits(repo: str, branch: str, since_iso: str, until_iso: str,
                  per_page: int = 100, max_pages: int = 5) -> List[Dict]:
    all_items = []
    for page in range(1, max_pages+1):
        params = {"sha": branch, "since": since_iso, "until": until_iso,
                  "per_page": per_page, "page": page}
        r = requests.get(f"https://api.github.com/repos/{repo}/commits",
                         headers=gh_headers, params=params, timeout=30)
        r.raise_for_status()
        items = r.json()
        if not items: break
        all_items.extend(items)
        if len(items) < per_page: break
    return all_items

def is_merge(commit: Dict) -> bool:
    return len(commit.get("parents", [])) > 1

def bullet_lines(items: List[Dict]) -> List[str]:
    lines = []
    for c in items:
        sha = c.get("sha","")[:7]
        commit = c.get("commit", {}) or {}
        msg = (commit.get("message","") or "").splitlines()[0][:200]
        author = (commit.get("author", {}) or {}).get("name", "unknown")
        ts = (commit.get("author", {}) or {}).get("date", "")
        url = c.get("html_url","")
        lines.append(f"• `{sha}` {msg} — {author} ({ts})\n{url}")
    return lines

def summarize_with_openai(repo: str, branch: str, hours: float, bullets: List[str]) -> str:
    """
    Ask OpenAI for a 2–5 sentence human-friendly summary.
    If OPENAI_API_KEY is missing or call fails, return an empty string.
    """
    if not OPENAI_API_KEY or not bullets:
        return ""

    max_bullets = 25
    subset = bullets[:max_bullets]
    subset_text = "\n".join(subset)  # <-- precompute to avoid backslash in f-string expression

    prompt = (
        f"You are a release-notes assistant. Summarize recent GitHub commits for {repo} "
        f"on branch '{branch}' from the last {hours:g} hours. "
        f"Write 2–5 concise sentences for non-developers. "
        f"Group by themes (features, fixes, refactors), avoid file paths/SHAs, and keep it neutral.\n\n"
        f"Also, if spreadsheet edit JSON entries are provided, summarize the change in plain English "
        f"(who edited, which sheet/cell, and what the new text says). Focus on the description of the change "
        f"rather than the technical cell coordinates.\n\n"
        f"Commits:\n{subset_text}"
    )

    # OpenAI Responses API (text generation).
    # Models like gpt-4.1 or gpt-4.1-mini work well here.
    # See official docs: Text generation & Responses API. 
    # https://platform.openai.com/docs/guides/text ; https://platform.openai.com/docs/guides/migrate-to-responses
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        # Modern SDKs expose `responses.create`; older expose `chat.completions.create`.
        # Use a generic fallback to support both.
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
                temperature=0.4,
                max_output_tokens=250
            )
            text = resp.output_text
        except Exception:
            # Fallback to chat.completions if needed
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=250,
            )
            text = resp["choices"][0]["message"]["content"]
        return text.strip()
    except Exception as e:
        print(f"OpenAI error (non-fatal): {e}", file=sys.stderr)
        return ""

def post_to_discord(content: str):
    MAX = 1900
    chunks = [content[i:i+MAX] for i in range(0, len(content), MAX)] or [content]
    for i, part in enumerate(chunks, 1):
        if len(chunks) > 1:
            part = f"{part}\n\n(part {i}/{len(chunks)})"
        r = requests.post(DISCORD_WEBHOOK, json={"content": part}, timeout=30)
        r.raise_for_status()

# 1) Fetch and filter commits
items = fetch_commits(REPO, args.branch, since_iso, until_iso)
items = [c for c in items if not is_merge(c)]
items.sort(key=lambda c: (c.get("commit", {}).get("author", {}) or {}).get("date", ""))

# 2) Build bullets (raw list for Discord) and header
bullets = bullet_lines(items)
header = f"**{REPO}** — branch **{args.branch}**\nCommits in last {args.hours:g}h: {len(bullets)}"

# 3) Summarize with OpenAI (optional)
summary = summarize_with_openai(REPO, args.branch, args.hours, bullets)

# 4) Post to Discord: SUMMARY ONLY
if not bullets:
    # No commits in this window — post nothing (or post a minimal note)
    # post_to_discord(f"{header}\n\n*(no commits in this window)*")
    sys.exit(0)

if summary:
    # Post just the AI summary (you can keep or remove the header line)
    post_to_discord(f"{header}\n\n**AI Summary:**\n{summary}")
else:
    # If the AI call failed or OPENAI_API_KEY missing, either post nothing...
    # sys.exit(0)
    # ...or post a short fallback message:
    post_to_discord(f"{header}\n\n*(AI summary unavailable this run)*")

print("Posted summary to Discord.")
