import os, subprocess, requests, json, textwrap, datetime as dt

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
OPENAI  = os.environ.get("OPENAI_API_KEY")  # optional; falls back if missing
REPO    = os.environ.get("GITHUB_REPOSITORY", "")

def sh(*args):
    return subprocess.check_output(args, stderr=subprocess.STDOUT).decode("utf-8","ignore")

# commits in last 24h (UTC)
since = (dt.datetime.utcnow() - dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
log_fmt = "%h|%an|%s"
try:
    raw = sh("git", "log", f'--since={since}', "--pretty=format:%h|%an|%s")
    commits = [line for line in raw.splitlines() if line.strip()]
except Exception:
    commits = []

# gather a few file paths per commit for context
entries = []
for line in commits[:50]:  # cap to avoid huge messages
    sha, author, subject = (line.split("|", 2) + ["", "", ""])[:3]
    try:
        files = sh("git", "show", "--name-only", "--pretty=", sha).splitlines()
        files = [f for f in files if f.strip()]
        preview = ", ".join(files[:5]) + (" …" if len(files) > 5 else "")
    except Exception:
        preview = ""
    entries.append({"sha": sha, "author": author, "subject": subject, "files": preview})

if not entries:
    msg = "No commits in the last 24 hours."
    requests.post(WEBHOOK, headers={"Content-Type":"application/json"}, data=json.dumps({"content": f"**[Daily Recap]**\n{msg}"}), timeout=30)
    raise SystemExit(0)

# Build plain text for AI / fallback
plain = "\n".join([f"- {e['sha']}: {e['subject']} (by {e['author']})  [files: {e['files'] or 'n/a'}]" for e in entries])

def fallback_summary():
    return "\n".join([
        f"Repo: `{REPO}` — last 24h",
        f"Total commits: {len(entries)}",
        "",
        plain[:3500]  # keep under limits
    ])

def ai_summary():
    if not OPENAI: return ""
    prompt = f"""Summarize the last 24 hours of work for a TBM engineering team in 6–10 bullets:
- group related work (mechanical/electrical/software/docs)
- highlight user-facing or risky changes
- call out follow-ups or tests to run
Commits:
{plain}"""
    r = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {OPENAI}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "input": prompt},
        timeout=60
    )
    r.raise_for_status()
    j = r.json()
    out = j.get("output_text") or ""
    if not out and isinstance(j.get("output"), list):
        out = "\n".join([p.get("text","") for p in j["output"] if isinstance(p, dict) and p.get("type")=="output_text"]).strip()
    return out

summary = ai_summary().strip() or fallback_summary()

content = textwrap.dedent(f"""**[Daily Recap]** `{REPO}`
{summary}
""").strip()

requests.post(WEBHOOK, headers={"Content-Type":"application/json"}, data=json.dumps({"content": content}), timeout=30).raise_for_status()
print("Posted daily recap.")
