const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const REPO_URL = 'https://github.com/cedanl/dair-agentic-coding';
const OUT_DIR = path.join(__dirname, '..', 'docs', 'images');
fs.mkdirSync(OUT_DIR, { recursive: true });

async function highlight(page, locator, { step, label, color = '#E53E3E', position = 'top' }) {
  const box = await locator.boundingBox();
  if (!box) { console.warn(`  ⚠ element niet gevonden: stap ${step}`); return; }
  await page.evaluate(({ box, step, label, color, position }) => {
    const pad = 5;
    const wrap = document.createElement('div');
    wrap.style.cssText = `
      position: fixed; left: ${box.x - pad}px; top: ${box.y - pad}px;
      width: ${box.width + pad * 2}px; height: ${box.height + pad * 2}px;
      border: 3px solid ${color}; border-radius: 7px;
      z-index: 2147483647; pointer-events: none;
      box-shadow: 0 0 0 4px ${color}30;
    `;
    const badge = document.createElement('div');
    const isTop = position !== 'bottom';
    badge.style.cssText = `
      position: absolute;
      ${isTop ? 'bottom: calc(100% + 8px)' : 'top: calc(100% + 8px)'};
      left: 0;
      background: ${color}; color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 13px; font-weight: 700; padding: 4px 12px;
      border-radius: 20px; white-space: nowrap;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    `;
    badge.textContent = `${step}  ${label}`;
    wrap.appendChild(badge);
    document.body.appendChild(wrap);
  }, { box, step, label, color, position });
}

async function shot(page, name) {
  const file = path.join(OUT_DIR, `${name}.png`);
  await page.screenshot({ path: file });
  console.log(`  ✔  ${name}.png`);
}

