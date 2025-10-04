# How to Log Sheet Updates

1. Open a Google Sheet
2. Extensions ➡️ Apps Script ➡️ Project Settings ➡️ Script Properties:

| Property | Value |
|----------|----------|
| GH_BRANCH    | main   |
| GH_LOG_PATH    | logs/[INSERT SPREADSHEET NAME HERE]_changes.ndjson   |
| GH_OWNER    | maxweinstein77   |
| GH_REPO    | UATXcavators   |
| GH_TOKEN    | [Max's UATXcavators-specific fine-grain PAT]   |


3. Save Script Properties
4. Copy/paste the following code into Editor
5. Select createInstallableEditTrigger in the function dropdown menu and hit run
6. Give permissions
7. All changes in *just that spreadsheet* will be posted to the file location specified.

```
/*** UI helpers you already tested ***/
function test_commit() {
  // Runs the GitHub test so you can confirm everything without editing a cell
  testCommit_();
  SpreadsheetApp.getActive().toast('✅ Sent test line to GitHub');
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('GitHub Logger')
    .addItem('Run test_commit', 'test_commit')
    .addToUi();
}

/*** EDIT LOGGER ***/
// NOTE: Simple triggers (onEdit) cannot call UrlFetchApp (GitHub). Make it a no-op to avoid errors/double-logs.
function onEdit(e) {
  // Intentionally empty. The installable trigger below (onEditHandler) does the real work.
}

/*** Installable edit handler (same logic as your original onEdit) ***/
function onEditHandler(e) {
  try {
    if (!e || !e.range || e.range.getNumRows() !== 1 || e.range.getNumColumns() !== 1) return;

    const cfg = getConfig_();
    if (!cfg.token || !cfg.owner || !cfg.repo) {
      console.error('Missing GitHub config in Script Properties');
      return;
    }

    // (Optional) limit to a specific tab or range:
    // if (e.range.getSheet().getName() !== 'Inputs') return;

    const sh   = e.range.getSheet();
    const row  = e.range.getRow();
    const col  = e.range.getColumn();
    const when = new Date().toISOString();

    const before = (typeof e.oldValue !== 'undefined') ? String(e.oldValue) : null;
    const after  = (typeof e.value     !== 'undefined') ? String(e.value)     : null;

    const record = {
      ts: when,
      sheet: sh.getName(),
      a1: e.range.getA1Notation(),
      row, col,
      old: before,
      new: after,
      user: (function(){ try { return Session.getActiveUser().getEmail() || null; } catch(_){ return null; } })()
    };

    appendLineToGithub_(cfg, JSON.stringify(record));
    // Optional UX ping so you know it fired
    SpreadsheetApp.getActive().toast('✅ Logged edit: ' + e.range.getA1Notation());
  } catch (err) {
    console.error('[onEditHandler] ' + err);
  }
}

/*** One-time creator for the installable trigger ***/
function createInstallableEditTrigger() {
  // Remove any existing duplicates (safe)
  ScriptApp.getProjectTriggers().forEach(t => {
    if (t.getHandlerFunction && t.getHandlerFunction() === 'onEditHandler') {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger('onEditHandler')
    .forSpreadsheet(SpreadsheetApp.getActive())
    .onEdit()
    .create();

  SpreadsheetApp.getActive().toast('✅ Installable onEdit trigger created');
}

/*** Config + GitHub helpers ***/
function getConfig_() {
  const p = PropertiesService.getScriptProperties();
  return {
    owner:  p.getProperty('GH_OWNER'),
    repo:   p.getProperty('GH_REPO'),
    branch: p.getProperty('GH_BRANCH')   || 'main',
    path:   p.getProperty('GH_LOG_PATH') || 'logs/Sensors_Actuators_Controls_List_changes.ndjson',
    token:  (p.getProperty('GH_TOKEN') || '').trim()
  };
}

function appendLineToGithub_(cfg, line) {
  const {content, sha} = getGithubFile_(cfg, cfg.path);
  const newContent = (content ? content + '\n' : '') + line;
  const msgPreview = line.length > 72 ? (line.slice(0,72) + '…') : line;
  putGithubFile_(cfg, cfg.path, newContent, `Sheets change: ${msgPreview}`, sha);
}

function getGithubFile_(cfg, path) {
  const api = `https://api.github.com/repos/${encodeURIComponent(cfg.owner)}/${encodeURIComponent(cfg.repo)}/contents/${encodeURIComponent(path)}?ref=${encodeURIComponent(cfg.branch)}`;
  const headers = ghHeaders_(cfg.token);
  const resp = UrlFetchApp.fetch(api, {method: 'get', headers, muteHttpExceptions: true});
  const code = resp.getResponseCode();

  if (code === 200) {
    const data = JSON.parse(resp.getContentText());
    const decoded = Utilities.newBlob(Utilities.base64Decode(data.content)).getDataAsString();
    return { content: decoded, sha: data.sha };
  }
  if (code === 404) {
    return { content: '', sha: null };
  }
  throw new Error(`[getGithubFile_] HTTP ${code}: ${resp.getContentText()}`);
}

function putGithubFile_(cfg, path, textContent, message, sha) {
  const api = `https://api.github.com/repos/${encodeURIComponent(cfg.owner)}/${encodeURIComponent(cfg.repo)}/contents/${encodeURIComponent(path)}`;
  const headers = ghHeaders_(cfg.token);
  const body = {
    message,
    content: Utilities.base64Encode(textContent, Utilities.Charset.UTF_8),
    branch: cfg.branch
  };
  if (sha) body.sha = sha;

  const resp = UrlFetchApp.fetch(api, {
    method: 'put',
    headers,
    contentType: 'application/json',
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });
  const code = resp.getResponseCode();
  if (code >= 300) throw new Error(`[putGithubFile_] HTTP ${code}: ${resp.getContentText()}`);
}

function ghHeaders_(token) {
  return {
    Authorization: `Bearer ${token}`,            // fine-grained PAT → Bearer
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'google-apps-script'
  };
}

/*** Self-test that writes a line to GitHub ***/
function testCommit_() {
  const cfg = getConfig_();
  appendLineToGithub_(cfg, JSON.stringify({ts:new Date().toISOString(), test:true}));
  Logger.log('Test line pushed.');
}

function validateGithubAuth_() {
  const cfg = getConfig_();
  if (!cfg.token) throw new Error('No GH_TOKEN set.');
  const headers = ghHeaders_(cfg.token);

  let r = UrlFetchApp.fetch('https://api.github.com/user', {headers, muteHttpExceptions:true});
  Logger.log('GET /user -> ' + r.getResponseCode());              // expect 200

  const repoUrl = `https://api.github.com/repos/${encodeURIComponent(cfg.owner)}/${encodeURIComponent(cfg.repo)}`;
  r = UrlFetchApp.fetch(repoUrl, {headers, muteHttpExceptions:true});
  Logger.log('GET /repos/:owner/:repo -> ' + r.getResponseCode()); // expect 200
}

```
