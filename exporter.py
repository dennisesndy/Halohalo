"""
Generates a single fully self-contained HTML file for ONE subject.
No server needed. Open directly in any browser on any device.

Three tabs (matching the main app):
  📇 Flashcards  – 3-D flip cards, SM-2 spaced repetition
  🔘 Multiple Choice – up to 4 choices, T/F auto-detected, 10-Q rounds
  ✏️ Identification  – free-recall typing, 10-Q rounds

Data is embedded as JSON in the script tag.
Uses .replace() — NOT f-strings — so JS curly braces are never escaped.
"""

import json


# ── Public API ────────────────────────────────────────────────────────────────

def build_subject_html(subject_name: str, items: list) -> str:
    """Return complete standalone HTML for the given subject + items."""
    safe  = (subject_name
             .replace('&', '&amp;')
             .replace('<', '<')
             .replace('>', '>')
             .replace('"', '"'))
    count = len(items)
    data  = json.dumps(items, ensure_ascii=False)

    if count == 0:
        return _EMPTY_TEMPLATE.replace('__NAME__', safe)

    return (
        _TEMPLATE
        .replace('__NAME__',  safe)
        .replace('__COUNT__', str(count))
        .replace('__DATA__',  data)
    )


def build_export_html(deck_name: str, subjects: list) -> str:
    """Legacy shim: merge all subject items into one file."""
    all_items = []
    for s in subjects:
        all_items.extend(s.get('items', []))
    return build_subject_html(deck_name, all_items)


# ── Templates ──────────────────────────────────────────────────────────────────
# Uses __NAME__ / __COUNT__ / __DATA__ as placeholders.
# Raw string (r"") so backslashes are literal.
# JS curly braces need NO escaping.

