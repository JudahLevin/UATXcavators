import os, subprocess, requests, json, textwrap

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]   # same webhook you already use
OPENAI  = os.environ.get("OPENAI_API_KEY")    # optional, but needed for AI

REPO  = os.environ.get("GITHUB_REPOSITORY","")
SHA   = os.environ.get("GITHUB_SHA","")
ACTOR = os.environ.get("GITHUB_ACTOR","")
MSG   = os.environ.get("COMMIT_MSG","").strip()

def git(*args):
    return subprocess.check_output(["git", *args], stderr=subprocess.STDOUT).decode("utf-8","ignore")

def safe_git(*args):
    try:
        return git(*args)
    except Exception:
        return ""

# Gather a short diff
diff = safe_git("show", "--no-color", "--unified=0", SHA)[:4000]

def fallback():
    # minimal readable summary if AI is off/unavailable
    lines = [f"• Summary: {MSG or '(no commit message)'}"]
    # list a few changed files from the diff headers
    files = []
    for ln in diff.splitlines():
        if ln.startswith("+++ b/"):
            files.append(ln[6:])
    if files:
        preview = ", ".join(files[:6]) + (" …" if len(files) > 6 else "")
        lines.append(f"• Files: {preview}")
    lines.append("• Next: run checks/tests for impacted areas.")
    return "\n".join(lines)

def ai_explain():
    prompt = f"""Explain this GitHub commit in 5–8 short lines for non-authors:
- What changed (high level)
- Why (intent)
- Any risks/checks
Commit message: {MSG or '(none)'}
Diff (trimmed):
{diff or '(no diff)'}"""
    r = requests.post(
        "https://api.openai.com/v1/responses",
        headers={"Authorization": f"Bearer {OPENAI}", "Content-Type": "application/json"},
        json={"model": "gpt-4o-mini", "input": prompt},
        timeout=60
    )
    r.raise_for_status()
    j = r.json()
    txt = j.get("output_text")
    if not txt and isinstance(j.get("output"), list):
        txt = "\n".join([p.get("text","") for p in j["output"] if isinstance(p, dict) and p.get("type")=="output_text"]).strip()
    return txt or "(no explanation generated)"

def post(content: str):
    payload = {"content": content}
    rr = requests.post(WEBHOOK, headers={"Content-Type":"application/json"}, data=json.dumps(payload), timeout=30)
    rr.raise_for_status()

# Build and post
explanation = fallback()
if OPENAI:
    try:
        explanation = ai_explain()
    except Exception as e:
        explanation = f"(AI explanation failed: {e})\n\n" + fallback()

commit_url = f"https://github.com/{REPO}/commit/{SHA}"
message = textwrap.dedent(f"""**[Commit Explanation]**  
{explanation}
""").strip()

post(message)
print("Posted explanation.")
