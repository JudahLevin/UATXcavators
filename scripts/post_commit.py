import os, subprocess, requests, json, textwrap

# --- Inputs / secrets ---
repo   = os.environ.get("GITHUB_REPOSITORY", "")
sha    = os.environ.get("GITHUB_SHA", "")
actor  = os.environ.get("GITHUB_ACTOR", "")
channel_id = os.environ["DISCORD_CHANNEL_ID"]
bot_token  = os.environ["DISCORD_BOT_TOKEN"]
openai_key = os.environ.get("OPENAI_API_KEY")  # optional

def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.STDOUT).decode("utf-8", "ignore")

def safe_git(*args):
    try:
        return git(*args)
    except Exception:
        return ""

title = safe_git("log", "-1", "--pretty=%s").strip()
body  = safe_git("log", "-1", "--pretty=%b").strip()
changed = [ln.strip() for ln in safe_git("show", "--name-only", "--pretty=", sha).splitlines() if ln.strip()]
diff = safe_git("show", "--no-color", "--unified=0", sha)[:6000]

files_preview = ", ".join(changed[:6]) + (" …" if len(changed) > 6 else "") if changed else "(no files listed)"

def fallback():
    out = [f"• Summary: {title or '(no title)'}"]
    if body:
        out.append("• Notes: " + body.splitlines()[0])
    out.append(f"• Files: {files_preview}")
    out.append("• Follow-ups: run tests/checks for affected areas.")
    return "\n".join(out)

def ai_explain(prompt: str) -> str:
    url = "https://api.openai.com/v1/responses"
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    data = {"model": "gpt-4o-mini", "input": prompt}
    r = requests.post(url, headers=headers, json=data, timeout=60)
    r.raise_for_status()
    j = r.json()
    out = j.get("output_text")
    if not out and isinstance(j.get("output"), list):
        out = "\n".join(
            it.get("text","") for it in j["output"] if isinstance(it, dict) and it.get("type")=="output_text"
        ).strip()
    return out or "(no explanation generated)"

prompt = f"""Explain this commit for a TBM team in 5–8 short lines:
- What changed (files/modules)
- Likely intent
- Risks or checks to run
Title: {title}
Body: {body or '(no body)'}
Files: {files_preview}
Diff (trimmed):
{diff}
"""

explanation = fallback()
if openai_key:
    try:
        explanation = ai_explain(prompt)
    except Exception as e:
        explanation = f"(AI explanation failed: {e})\n\n" + fallback()

commit_url = f"https://github.com/{repo}/commit/{sha}"
content = textwrap.dedent(f"""
**[Commit]** `{repo}` @ `{sha[:7]}` by {actor}
{commit_url}

**[Explanation]**
@everyone
{explanation}
""").strip()

payload = {"content": content, "allowed_mentions": {"parse": ["everyone"]}}
resp = requests.post(
    f"https://discord.com/api/v10/channels/{channel_id}/messages",
    headers={"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"},
    data=json.dumps(payload),
    timeout=30
)
resp.raise_for_status()
print("Posted to Discord.")