_EMPTY_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>No Cards - __NAME__ · Halo-Halo</title>
<style>
body { font-family: system-ui, sans-serif; max-width: 500px; margin: 0 auto; padding: 40px 20px; text-align: center; background: #f8f9fa; color: #333; }
h1 { color: #6c757d; font-size: 1.5rem; margin-bottom: 20px; }
p { font-size: 1rem; line-height: 1.5; color: #666; margin-bottom: 30px; }
.btn { background: #4B164C; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; text-decoration: none; display: inline-block; }
.btn:hover { background: #3a112f; }
</style>
</head>
<body>
<h1>No study cards available</h1>
<p>This exported reviewer has no flashcards or questions yet.</p>
<p><strong>Tip:</strong> Go back to Halo-Halo app, import notes into this subject, then export again.</p>
<a href="#" class="btn" onclick="window.close()">Close</a>
</body>
</html>"""

_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>__NAME__ · Halo-Halo</title>
<!-- Fonts embedded via system stack - fully offline -->
<style>
/* ── tokens ───────────────────────────────────────────────────────── */
:root {
  --purple:  #4B164C;
  --pink:    #F37E9A;
  --pink2:   #fde8ef;
  --cream:   #FFFCF0;
  --cream2:  #f5eedf;
  --white:   #ffffff;
  --text:    #1e1025;
  --muted:   #7a5a85;
  --border:  #e8dff0;
  --green:   #16a34a;
  --green-bg:#f0fdf4;
  --red:     #dc2626;
  --red-bg:  #fef2f2;
  --r0:#94a3b8; --r1:#ef4444; --r2:#f97316;
  --r3:#eab308; --r4:#84cc16; --r5:#22c55e;
}
[data-theme="dark"] {
  --purple:  #d8a4f8;
  --pink:    #f9a8c9;
  --pink2:   #3b1a2e;
  --cream:   #130b1a;
  --cream2:  #1c1128;
  --white:   #231530;
  --text:    #f0e6fa;
  --muted:   #c4a8d4;
  --border:  #3a2450;
  --green:   #4ade80;
  --green-bg:#052e16;
  --red:     #f87171;
  --red-bg:  #450a0a;
}
/* ── reset ────────────────────────────────────────────────────────── */
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
html { -webkit-font-smoothing:antialiased; font-size:15px; }
body {
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;
  background:var(--cream); color:var(--text);
  min-height:100vh;
  transition:background .2s,color .2s;
}
/* ── nav ──────────────────────────────────────────────────────────── */
.nav {
  height:56px; padding:0 18px;
  display:flex; align-items:center; justify-content:space-between;
  background:var(--purple);
  position:sticky; top:0; z-index:50;
}
.nav-left { display:flex; align-items:center; gap:8px; min-width:0; }
.nav-logo  { font-family:'Comic Sans MS',cursive,'Coiny',sans-serif; font-size:1.3rem; color:#fff; font-weight:700; }
.nav-subj  {
  font-size:.8rem; color:rgba(255,255,255,.6); font-weight:600;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:200px;
}
/* dark mode toggle pill */
.dm-wrap {
  background:rgba(255,255,255,.18); border:none;
  border-radius:999px; padding:3px 6px 3px 4px;
  display:flex; align-items:center; gap:4px;
  cursor:pointer; transition:background .2s; flex-shrink:0;
}
.dm-wrap:hover { background:rgba(255,255,255,.28); }
.dm-knob {
  width:22px; height:22px; border-radius:50%;
  background:#fff; display:flex; align-items:center;
  justify-content:center; font-size:.72rem;
}
.dm-label { font-size:.7rem; color:rgba(255,255,255,.7); font-weight:700; }
[... Full content truncated ...]
}
.prog-head .hi { color:var(--pink); font-weight:700; }
.prog-track { height:5px; background:var(--cream2); border-radius:4px; overflow:hidden; margin-bottom:16px; }
.prog-fill  { height:100%; border-radius:4px; background:linear-gradient(90deg,var(--purple),var(--pink)); transition:width .4s; }
/* breakdown bar */
.bbar { display:flex; height:5px; border-radius:4px; overflow:hidden; gap:1px; margin-bottom:3px; }
.bseg { height:100%; min-width:0; transition:width .4s; }
.bleg { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
.bleg-i { display:flex; align-items:center; gap:3px; font-size:.64rem; font-weight:700; color:var(--muted); }
.bleg-d { width:6px; height:6px; border-radius:50%; flex-shrink:0; }
/* ── score pills ──────────────────────────────────────────────────── */
.pills { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:12px; }
.pill  { padding:3px 10px; border-radius:999px; font-size:.71rem; font-weight:700; }
.p-ac  { background:var(--purple); color:#fff; }
.p-gn  { background:var(--green-bg); color:var(--green); }
.p-rd  { background:var(--red-bg); color:var(--red); }
.p-pk  { background:var(--pink); color:#fff; }
/* ── 3-D flashcard ────────────────────────────────────────────────── */
.scene {
  perspective:1000px; height:210px;
  cursor:pointer; margin-bottom:14px; user-select:none;
}
.card3 {
  width:100%; height:100%; position:relative;
  transform-style:preserve-3d;
  transition:transform .6s cubic-bezier(.4,0,.2,1);
}
.card3.flip { transform:rotateY(180deg); }
.face {
  position:absolute; inset:0; backface-visibility:hidden;
  border-radius:14px;
  display:flex; flex-direction:column;
  align-items:center; justify-content:center;
  padding:26px 22px; text-align:center;
}
.f-front {
  background:var(--white); border:1.5px solid var(--border);
  box-shadow:0 2px 10px rgba(0,0,0,.05);
}
.f-front[data-r="1"] { border-color:var(--r1); }
.f-front[data-r="2"] { border-color:var(--r2); }
.f-front[data-r="3"] { border-color:var(--r3); }
.f-front[data-r="4"] { border-color:var(--r4); }
.f-front[data-r="5"] { border-color:var(--r5); }
.f-back {
  background:var(--purple); color:#fff;
  transform:rotateY(180deg);
  box-shadow:0 4px 18px rgba(75,22,76,.22);
}
.ftag  { font-size:.58rem; letter-spacing:.14em; text-transform:uppercase; opacity:.38; margin-bottom:8px; font-weight:700; }
.ftext { font-size:1.1rem; font-weight:700; line-height:1.45; max-width:480px; }
.fhint { font-size:.68rem; opacity:.3; margin-top:12px; font-style:italic; }
/* rating badge on card */
.rbadge {
  position:absolute; top:9px; right:11px;
  padding:2px 8px; border-radius:999px;
  font-size:.6rem; font-weight:800; color:#fff;
}
.rb0{background:var(--r0)} .rb1{background:var(--r1)} .rb2{background:var(--r2)}
.rb3{background:var(--r3);color:#1a1a1a} .rb4{background:var(--r4);color:#1a1a1a}
.rb5{background:var(--r5)}
/* ── rating strip ─────────────────────────────────────────────────── */
.rstrip { text-align:center; margin-bottom:14px; }
.rlbl   { font-size:.7rem; color:var(--muted); font-weight:600; margin-bottom:7px; display:block; }
.rrow   { display:flex; justify-content:center; gap:5px; }
.rbtn {
  display:flex; flex-direction:column; align-items:center; gap:1px;
  border:none; border-radius:9px; padding:7px 10px; cursor:pointer;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:.88rem; font-weight:800;
  color:#fff; min-width:48px; transition:transform .12s;
}
.rbtn small { font-size:.52rem; font-weight:600; opacity:.85; }
.rbtn:hover { transform:translateY(-2px); }
.rb-1{background:var(--r1)} .rb-2{background:var(--r2)}
.rb-3{background:var(--r3);color:#1a1a1a} .rb-4{background:var(--r4);color:#1a1a1a}
.rb-5{background:var(--r5)}
/* ── stat grid ────────────────────────────────────────────────────── */
.sgrid { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; margin-bottom:14px; }
.sbox  { background:var(--white); border:1px solid var(--border); border-radius:10px; padding:10px 6px; text-align:center; }
.snum  { font-family:'Comic Sans MS',cursive,'Coiny',sans-serif; font-size:1.5rem; line-height:1; font-weight:700; }
.slbl  { font-size:.6rem; color:var(--muted); font-weight:700; margin-top:2px; }
/* ── question card ────────────────────────────────────────────────── */
.qcard {
  background:var(--white); border:1.5px solid var(--border);
  border-radius:14px; padding:24px 20px;
  text-align:center; font-size:1.08rem; font-weight:700;
  min-height:88px; display:flex; align-items:center; justify-content:center;
  margin-bottom:14px; line-height:1.5;
  box-shadow:0 1px 6px rgba(0,0,0,.04);
}
/* ── choices ──────────────────────────────────────────────────────── */
.choices { display:flex; flex-direction:column; gap:7px; margin-bottom:12px; }
.ch {
  background:var(--white); border:1.5px solid var(--border); color:var(--text);
  border-radius:11px; padding:11px 14px; text-align:left;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:.88rem; font-weight:600;
  cursor:pointer; transition:border-color .15s;
  display:flex; align-items:center; gap:8px; width:100%;
}
.cl {
  width:22px; height:22px; border-radius:50%; flex-shrink:0;
  background:var(--cream2); color:var(--muted);
  font-size:.68rem; font-weight:800;
  display:flex; align-items:center; justify-content:center;
}
.ch:hover:not(:disabled) { border-color:var(--pink); }
.ch:hover:not(:disabled) .cl { background:var(--pink); color:#fff; }
.ch.correct { background:var(--green-bg); border-color:var(--green); color:var(--green); }
.ch.correct .cl { background:var(--green); color:#fff; }
.ch.wrong   { background:var(--red-bg); border-color:var(--red); color:var(--red); }
.ch.wrong   .cl { background:var(--red); color:#fff; }
.ch:disabled { cursor:default; }
/* ── feedback ─────────────────────────────────────────────────────── */
.fb {
  padding:10px 14px; border-radius:10px; font-size:.84rem;
  line-height:1.5; margin-bottom:12px; border-left:3px solid transparent;
}
.fb-lbl { font-weight:800; display:block; margin-bottom:2px; }
.fbok   { background:var(--green-bg); border-color:var(--green); color:var(--green); }
.fbbad  { background:var(--red-bg);   border-color:var(--red);   color:var(--red);   }
/* ── id input ─────────────────────────────────────────────────────── */
.idinp {
  width:100%; padding:11px 15px;
  border:1.5px solid var(--border); border-radius:11px;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:.92rem;
  background:var(--white); color:var(--text);
  outline:none; margin-bottom:10px; transition:border-color .18s;
}
.idinp:focus { border-color:var(--pink); }
.idinp.ok  { border-color:var(--green); background:var(--green-bg); }
.idinp.bad { border-color:var(--red);   background:var(--red-bg);   }
/* ── buttons ──────────────────────────────────────────────────────── */
.acts { display:flex; align-items:center; gap:7px; margin-top:8px; }
.ml   { margin-left:auto; }
.btn {
  display:inline-flex; align-items:center; justify-content:center;
  padding:8px 18px; border:none; border-radius:10px;
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size:.8rem; font-weight:700;
  cursor:pointer; transition:filter .15s,transform .1s; white-space:nowrap;
}
.btn:hover  { filter:brightness(1.08); }
.btn:active { transform:scale(.97); }
.btn-primary   { background:var(--purple); color:#fff; }
.btn-secondary { background:var(--pink);   color:#fff; }
.btn-ghost {
  background:transparent; border:1.5px solid var(--border); color:var(--muted);
}
.btn-ghost:hover { border-color:var(--purple); color:var(--purple); }
.btn-sm { padding:6px 14px; font-size:.78rem; border-radius:8px; }
/* ── done card ────────────────────────────────────────────────────── */
.done {
  background:var(--white); border:1px solid var(--border);
  border-radius:14px; padding:32px 22px; text-align:center; margin-top:14px;
}
.done h3    { font-family:'Comic Sans MS',cursive,'Coiny',sans-serif; font-size:1.4rem; color:var(--purple); margin-bottom:6px; }
.done-score { font-family:'Comic Sans MS',cursive,'Coiny',sans-serif; font-size:3rem; color:var(--purple); line-height:1; }
.done-sub   { color:var(--muted); font-size:.8rem; margin-bottom:14px; }
.done-btns  { display:flex; gap:8px; justify-content:center; flex-wrap:wrap; }
/* ── round notice ─────────────────────────────────────────────────── */
.rnotice {
  background:var(--pink2); border:1px solid rgba(243,126,154,.3);
  border-radius:8px; padding:8px 12px;
  font-size:.78rem; font-weight:700; color:var(--purple);
  margin-bottom:12px; text-align:center;
}
.hidden { display:none !important; }
</style>
</head>
<body>

<!-- ── nav ── -->
<nav class="nav">
  <div class="nav-left">
    <span class="nav-logo">🍧 Halo-Halo</span>
    <span class="nav-subj">__NAME__</span>
  </div>
  <button class="dm-wrap" onclick="toggleDark()" title="Toggle dark mode">
    <span class="dm-knob" id="dm-knob">🌙</span>
    <span class="dm-label" id="dm-label">Light</span>
  </button>
</nav>

<!-- ── tabs ── -->
<div class="tabs">
  <button class="tab-btn active" id="tab-fc" onclick="setMode('fc',this)">📇 Flashcards</button>
  <button class="tab-btn"        id="tab-mc" onclick="setMode('mc',this)">🔘 Multiple Choice</button>
  <button class="tab-btn"        id="tab-id" onclick="setMode('id',this)">✏️ Identification</button>
</div>

<!-- ══════════════════════════════════════════════════════════════════
     FLASHCARDS
     ══════════════════════════════════════════════════════════════════ -->
<div id="panel-fc" class="panel show">
  <div class="wrap">
    <!-- breakdown colour bar -->
    <div class="bbar" id="fc-bbar"></div>
    <div class="bleg" id="fc-bleg"></div>
    <!-- position / mastery -->
    <div class="prog-head">
      <span id="fc-pos">Card — of —</span>
      <span class="hi" id="fc-pct">0% mastered</span>
    </div>
    <!-- 3-D card -->
    <div class="scene" id="fc-scene" onclick="flipCard()">
      <div class="card3" id="fc-card">
        <div class="face f-front" id="fc-front" data-r="0">
          <div class="rbadge rb0" id="fc-badge">New</div>
          <div class="ftag">term</div>
          <p  class="ftext" id="fc-term">—</p>
          <p  class="fhint">tap to flip</p>
        </div>
        <div class="face f-back">
          <div class="ftag" style="opacity:.3">definition</div>
          <p class="ftext" id="fc-def">—</p>
        </div>
      </div>
    </div>
    <!-- rating strip (hidden until flipped) -->
    <div class="rstrip hidden" id="rstrip">
      <span class="rlbl">How well did you know this?</span>
      <div class="rrow">
        <button class="rbtn rb-1" onclick="rate(1)">1<small>Again</small></button>
        <button class="rbtn rb-2" onclick="rate(2)">2<small>Hard</small></button>
        <button class="rbtn rb-3" onclick="rate(3)">3<small>Okay</small></button>
        <button class="rbtn rb-4" onclick="rate(4)">4<small>Good</small></button>
        <button class="rbtn rb-5" onclick="rate(5)">5<small>Easy</small></button>
      </div>
    </div>
    <!-- per-rating stat grid -->
    <div class="sgrid">
      <div class="sbox"><div class="snum" id="s0" style="color:var(--r0)">0</div><div class="slbl">Unseen</div></div>
      <div class="sbox"><div class="snum" id="s1" style="color:var(--r1)">0</div><div class="slbl">Again</div></div>
      <div class="sbox"><div class="snum" id="s2" style="color:var(--r2)">0</div><div class="slbl">Hard</div></div>
      <div class="sbox"><div class="snum" id="s3" style="color:var(--r3)">0</div><div class="slbl">Okay</div></div>
      <div class="sbox"><div class="snum" id="s4" style="color:var(--r4)">0</div><div class="slbl">Good</div></div>
      <div class="sbox"><div class="snum" id="s5" style="color:var(--r5)">0</div><div class="slbl">Mastered</div></div>
    </div>
    <div class="acts">
      <button class="btn btn-ghost btn-sm" onclick="initFC()">↺ Restart</button>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════════
     MULTIPLE CHOICE
     ══════════════════════════════════════════════════════════════════ -->
<div id="panel-mc" class="panel">
  <div class="wrap">
    <div class="pills" id="mc-pills"></div>
    <div class="prog-track"><div class="prog-fill" id="mc-bar" style="width:0%"></div></div>
    <div class="prog-head" style="margin-top:-10px;margin-bottom:16px">
      <span id="mc-pos">Question — of 10</span>
      <span class="hi" id="mc-pct">—</span>
    </div>
    <div class="rnotice hidden" id="mc-notice"></div>
    <div class="qcard"   id="mc-q">Loading…</div>
    <div class="choices" id="mc-choices"></div>
    <div class="fb hidden" id="mc-fb"></div>
    <div class="acts">
      <button class="btn btn-ghost btn-sm" onclick="initMC()">↺ Restart</button>
      <button class="btn btn-secondary btn-sm ml hidden" id="mc-nxt" onclick="nextMC()">Next →</button>
    </div>
    <div class="done hidden" id="mc-done">
      <div style="font-size:1.6rem;margin-bottom:8px">🎉</div>
      <h3>Round Complete!</h3>
      <div class="done-score" id="mc-ds"></div>
      <p class="done-sub" id="mc-dp"></p>
      <div class="done-btns">
        <button class="btn btn-ghost btn-sm" onclick="initMC()">Start Over</button>
        <button class="btn btn-primary btn-sm" onclick="nextRoundMC()">Next Round →</button>
      </div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════════════════
     IDENTIFICATION
     ══════════════════════════════════════════════════════════════════ -->
<div id="panel-id" class="panel">
  <div class="wrap">
    <div class="pills" id="id-pills"></div>
    <div class="prog-track"><div class="prog-fill" id="id-bar" style="width:0%"></div></div>
    <div class="prog-head" style="margin-top:-10px;margin-bottom:16px">
      <span id="id-pos">Question — of 10</span>
      <span class="hi" id="id-pct">—</span>
    </div>
    <div class="rnotice hidden" id="id-notice"></div>
    <div class="qcard" id="id-q">Loading…</div>
    <input class="idinp" id="id-inp" type="text" placeholder="Type the definition here…" autocomplete="off"/>
    <div class="fb hidden" id="id-fb"></div>
    <div class="acts">
      <button class="btn btn-ghost btn-sm" onclick="initID()">↺ Restart</button>
      <button class="btn btn-primary btn-sm" id="id-sub" onclick="submitID()">Submit</button>
      <button class="btn btn-secondary btn-sm ml hidden" id="id-nxt" onclick="nextID()">Next →</button>
    </div>
    <div class="done hidden" id="id-done">
      <div style="font-size:1.6rem;margin-bottom:8px">🎉</div>
      <h3>Round Complete!</h3>
      <div class="done-score" id="id-ds"></div>
      <p class="done-sub" id="id-dp"></p>
      <div class="done-btns">
        <button class="btn btn-ghost btn-sm" onclick="initID()">Start Over</button>
        <button class="btn btn-primary btn-sm" onclick="nextRoundID()">Next Round →</button>
      </div>
    </div>
  </div>
</div>

<script>
// ── embedded study data ────────────────────────────────────────────
const ITEMS  = __DATA__;
const ROUNDS = 10;

// ── helpers ────────────────────────────────────────────────────────
function el(id) { return document.getElementById(id); }
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function sample(arr, n) { return shuffle(arr).slice(0, n); }

// ── true/false detection ───────────────────────────────────────────
const TF_SET = new Set(['true','false','yes','no','correct','incorrect','right','wrong','always','never']);
function isTF(defStr) { return TF_SET.has(defStr.trim().toLowerCase()); }

// ── dark mode ──────────────────────────────────────────────────────
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  el('dm-knob').textContent  = t === 'dark' ? '☀️' : '🌙';
  el('dm-label').textContent = t === 'dark' ? 'Dark' : 'Light';
}
function toggleDark() {
  const cur  = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  // No storage - session only, works everywhere
}
(function() {
  applyTheme('light');  // Default light theme - universal compatibility
})();

// ── tab / mode switching ───────────────────────────────────────────
function setMode(mode, btn) {
  // hide all panels
  ['fc','mc','id'].forEach(function(m) {
    el('panel-' + m).classList.remove('show');
  });
  // deactivate all tabs
  document.querySelectorAll('.tab-btn').forEach(function(b) {
    b.classList.remove('active');
  });
  // show selected panel & activate tab
  el('panel-' + mode).classList.add('show');
  btn.classList.add('active');
  // init the mode
  if (mode === 'fc') initFC();
  if (mode === 'mc') initMC();
  if (mode === 'id') initID();
}

// ════════════════════════════════════════════════════════════════════
// FLASHCARDS
// ════════════════════════════════════════════════════════════════════
const RCOLS  = ['#94a3b8','#ef4444','#f97316','#eab308','#84cc16','#22c55e'];
const RLABELS = ['New','Again','Hard','Okay','Good','Easy'];

var fcDeck   = [];
var fcIdx    = 0;
var fcFlipped = false;

function initFC() {
  // build deck: shuffle items, all ratings start at 0
  fcDeck = shuffle(ITEMS).map(function(it) {
    return { term: it.term, def: it.def, r: 0 };
  });
  fcIdx     = 0;
  fcFlipped = false;
  el('fc-card').classList.remove('flip');
  el('rstrip').classList.add('hidden');
  renderFC();
}

function renderFC() {
  // count per rating bucket
  var cnt = [0,0,0,0,0,0];
  fcDeck.forEach(function(c) { cnt[c.r]++; });
  var total = fcDeck.length;

  // breakdown bar
  var barHTML = '';
  var legHTML = '';
  cnt.forEach(function(n, i) {
    if (!n) return;
    var pct = Math.round(n / total * 100);
    barHTML += '<div class="bseg" style="width:' + pct + '%;background:' + RCOLS[i] + '" title="' + RLABELS[i] + ': ' + n + '"></div>';
    legHTML += '<span class="bleg-i"><span class="bleg-d" style="background:' + RCOLS[i] + '"></span>' + RLABELS[i] + ' (' + n + ')</span>';
  });
  el('fc-bbar').innerHTML = barHTML;
  el('fc-bleg').innerHTML = legHTML;

  // stat tiles
  cnt.forEach(function(n, i) { el('s' + i).textContent = n; });

  // done?
  if (fcIdx >= fcDeck.length) {
    el('fc-term').textContent = '🎉 All done!';
    el('fc-def').textContent  = 'Great work!';
    el('fc-pos').textContent  = 'Session complete';
    el('fc-pct').textContent  = '100% mastered';
    el('rstrip').classList.add('hidden');
    return;
  }

  var card = fcDeck[fcIdx];
  el('fc-term').textContent = card.term;
  el('fc-def').textContent  = card.def;
  el('fc-pos').textContent  = 'Card ' + (fcIdx + 1) + ' of ' + fcDeck.length;

  var mastered  = cnt[5];
  var masteredPct = total ? Math.round(mastered / total * 100) : 0;
  el('fc-pct').textContent = masteredPct + '% mastered';

  // colour-coded border & badge
  var front = el('fc-front');
  front.setAttribute('data-r', card.r);
  var badge = el('fc-badge');
  badge.textContent = RLABELS[card.r];
  badge.className   = 'rbadge rb' + card.r;

  // reset flip
  el('fc-card').classList.remove('flip');
  el('rstrip').classList.add('hidden');
  fcFlipped = false;
}

function flipCard() {
  if (fcIdx >= fcDeck.length) return;
  fcFlipped = !fcFlipped;
  el('fc-card').classList.toggle('flip', fcFlipped);
  el('rstrip').classList.toggle('hidden', !fcFlipped);
}

function rate(r) {
  if (!fcFlipped) return;

  // remove current card
  var card = fcDeck.splice(fcIdx, 1)[0];
  card.r = r;

  // re-insert based on rating
  var rem = fcDeck.length - fcIdx;
  if      (r === 1) fcDeck.splice(Math.min(fcIdx + 3, fcDeck.length), 0, card);
  else if (r === 2) fcDeck.splice(Math.min(fcIdx + 5, fcDeck.length), 0, card);
  else if (r === 3) fcDeck.splice(fcIdx + Math.max(1, Math.floor(rem / 2)), 0, card);
  else if (r === 4) fcDeck.splice(fcIdx + Math.max(1, Math.floor(rem * 3 / 4)), 0, card);
  else              fcDeck.push(card);  // r===5 → mastered, end of deck

  renderFC();
}

// ════════════════════════════════════════════════════════════════════
// ROUND QUEUE (shared by MC and ID)
// ════════════════════════════════════════════════════════════════════
function buildQueue(prevWrong) {
  var pwSet = {};
  prevWrong.forEach(function(t) { pwSet[t] = true; });
  var all      = ITEMS.map(function(i) { return i.term; });
  var priority = all.filter(function(t) { return pwSet[t]; });
  var fresh    = shuffle(all.filter(function(t) { return !pwSet[t]; }));
  return shuffle(priority.concat(fresh)).slice(0, ROUNDS);
}

// ════════════════════════════════════════════════════════════════════
// MULTIPLE CHOICE
// ════════════════════════════════════════════════════════════════════
var mcTotal   = 0;
var mcCorrect = 0;
var mcQ       = 0;
var mcAnswered = false;
var mcWrong   = [];
var mcRound   = 1;
var mcQueue   = [];
var mcCurrentTerm = '';

function initMC() {
  mcTotal   = 0;
  mcCorrect = 0;
  mcQ       = 0;
  mcAnswered = false;
  mcWrong   = [];
  mcRound   = 1;
  mcQueue   = buildQueue([]);
  el('mc-done').classList.add('hidden');
  el('mc-notice').classList.add('hidden');
  renderMCPills();
  loadMCQuestion();
}

function loadMCQuestion() {
  if (mcQ >= ROUNDS || mcQueue.length === 0) { showMCDone(); return; }

  var termStr = mcQueue.shift();
  var item    = null;
  for (var i = 0; i < ITEMS.length; i++) {
    if (ITEMS[i].term === termStr) { item = ITEMS[i]; break; }
  }
  if (!item) item = ITEMS[Math.floor(Math.random() * ITEMS.length)];

  var correct = item.def;
  mcCurrentTerm = item.term;
  mcAnswered = false;

  el('mc-q').textContent = item.term;
  el('mc-fb').classList.add('hidden');
  el('mc-nxt').classList.add('hidden');
  el('mc-pos').textContent = 'Question ' + (mcQ + 1) + ' of ' + ROUNDS;

  // build choices
  var choices;
  if (isTF(correct)) {
    choices = ['True', 'False'];
  } else {
    var otherDefs = [];
    for (var j = 0; j < ITEMS.length; j++) {
      if (ITEMS[j].def.toLowerCase() !== correct.toLowerCase()) {
        otherDefs.push(ITEMS[j].def);
      }
    }
    var distractors = sample(otherDefs, 3);
    choices = shuffle(distractors.concat([correct]));
  }

  var letters = ['A','B','C','D'];
  var ch = el('mc-choices');
  ch.innerHTML = '';
  choices.forEach(function(c, idx) {
    var btn = document.createElement('button');
    btn.className = 'ch';
    btn.innerHTML = '<span class="cl">' + (letters[idx] || '') + '</span><span>' + esc(c) + '</span>';
    btn.onclick   = (function(b, chosen, corr, term) {
      return function() { answerMC(b, chosen, corr, term); };
    })(btn, c, correct, item.term);
    ch.appendChild(btn);
  });

  renderMCPills();
}

function answerMC(btn, chosen, correct, term) {
  if (mcAnswered) return;
  mcAnswered = true;

  var ok = chosen.trim().toLowerCase() === correct.trim().toLowerCase();
  if (ok) {
    mcCorrect++;
  } else {
    if (mcWrong.indexOf(term) === -1) mcWrong.push(term);
  }
  mcTotal++;
  mcQ++;

  // colour all buttons
  var allBtns = document.querySelectorAll('.ch');
  allBtns.forEach(function(b) {
    b.disabled = true;
    var txt = b.querySelector('span:last-child').textContent;
    if (txt.toLowerCase() === correct.toLowerCase()) {
      b.classList.add('correct');
    } else if (b === btn && !ok) {
      b.classList.add('wrong');
    }
  });

  // feedback
  var fb = el('mc-fb');
  if (ok) {
    fb.innerHTML = '<span class="fb-lbl">✅ Correct!</span>Right — ' + esc(correct);
    fb.className = 'fb fbok';
  } else {
    fb.innerHTML = '<span class="fb-lbl">❌ Wrong</span>Correct answer: ' + esc(correct);
    fb.className = 'fb fbbad';
  }
  fb.classList.remove('hidden');
  el('mc-nxt').classList.remove('hidden');

  renderMCPills();
}

function nextMC() { loadMCQuestion(); }

function nextRoundMC() {
  mcRound++;
  var prevWrong = mcWrong.slice();
  mcWrong    = [];
  mcQ        = 0;
  mcAnswered = false;
  mcQueue    = buildQueue(prevWrong);
  el('mc-done').classList.add('hidden');

  if (prevWrong.length > 0) {
    el('mc-notice').textContent =
      'Round ' + mcRound + ' · Revisiting ' + prevWrong.length +
      ' missed item' + (prevWrong.length > 1 ? 's' : '') + ' 🔄';
    el('mc-notice').classList.remove('hidden');
  } else {
    el('mc-notice').classList.add('hidden');
  }

  renderMCPills();
  loadMCQuestion();
}

function showMCDone() {
  var pct = mcTotal ? Math.round(mcCorrect / mcTotal * 100) : 0;
  el('mc-ds').textContent = pct + '%';
  el('mc-dp').textContent = mcCorrect + ' correct out of ' + mcTotal;
  el('mc-done').classList.remove('hidden');
  renderMCPills();
}

function renderMCPills() {
  var pct   = mcTotal ? Math.round(mcCorrect / mcTotal * 100) : 0;
  var wrong = mcTotal - mcCorrect;
  el('mc-pills').innerHTML =
    '<span class="pill p-ac">📋 ' + mcTotal + '</span>' +
    '<span class="pill p-gn">✅ ' + mcCorrect + '</span>' +
    '<span class="pill p-rd">❌ ' + wrong + '</span>' +
    '<span class="pill p-pk">🎯 ' + (mcTotal ? pct + '%' : '—') + '</span>';
  el('mc-bar').style.width = Math.min(mcQ / ROUNDS * 100, 100) + '%';
  el('mc-pct').textContent = mcTotal ? pct + '%' : '—';
}

// ════════════════════════════════════════════════════════════════════
// IDENTIFICATION
// ════════════════════════════════════════════════════════════════════
var idTotal    = 0;
var idCorrect  = 0;
var idQ        = 0;
var idAnswered = false;
var idWrong    = [];
var idRound    = 1;
var idQueue    = [];
var idCurDef   = '';
var idCurTerm  = '';

function initID() {
  idTotal    = 0;
  idCorrect  = 0;
  idQ        = 0;
  idAnswered = false;
  idWrong    = [];
  idRound    = 1;
  idQueue    = buildQueue([]);
  el('id-done').classList.add('hidden');
  el('id-notice').classList.add('hidden');
  renderIDPills();
  loadIDQuestion();
}

function loadIDQuestion() {
  if (idQ >= ROUNDS || idQueue.length === 0) { showIDDone(); return; }

  var termStr = idQueue.shift();
  var item    = null;
  for (var i = 0; i < ITEMS.length; i++) {
    if (ITEMS[i].term === termStr) { item = ITEMS[i]; break; }
  }
  if (!item) item = ITEMS[Math.floor(Math.random() * ITEMS.length)];

  idCurDef  = item.def;
  idCurTerm = item.term;
  idAnswered = false;

  el('id-q').textContent = item.term;
  el('id-pos').textContent = 'Question ' + (idQ + 1) + ' of ' + ROUNDS;

  var inp = el('id-inp');
  inp.value     = '';
  inp.className = 'idinp';
  inp.disabled  = false;
  inp.focus();

  el('id-fb').classList.add('hidden');
  el('id-sub').classList.remove('hidden');
  el('id-nxt').classList.add('hidden');
  renderIDPills();
}

function submitID() {
  if (idAnswered || !idCurDef) return;
  idAnswered = true;

  var inp = el('id-inp');
  var ok  = inp.value.trim().toLowerCase() === idCurDef.trim().toLowerCase();

  if (ok) {
    idCorrect++;
  } else {
    if (idWrong.indexOf(idCurTerm) === -1) idWrong.push(idCurTerm);
  }
  idTotal++;
  idQ++;

  inp.disabled  = true;
  inp.className = 'idinp ' + (ok ? 'ok' : 'bad');

  var fb = el('id-fb');
  if (ok) {
    fb.innerHTML = '<span class="fb-lbl">✅ Correct!</span>Well done!';
    fb.className = 'fb fbok';
  } else {
    fb.innerHTML = '<span class="fb-lbl">❌ Wrong</span>Correct answer: ' + esc(idCurDef);
    fb.className = 'fb fbbad';
  }
  fb.classList.remove('hidden');

  el('id-sub').classList.add('hidden');
  el('id-nxt').classList.remove('hidden');
  renderIDPills();
}

function nextID() { loadIDQuestion(); }

function nextRoundID() {
  idRound++;
  var prevWrong = idWrong.slice();
  idWrong    = [];
  idQ        = 0;
  idAnswered = false;
  idQueue    = buildQueue(prevWrong);
  el('id-done').classList.add('hidden');

  if (prevWrong.length > 0) {
    el('id-notice').textContent =
      'Round ' + idRound + ' · Revisiting ' + prevWrong.length +
      ' missed item' + (prevWrong.length > 1 ? 's' : '') + ' 🔄';
    el('id-notice').classList.remove('hidden');
  } else {
    el('id-notice').classList.add('hidden');
  }

  renderIDPills();
  loadIDQuestion();
}

function showIDDone() {
  var pct = idTotal ? Math.round(idCorrect / idTotal * 100) : 0;
  el('id-ds').textContent = idTotal ? pct + '%' : '0%';
  el('id-dp').textContent = idCorrect + ' correct out of ' + idTotal;
  el('id-done').classList.remove('hidden');
  renderIDPills();
}

function renderIDPills() {
  var pct   = idTotal ? Math.round(idCorrect / idTotal * 100) : 0;
  var wrong = idTotal - idCorrect;
  el('id-pills').innerHTML =
    '<span class="pill p-ac">📋 ' + idTotal + '</span>' +
    '<span class="pill p-gn">✅ ' + idCorrect + '</span>' +
    '<span class="pill p-rd">❌ ' + wrong + '</span>' +
    '<span class="pill p-pk">🎯 ' + (idTotal ? pct + '%' : '—') + '</span>';
  el('id-bar').style.width = Math.min(idQ / ROUNDS * 100, 100) + '%';
  el('id-pct').textContent = idTotal ? pct + '%' : '—';
}

// ── enter key for identification ───────────────────────────────────
el('id-inp').addEventListener('keydown', function(e) {
  if (e.key !== 'Enter') return;
  if (!el('id-nxt').classList.contains('hidden')) nextID();
  else submitID();
});

// ── boot: start flashcards ─────────────────────────────────────────
initFC();
</script>
</body>
</html>"""