async function githubPage(html) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
           font-size: 14px; color: #1f2328; background: #fff; width: 1280px; min-height: 860px; }
    .header { background: #1f2328; height: 64px; display:flex; align-items:center; padding: 0 32px; gap: 16px; }
    .header-logo { color: white; font-size: 24px; }
    .header-nav { display:flex; gap: 4px; }
    .header-link { color: #f0f6fc; font-size: 14px; padding: 6px 10px; border-radius: 6px; }
    .subnav { border-bottom: 1px solid #d1d9e0; padding: 0 32px; display:flex; gap: 0; }
    .subnav-item { padding: 12px 16px; color: #656d76; font-size: 14px; display:flex; align-items:center; gap: 6px; cursor:pointer; border-bottom: 2px solid transparent; margin-bottom:-1px; }
    .subnav-item.active { color: #1f2328; font-weight: 600; border-bottom-color: #fd8c73; }
    .main { padding: 24px 32px; max-width: 1280px; display: flex; gap: 24px; }
    .content { flex: 1; min-width: 0; }
    .sidebar { width: 296px; flex-shrink: 0; }
    .branch-bar { display:flex; align-items:center; justify-content:space-between; margin-bottom: 16px; gap: 8px; }
    .branch-btn { border: 1px solid #d1d9e0; border-radius: 6px; padding: 5px 12px; font-size: 14px; background: #f6f8fa; color: #1f2328; display:flex; align-items:center; gap: 6px; }
    .code-btn { background: #2ea043; color: #fff; border: 1px solid rgba(27,31,36,0.15); border-radius: 6px; padding: 5px 16px; font-size: 14px; font-weight: 600; display:flex; align-items:center; gap: 6px; cursor:pointer; }
    .file-list { border: 1px solid #d1d9e0; border-radius: 6px; overflow: hidden; }
    .file-header { background: #f6f8fa; padding: 8px 16px; border-bottom: 1px solid #d1d9e0; font-size: 13px; color: #656d76; }
    .file-row { padding: 8px 16px; border-bottom: 1px solid #d1d9e0; display:flex; align-items:center; gap: 8px; }
    .file-row:last-child { border-bottom: none; }
    .file-icon { color: #656d76; }
    .file-name { color: #0969da; }
    .file-msg { color: #656d76; flex: 1; margin-left: 16px; }
    .readme { border: 1px solid #d1d9e0; border-radius: 6px; margin-top: 16px; overflow: hidden; }
    .readme-header { background: #f6f8fa; padding: 10px 16px; border-bottom: 1px solid #d1d9e0; font-weight: 600; }
    .readme-body { padding: 24px; line-height: 1.6; }
    .readme-body h1 { font-size: 24px; border-bottom: 1px solid #d1d9e0; padding-bottom: 8px; margin-bottom: 16px; }
    .readme-body h2 { font-size: 18px; margin: 20px 0 8px; }
    .readme-body p { margin-bottom: 12px; color: #1f2328; }
    .readme-body code { background: #f6f8fa; padding: 2px 6px; border-radius: 4px; font-family: monospace; color: #cf222e; }
    .search-bar { flex: 1; border: 1px solid #d1d9e0; border-radius: 6px; padding: 5px 12px; font-size: 14px; color: #656d76; background: #f6f8fa; }
  </style>
  </head><body>${html}</body></html>`;
}

// ── Stap 1: Repo pagina — echte GitHub screenshot ────────────────────────────
async function stap1(browser) {
  console.log('\nStap 1: repo pagina (echt GitHub)');
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 860 });
  await page.goto(REPO_URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  const codeBtn = page.locator('button').filter({ hasText: /^Code$/ });
  await highlight(page, codeBtn, { step: '① Klik hier', label: 'groene "Code" knop', color: '#2EA043', position: 'bottom' });
  await shot(page, '01-repo-pagina');
  await page.close();
}

// ── Stap 2: Code dropdown — GitHub simulatie (logged-in state) ───────────────
async function stap2(browser) {
  console.log('Stap 2: Code dropdown simulatie');
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 860 });
  await page.setContent(await githubPage(`
    <div class="header">
      <span class="header-logo">⊛ GitHub</span>
      <div class="header-nav">
        <span class="header-link">cedanl / dair-agentic-coding</span>
      </div>
    </div>
    <div class="subnav">
      <div class="subnav-item active">⎇ Code</div>
      <div class="subnav-item">Issues</div>
      <div class="subnav-item">Pull requests</div>
      <div class="subnav-item">Actions</div>
    </div>
    <div class="main">
      <div class="content">
        <div class="branch-bar">
          <div style="display:flex;gap:8px;align-items:center">
            <div class="branch-btn">⎇ main ▾</div>
            <span style="color:#656d76;font-size:13px">1 Branch &nbsp; 0 Tags</span>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <div class="search-bar" style="max-width:200px">Go to file</div>
            <div class="code-btn" id="code-btn">⟨/⟩ Code ▾</div>
          </div>
        </div>

        <!-- Dropdown -->
        <div id="dropdown" style="
          position: absolute; right: 336px; top: 200px;
          background: #fff; border: 1px solid #d1d9e0; border-radius: 12px;
          box-shadow: 0 8px 24px rgba(140,149,159,0.2);
          width: 340px; overflow: hidden; z-index: 100;
        ">
          <!-- Tabs: Local / Codespaces -->
          <div style="display:flex; border-bottom: 1px solid #d1d9e0;">
            <div style="flex:1; padding:10px 16px; font-size:14px; color:#656d76; text-align:center; cursor:pointer;">Local</div>
            <div id="codespaces-tab" style="flex:1; padding:10px 16px; font-size:14px; font-weight:600; color:#1f2328; text-align:center; border-bottom:2px solid #1f2328; cursor:pointer;">Codespaces</div>
          </div>
          <!-- Codespaces content (empty state) -->
          <div style="padding:16px; text-align:center;">
            <div style="font-size:13px; color:#656d76; margin-bottom:12px;">
              Geen actieve Codespace voor deze repo.
            </div>
            <div id="create-btn" style="
              display:inline-block; width:100%;
              background:#2ea043; color:#fff; border-radius:6px;
              padding:8px 0; font-size:14px; font-weight:600; cursor:pointer;
            ">
              Create codespace on main
            </div>
          </div>
        </div>

        <div class="file-list">
          <div class="file-header">2 commits — Updated just now</div>
          <div class="file-row"><span class="file-icon">📁</span><span class="file-name">.devcontainer</span><span class="file-msg">init: minimale devcontainer</span></div>
          <div class="file-row"><span class="file-icon">📄</span><span class="file-name">README.md</span><span class="file-msg">docs: README met instructies voor deelnemers</span></div>
        </div>
      </div>
      <div class="sidebar">
        <div style="font-weight:600; margin-bottom:8px">About</div>
        <div style="color:#656d76; font-size:13px">DAIR Agentic Coding Sessie</div>
      </div>
    </div>
  `));
  await page.waitForTimeout(300);

  const codespacesTab = page.locator('#codespaces-tab');
  const createBtn = page.locator('#create-btn');
  await highlight(page, codespacesTab, { step: '② Klik op', label: '"Codespaces" tab', color: '#E53E3E', position: 'top' });
  await highlight(page, createBtn, { step: '③ Klik op', label: '"Create codespace on main"', color: '#2EA043', position: 'bottom' });
  await shot(page, '02-codespaces-dropdown');
  await page.close();
}

// ── Stap 3: Codespace laadt — browser geeft de VSCode interface ──────────────
async function stap3(browser) {
  console.log('Stap 3: Codespace loading screen');
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 860 });
  await page.setContent(`<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#1e1e1e; display:flex; align-items:center; justify-content:center;
           height:860px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .card { background:#252526; border-radius:12px; padding:48px 64px; text-align:center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.5); min-width:420px; }
    .logo { font-size:48px; margin-bottom:16px; }
    .title { color:#cccccc; font-size:22px; font-weight:600; margin-bottom:8px; }
    .sub { color:#8c8c8c; font-size:14px; margin-bottom:32px; }
    .bar-bg { background:#3c3c3c; border-radius:4px; height:6px; overflow:hidden; }
    .bar { background:#0078d4; height:6px; border-radius:4px; animation:load 2s ease-in-out infinite; width:60%; }
    @keyframes load { 0%{width:20%} 100%{width:90%} }
    .hint { color:#8c8c8c; font-size:13px; margin-top:24px; }
    .check { color:#4caf50; }
  </style></head><body>
    <div class="card" id="card">
      <div class="logo">⚡</div>
      <div class="title">Je Codespace wordt gestart…</div>
      <div class="sub">Dit duurt ongeveer 1 minuut. Daarna open VSCode automatisch.</div>
      <div class="bar-bg"><div class="bar"></div></div>
      <div class="hint">✓ Container gebouwd &nbsp; ✓ Extensies geladen &nbsp; ⏳ Verbinding maken…</div>
    </div>
  </body></html>`);
  await page.waitForTimeout(400);

  const card = page.locator('#card');
  await highlight(page, card, { step: '③ Wacht', label: 'de omgeving start vanzelf op (~1 minuut)', color: '#0078d4', position: 'bottom' });
  await shot(page, '03-codespace-laadt');
  await page.close();
}

// ── Stap 4: VSCode terminal openen ───────────────────────────────────────────
async function stap4(browser) {
  console.log('Stap 4: VSCode terminal menu');
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 860 });
  await page.setContent(`<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#1e1e1e; font-family: "Segoe UI", -apple-system, sans-serif; width:1280px; height:860px; overflow:hidden; }
    .titlebar { background:#3c3c3c; height:30px; display:flex; align-items:center; justify-content:center; color:#ccc; font-size:12px; }
    .menubar { background:#3c3c3c; height:30px; display:flex; align-items:center; padding:0 8px; gap:2px; border-bottom:1px solid #252526; }
    .menu-item { color:#ccc; font-size:13px; padding:4px 10px; border-radius:4px; cursor:pointer; }
    .menu-item.open { background:#094771; color:white; }
    .layout { display:flex; height:calc(860px - 60px - 22px); }
    .activitybar { width:48px; background:#333; border-right:1px solid #252526; }
    .editor-area { flex:1; display:flex; flex-direction:column; }
    .tabs { background:#2d2d2d; height:36px; display:flex; align-items:center; border-bottom:1px solid #252526; }
    .tab { padding:0 16px; height:100%; display:flex; align-items:center; color:#ccc; font-size:13px; border-right:1px solid #252526; }
    .tab.active { background:#1e1e1e; color:white; border-top:1px solid #007acc; }
    .editor { flex:1; background:#1e1e1e; padding:24px; color:#d4d4d4; font-family:Consolas,monospace; font-size:14px; line-height:1.6; }
    .terminal-panel { height:180px; background:#1e1e1e; border-top:1px solid #3c3c3c; display:flex; flex-direction:column; }
    .terminal-bar { background:#2d2d2d; height:35px; display:flex; align-items:center; padding:0 12px; border-bottom:1px solid #252526; }
    .terminal-bar span { color:#ccc; font-size:13px; }
    .terminal-body { flex:1; padding:10px 16px; font-family:Consolas,monospace; font-size:13px; color:#ccc; }
    .prompt { color:#4ec9b0; }
    .statusbar { background:#007acc; height:22px; display:flex; align-items:center; padding:0 12px; color:#fff; font-size:12px; gap:16px; }
    .dropdown { position:absolute; top:60px; left:244px; background:#252526; border:1px solid #454545; border-radius:4px; width:240px; box-shadow:0 4px 16px rgba(0,0,0,0.5); z-index:100; }
    .dd-item { color:#ccc; font-size:13px; padding:7px 16px; display:flex; justify-content:space-between; align-items:center; }
    .dd-item.active { background:#094771; color:white; }
    .dd-sep { height:1px; background:#454545; margin:3px 0; }
    .shortcut { color:#8c8c8c; font-size:11px; }
    .dd-item.active .shortcut { color:#aaa; }
  </style></head><body>
    <div class="titlebar">dair-agentic-coding — Codespace — Visual Studio Code</div>
    <div class="menubar">
      <div class="menu-item">File</div>
      <div class="menu-item">Edit</div>
      <div class="menu-item">View</div>
      <div class="menu-item">Go</div>
      <div class="menu-item">Run</div>
      <div class="menu-item open">Terminal</div>
      <div class="menu-item">Help</div>
    </div>
    <div class="dropdown" id="menu-dropdown">
      <div class="dd-item active" id="new-terminal">New Terminal <span class="shortcut">Ctrl+&#96;</span></div>
      <div class="dd-item">Split Terminal</div>
      <div class="dd-sep"></div>
      <div class="dd-item">Run Task…</div>
      <div class="dd-item">Run Build Task… <span class="shortcut">Ctrl+Shift+B</span></div>
    </div>
    <div class="layout">
      <div class="activitybar"></div>
      <div class="editor-area">
        <div class="tabs">
          <div class="tab active">README.md</div>
        </div>
        <div class="editor">
          <span style="color:#6a9955"># DAIR — Agentic Coding Sessie</span><br><br>
          <span style="color:#ccc">Welkom bij de agentic coding sessie...</span>
        </div>
        <div class="terminal-panel">
          <div class="terminal-bar"><span>Terminal</span></div>
          <div class="terminal-body">
            <span class="prompt">dev@codespace:/workspace$</span> <span style="color:#ccc">_</span>
          </div>
        </div>
      </div>
    </div>
    <div class="statusbar">
      <span>⎇ main</span>
      <span>Codespaces: dair-agentic-coding</span>
    </div>
  </body></html>`);
  await page.waitForTimeout(300);

  const dropdown = page.locator('#menu-dropdown');
  const newTerminal = page.locator('#new-terminal');
  await highlight(page, dropdown, { step: '④ Open Terminal', label: 'klik op Terminal in de menubalk', color: '#E53E3E', position: 'top' });
  await highlight(page, newTerminal, { step: '④b', label: 'klik op "New Terminal"', color: '#2EA043', position: 'bottom' });
  await shot(page, '04-vscode-terminal');
  await page.close();
}

// ── Stap 5: claude typen ──────────────────────────────────────────────────────
async function stap5(browser) {
  console.log('Stap 5: claude commando');
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 860 });
  await page.setContent(`<!DOCTYPE html><html><head><meta charset="utf-8"><style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#1e1e1e; font-family:"Segoe UI",-apple-system,sans-serif; width:1280px; height:860px; overflow:hidden; }
    .titlebar { background:#3c3c3c; height:30px; display:flex; align-items:center; justify-content:center; color:#ccc; font-size:12px; }
    .menubar { background:#3c3c3c; height:30px; display:flex; align-items:center; padding:0 8px; border-bottom:1px solid #252526; }
    .menu-item { color:#ccc; font-size:13px; padding:4px 10px; border-radius:4px; }
    .layout { display:flex; height:calc(860px - 60px - 22px); }
    .activitybar { width:48px; background:#333; border-right:1px solid #252526; }
    .editor-area { flex:1; display:flex; flex-direction:column; }
    .tabs { background:#2d2d2d; height:36px; display:flex; align-items:center; border-bottom:1px solid #252526; }
    .tab { padding:0 16px; height:100%; display:flex; align-items:center; color:white; font-size:13px; border-top:1px solid #007acc; background:#1e1e1e; }
    .editor { flex:1; background:#1e1e1e; padding:24px; color:#d4d4d4; font-family:Consolas,monospace; font-size:14px; line-height:1.6; }
    .terminal-panel { height:360px; background:#1e1e1e; border-top:1px solid #3c3c3c; display:flex; flex-direction:column; }
    .terminal-bar { background:#2d2d2d; height:35px; display:flex; align-items:center; padding:0 12px; border-bottom:1px solid #252526; }
    .terminal-bar span { color:white; font-size:13px; border-bottom:1px solid white; padding-bottom:2px; }
    .terminal-body { flex:1; padding:14px 18px; font-family:Consolas,"Courier New",monospace; font-size:14px; line-height:1.7; }
    .prompt { color:#4ec9b0; }
    .cmd { color:#fff; font-weight:bold; }
    .statusbar { background:#007acc; height:22px; display:flex; align-items:center; padding:0 12px; color:#fff; font-size:12px; gap:16px; }
    .claude-output { margin-top:16px; border-top:1px solid #333; padding-top:14px; }
    .claude-header { color:#ce9178; font-size:15px; font-weight:bold; margin-bottom:10px; }
    .claude-tip { color:#888; font-size:13px; }
    .claude-tip em { color:#ce9178; font-style:normal; }
    .cursor { display:inline-block; width:8px; height:16px; background:#ccc; vertical-align:middle; animation:blink 1s step-end infinite; }
    @keyframes blink { 50%{opacity:0} }
  </style></head><body>
    <div class="titlebar">dair-agentic-coding — Codespace — Visual Studio Code</div>
    <div class="menubar">
      <div class="menu-item">File</div><div class="menu-item">Edit</div>
      <div class="menu-item">Terminal</div><div class="menu-item">Help</div>
    </div>
    <div class="layout">
      <div class="activitybar"></div>
      <div class="editor-area">
        <div class="tabs"><div class="tab">README.md</div></div>
        <div class="editor"><span style="color:#6a9955"># DAIR — Agentic Coding Sessie</span></div>
        <div class="terminal-panel">
          <div class="terminal-bar"><span>bash</span></div>
          <div class="terminal-body" id="terminal">
            <span class="prompt">dev@codespace:/workspace$</span> <span class="cmd" id="cmd">claude</span><br>
            <div class="claude-output" id="output">
              <div class="claude-header">◆ Claude Code</div>
              <div style="color:#ccc; font-size:14px; margin-bottom:8px;">Klaar om te helpen. Wat wil je bouwen?</div>
              <div class="claude-tip">Tip: typ je opdracht en druk op <em>Enter</em> — bijv. "Maak een script dat mijn data analyseert"</div>
              <br>
              <span class="prompt">&gt;</span> <span class="cursor"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="statusbar">
      <span>⎇ main</span><span>Codespaces: dair-agentic-coding</span>
    </div>
  </body></html>`);
  await page.waitForTimeout(300);

  const cmd = page.locator('#cmd');
  const output = page.locator('#output');
  await highlight(page, cmd, { step: '⑤ Typ "claude"', label: 'en druk op Enter', color: '#2EA043', position: 'top' });
  await shot(page, '05-claude-gestart');
  await page.close();
}

// ── Main ──────────────────────────────────────────────────────────────────────
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    await stap1(browser);
    await stap2(browser);
    await stap3(browser);
    await stap4(browser);
    await stap5(browser);
    console.log('\n✅ Alle screenshots klaar in docs/images/');
  } finally {
    await browser.close();
  }
})();
