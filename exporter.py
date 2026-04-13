"""
exporter.py
-----------
Generates a fully standalone HTML reviewer file.
The JS-heavy template lives here so engine.py stays clean Python.
"""

import json


def build_export_html(deck_name: str, subjects: list) -> str:
    """
    Build a self-contained HTML string with embedded JS study modes.
    subjects = [{"name": str, "items": [{"term": str, "def": str}]}]
    """
    payload   = json.dumps(subjects, ensure_ascii=False)
    safe_name = deck_name.replace('"', "'")

    # ── Inline template (f-string, JS braces doubled) ─────────────────────
    return (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8"/>\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0"/>\n'
        f'<title>🍧 {safe_name} – Halo-Halo Reviewer</title>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Lekkerli+One'
        '&family=Nunito:wght@400;500;600;700&display=swap" rel="stylesheet"/>\n'
        + _EXPORT_STYLE
        + f'</head>\n<body>\n'
        + f'<header><h1>🍧 Halo-Halo</h1>'
        + f'<span class="deck-label">{safe_name}</span></header>\n'
        + _EXPORT_NAV
        + _EXPORT_BODY
        + f'<script>\nconst SUBJECTS = {payload};\nconst ROUNDS = 10;\n'
        + _EXPORT_JS
        + '</script>\n</body>\n</html>'
    )


# ── CSS ───────────────────────────────────────────────────────────────────────
_EXPORT_STYLE = """
<style>
:root{--purple:#4B164C;--purple-dk:#370f37;--pink:#F37E9A;--cream:#FFFCF0;
  --white:#fff;--text:#2d1535;--muted:#8b6a93;--green:#22c55e;
  --green-lt:#dcfce7;--green-dk:#166534;--red:#ef4444;
  --red-lt:#fee2e2;--red-dk:#991b1b;--yellow:#f59e0b;
  --glass:rgba(255,252,240,.65);--gborder:rgba(255,255,255,.55);}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Nunito',sans-serif;background:var(--cream);color:var(--text);min-height:100vh;overflow-x:hidden}
body::before{content:'';position:fixed;width:500px;height:500px;
  background:radial-gradient(circle,rgba(243,126,154,.18) 0%,transparent 70%);
  top:-160px;right:-100px;border-radius:50%;filter:blur(70px);pointer-events:none;z-index:0}
header{background:var(--purple);padding:16px 32px;display:flex;align-items:center;
  justify-content:space-between;box-shadow:0 2px 20px rgba(75,22,76,.28);position:relative;z-index:10}
header h1{font-family:'Lekkerli One',cursive;font-size:1.6rem;color:var(--cream);letter-spacing:.02em}
.deck-label{color:rgba(255,252,240,.55);font-size:.85rem;font-weight:500}
nav{background:rgba(75,22,76,.92);backdrop-filter:blur(12px);
  display:flex;gap:4px;justify-content:center;padding:10px 20px;position:relative;z-index:10}
nav button{background:transparent;border:1.5px solid rgba(243,126,154,.4);
  color:rgba(255,252,240,.6);padding:8px 22px;border-radius:999px;cursor:pointer;
  font-family:'Nunito',sans-serif;font-size:.85rem;font-weight:700;transition:all .2s}
nav button.active,nav button:hover{background:var(--pink);color:#fff;border-color:var(--pink)}
.sub-nav{display:flex;gap:7px;justify-content:center;padding:10px 20px;
  background:rgba(255,252,240,.7);backdrop-filter:blur(8px);
  border-bottom:1px solid rgba(75,22,76,.1);flex-wrap:wrap}
.sub-btn{background:transparent;border:1.5px solid rgba(75,22,76,.18);color:var(--muted);
  padding:5px 15px;border-radius:999px;cursor:pointer;font-family:'Nunito',sans-serif;
  font-size:.78rem;font-weight:700;transition:all .2s}
.sub-btn.active{background:var(--purple);color:var(--cream);border-color:var(--purple)}
#app{max-width:680px;margin:28px auto;padding:0 18px 80px;position:relative;z-index:1}
.hidden{display:none!important}
.glass{background:var(--glass);backdrop-filter:blur(18px);border:1px solid var(--gborder)}
.prog-track{background:rgba(75,22,76,.1);border-radius:8px;height:7px;overflow:hidden;margin-bottom:6px}
.prog-fill{height:100%;background:linear-gradient(90deg,var(--purple),var(--pink));
  border-radius:8px;transition:width .5s ease}
.prog-meta{display:flex;justify-content:space-between;font-size:.75rem;
  color:var(--muted);font-weight:600;margin-bottom:20px}
.prog-meta .pct{color:var(--pink);font-weight:700}
.score-bar{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:12px}
.s-pill{padding:4px 13px;border-radius:999px;font-size:.75rem;font-weight:700}
.sp-t{background:var(--purple);color:var(--cream)}
.sp-c{background:var(--green-lt);color:var(--green-dk)}
.sp-w{background:var(--red-lt);color:var(--red-dk)}
.sp-p{background:var(--pink);color:#fff}
.card-scene{perspective:1200px;height:220px;cursor:pointer;margin:6px 0 16px;user-select:none}
.card-3d{width:100%;height:100%;position:relative;transform-style:preserve-3d;
  transition:transform .65s cubic-bezier(.4,0,.2,1)}
.card-3d.flipped{transform:rotateY(180deg)}
.card-face{position:absolute;inset:0;backface-visibility:hidden;border-radius:22px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  padding:32px;text-align:center}
.card-front{background:var(--glass);backdrop-filter:blur(18px);
  border:2px solid rgba(243,126,154,.3);
  box-shadow:0 8px 28px rgba(75,22,76,.1),inset 0 1px 0 rgba(255,255,255,.6)}
.card-back{background:linear-gradient(135deg,var(--purple),#7a3d7b);color:var(--cream);
  border:2px solid rgba(243,126,154,.4);transform:rotateY(180deg);
  box-shadow:0 8px 28px rgba(75,22,76,.28)}
.face-tag{font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;
  opacity:.4;margin-bottom:10px;font-weight:700}
.face-text{font-size:1.25rem;font-weight:700;line-height:1.45;max-width:500px}
.face-hint{font-size:.72rem;opacity:.32;margin-top:14px;font-style:italic}
.r-row{display:flex;justify-content:center;gap:7px;flex-wrap:wrap;margin-bottom:16px}
.r-lbl{text-align:center;font-size:.75rem;color:var(--muted);font-weight:600;
  margin-bottom:9px;display:block}
.r-btn{display:flex;flex-direction:column;align-items:center;gap:2px;
  border:none;border-radius:12px;padding:9px 12px;cursor:pointer;
  font-family:'Nunito',sans-serif;font-size:1rem;font-weight:800;color:#fff;
  min-width:52px;transition:transform .15s}
.r-btn small{font-size:.58rem;font-weight:600;opacity:.85}
.r-btn:hover{transform:translateY(-3px)}
.r1{background:#ef4444}.r2{background:#f97316}
.r3{background:#eab308;color:#1a0f22}.r4{background:#84cc16;color:#1a0f22}
.r5{background:#22c55e}
.fc-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin:14px 0 18px}
.stat{background:var(--glass);backdrop-filter:blur(14px);border:1px solid var(--gborder);
  border-radius:14px;padding:12px 8px;text-align:center}
.stat .n{font-family:'Lekkerli One',cursive;font-size:1.7rem;line-height:1}
.n-g{color:var(--green)}.n-r{color:var(--red)}.n-y{color:var(--yellow)}.n-m{color:var(--muted)}
.stat .l{font-size:.65rem;color:var(--muted);font-weight:700;margin-top:3px}
.q-card{background:var(--glass);backdrop-filter:blur(18px);
  border:2px solid rgba(243,126,154,.28);border-radius:22px;
  padding:32px 26px;text-align:center;font-size:1.2rem;font-weight:700;
  min-height:100px;display:flex;align-items:center;justify-content:center;
  margin-bottom:18px;line-height:1.5;
  box-shadow:0 6px 22px rgba(75,22,76,.09),inset 0 1px 0 rgba(255,255,255,.6)}
.choices{display:flex;flex-direction:column;gap:9px;margin-bottom:12px}
.c-btn{background:var(--glass);backdrop-filter:blur(10px);
  border:1.5px solid rgba(75,22,76,.15);color:var(--text);
  border-radius:14px;padding:13px 18px;text-align:left;
  font-family:'Nunito',sans-serif;font-size:.93rem;font-weight:500;
  cursor:pointer;transition:all .18s;line-height:1.4}
.c-btn:hover:not(:disabled){border-color:var(--pink);background:rgba(243,126,154,.06)}
.c-btn.correct{background:var(--green-lt);border-color:var(--green);color:var(--green-dk);font-weight:700}
.c-btn.wrong{background:var(--red-lt);border-color:var(--red);color:var(--red-dk)}
.c-btn:disabled{cursor:default}
.fb{padding:11px 16px;border-radius:12px;font-weight:700;font-size:.88rem;margin-bottom:12px}
.fb-ok{background:var(--green-lt);color:var(--green-dk)}
.fb-bad{background:var(--red-lt);color:var(--red-dk)}
.id-input{width:100%;padding:13px 17px;border:1.5px solid rgba(75,22,76,.18);
  border-radius:14px;font-family:'Nunito',sans-serif;font-size:.98rem;
  background:var(--glass);backdrop-filter:blur(10px);
  color:var(--text);outline:none;margin-bottom:11px;transition:border-color .2s}
.id-input:focus{border-color:var(--pink)}
.id-input.ok{border-color:var(--green);background:var(--green-lt)}
.id-input.bad{border-color:var(--red);background:var(--red-lt)}
.actions{display:flex;align-items:center;gap:8px}
.btn{padding:9px 20px;border:none;border-radius:999px;
  font-family:'Nunito',sans-serif;font-weight:700;font-size:.85rem;
  cursor:pointer;transition:all .2s}
.btn-p{background:var(--purple);color:var(--cream)}
.btn-p:hover{background:var(--purple-dk,#370f37)}
.btn-s{background:var(--pink);color:#fff}
.btn-s:hover{filter:brightness(1.08)}
.btn-g{background:transparent;border:1.5px solid rgba(75,22,76,.2);color:var(--muted)}
.btn-g:hover{border-color:var(--purple);color:var(--purple)}
.ml{margin-left:auto}
.done-box{text-align:center;padding:44px 28px;background:var(--glass);
  backdrop-filter:blur(20px);border:2px solid rgba(243,126,154,.3);
  border-radius:24px;margin-top:18px;
  box-shadow:0 8px 32px rgba(75,22,76,.12)}
.done-box h2{font-family:'Lekkerli One',cursive;font-size:1.7rem;color:var(--purple);margin-bottom:8px}
.done-score{font-family:'Lekkerli One',cursive;font-size:3.8rem;color:var(--purple);
  line-height:1;margin:14px 0 6px}
.done-sub{color:var(--muted);font-size:.87rem;margin-bottom:22px}
</style>
"""


# ── Navigation bar ────────────────────────────────────────────────────────────
_EXPORT_NAV = """
<nav>
  <button class="active" onclick="setMode('fc',this)">📇 Flashcards</button>
  <button onclick="setMode('mc',this)">🔘 Multiple Choice</button>
  <button onclick="setMode('id',this)">✏️ Identification</button>
</nav>
<div class="sub-nav" id="sub-nav"></div>
"""


# ── App body ──────────────────────────────────────────────────────────────────
_EXPORT_BODY = """
<div id="app">

  <!-- Flashcards -->
  <div id="mode-fc">
    <div class="prog-track"><div class="prog-fill" id="fc-bar" style="width:0%"></div></div>
    <div class="prog-meta"><span id="fc-pos">Card — of —</span><span class="pct" id="fc-pct">0%</span></div>
    <div class="card-scene" onclick="flipCard()">
      <div class="card-3d" id="fc-card">
        <div class="card-face card-front">
          <span class="face-tag">term</span>
          <p class="face-text" id="fc-term">—</p>
          <span class="face-hint">tap to flip</span>
        </div>
        <div class="card-face card-back">
          <span class="face-tag" style="color:rgba(255,252,240,.45)">definition</span>
          <p class="face-text" id="fc-def">—</p>
        </div>
      </div>
    </div>
    <div id="r-strip" class="hidden">
      <span class="r-lbl">How well did you know this?</span>
      <div class="r-row">
        <button class="r-btn r1" onclick="rate(1)">1<small>Again</small></button>
        <button class="r-btn r2" onclick="rate(2)">2<small>Hard</small></button>
        <button class="r-btn r3" onclick="rate(3)">3<small>Okay</small></button>
        <button class="r-btn r4" onclick="rate(4)">4<small>Good</small></button>
        <button class="r-btn r5" onclick="rate(5)">5<small>Easy</small></button>
      </div>
    </div>
    <div class="fc-stats">
      <div class="stat"><div class="n n-g" id="fc-m">0</div><div class="l">Mastered</div></div>
      <div class="stat"><div class="n n-r" id="fc-s">0</div><div class="l">Struggling</div></div>
      <div class="stat"><div class="n n-y" id="fc-g">0</div><div class="l">Getting it</div></div>
      <div class="stat"><div class="n n-m" id="fc-r">0</div><div class="l">Remaining</div></div>
    </div>
    <div class="actions"><button class="btn btn-g" onclick="initFC()">↺ Restart</button></div>
  </div>

  <!-- Multiple Choice -->
  <div id="mode-mc" class="hidden">
    <div class="score-bar" id="mc-sb"></div>
    <div class="prog-track"><div class="prog-fill" id="mc-bar" style="width:0%"></div></div>
    <div class="prog-meta"><span id="mc-pos"></span><span class="pct" id="mc-pct">—</span></div>
    <div class="q-card" id="mc-q"></div>
    <div class="choices" id="mc-choices"></div>
    <div class="fb hidden" id="mc-fb"></div>
    <div class="actions">
      <button class="btn btn-g" onclick="initMC()">↺ Restart</button>
      <button class="btn btn-s ml hidden" id="mc-next" onclick="nextMC()">Next →</button>
    </div>
    <div class="done-box hidden" id="mc-done">
      <div style="font-size:2.2rem;margin-bottom:12px">🎉</div>
      <h2>Quiz Complete!</h2>
      <div class="done-score" id="mc-ds"></div>
      <p class="done-sub" id="mc-dp"></p>
      <button class="btn btn-p" onclick="initMC()">Try Again</button>
    </div>
  </div>

  <!-- Identification -->
  <div id="mode-id" class="hidden">
    <div class="score-bar" id="id-sb"></div>
    <div class="prog-track"><div class="prog-fill" id="id-bar" style="width:0%"></div></div>
    <div class="prog-meta"><span id="id-pos"></span><span class="pct" id="id-pct">—</span></div>
    <div class="q-card" id="id-q"></div>
    <input class="id-input" id="id-inp" placeholder="Type the definition…"/>
    <div class="fb hidden" id="id-fb"></div>
    <div class="actions">
      <button class="btn btn-g" onclick="initID()">↺ Restart</button>
      <button class="btn btn-p" id="id-sub" onclick="submitID()">Submit</button>
      <button class="btn btn-s ml hidden" id="id-nxt" onclick="nextID()">Next →</button>
    </div>
    <div class="done-box hidden" id="id-done">
      <div style="font-size:2.2rem;margin-bottom:12px">🎉</div>
      <h2>Round Complete!</h2>
      <div class="done-score" id="id-ds"></div>
      <p class="done-sub" id="id-dp"></p>
      <button class="btn btn-p" onclick="initID()">Try Again</button>
    </div>
  </div>

</div>
"""


# ── JavaScript ────────────────────────────────────────────────────────────────
_EXPORT_JS = r"""
// ── Helpers ──────────────────────────────────────────────────────────────────
function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function sample(a, n) { return shuffle([...a]).slice(0, n); }
function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Subject tabs ──────────────────────────────────────────────────────────────
let curSubj = 0;

function buildSubNav() {
  const el = document.getElementById('sub-nav');
  if (SUBJECTS.length <= 1) { el.style.display = 'none'; return; }
  el.innerHTML = SUBJECTS.map((s, i) =>
    `<button class="sub-btn${i === 0 ? ' active' : ''}" onclick="switchSubj(${i},this)">${esc(s.name)}</button>`
  ).join('');
}

function switchSubj(i, btn) {
  curSubj = i;
  document.querySelectorAll('.sub-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const activeMode = document.querySelector('nav button.active');
  const mode = activeMode ? (activeMode.textContent.includes('Flash') ? 'fc' :
               activeMode.textContent.includes('Choice') ? 'mc' : 'id') : 'fc';
  if (mode === 'fc') initFC();
  if (mode === 'mc') initMC();
  if (mode === 'id') initID();
}

function items() { return SUBJECTS[curSubj] ? SUBJECTS[curSubj].items : []; }

function setMode(m, btn) {
  ['fc','mc','id'].forEach(k =>
    document.getElementById('mode-' + k).classList.toggle('hidden', k !== m)
  );
  document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  if (m === 'fc') initFC();
  if (m === 'mc') initMC();
  if (m === 'id') initID();
}

// ── FLASHCARDS ────────────────────────────────────────────────────────────────
let fcDeck = [], fcIdx = 0, fcMastered = 0, fcStruggling = 0, fcGood = 0, fcFlipped = false;

function initFC() {
  fcDeck = shuffle(items().map(it => ({ term: it.term, def: it.def, r: 0 })));
  fcIdx = 0; fcMastered = 0; fcStruggling = 0; fcGood = 0; fcFlipped = false;
  renderFC();
}

function renderFC() {
  if (fcIdx >= fcDeck.length) {
    document.getElementById('fc-term').textContent = '🎉 All done!';
    document.getElementById('fc-def').textContent  = 'Great work!';
    document.getElementById('fc-pos').textContent  = 'Complete';
    document.getElementById('fc-pct').textContent  = '100%';
    document.getElementById('fc-bar').style.width  = '100%';
    document.getElementById('r-strip').classList.add('hidden');
    updFCStats(); return;
  }
  const c = fcDeck[fcIdx];
  document.getElementById('fc-term').textContent = c.term;
  document.getElementById('fc-def').textContent  = c.def;
  document.getElementById('fc-pos').textContent  = `Card ${fcIdx + 1} of ${fcDeck.length}`;
  const pct = Math.round(fcMastered / fcDeck.length * 100);
  document.getElementById('fc-pct').textContent = pct + '% mastered';
  document.getElementById('fc-bar').style.width = pct + '%';
  fcFlipped = false;
  document.getElementById('fc-card').classList.remove('flipped');
  document.getElementById('r-strip').classList.add('hidden');
  updFCStats();
}

function updFCStats() {
  document.getElementById('fc-m').textContent = fcMastered;
  document.getElementById('fc-s').textContent = fcStruggling;
  document.getElementById('fc-g').textContent = fcGood;
  document.getElementById('fc-r').textContent = Math.max(0, fcDeck.length - fcIdx);
}

function flipCard() {
  if (fcIdx >= fcDeck.length) return;
  fcFlipped = !fcFlipped;
  document.getElementById('fc-card').classList.toggle('flipped', fcFlipped);
  document.getElementById('r-strip').classList.toggle('hidden', !fcFlipped);
}

function rate(r) {
  if (!fcFlipped) return;
  const c = fcDeck.splice(fcIdx, 1)[0];
  c.r = r;
  if (r <= 2) {
    fcStruggling++;
    fcDeck.splice(Math.min(fcIdx + (r === 1 ? 3 : 5), fcDeck.length), 0, c);
  } else if (r <= 4) {
    fcGood++;
    fcDeck.splice(Math.max(fcIdx, Math.floor((fcIdx + fcDeck.length) / 2)), 0, c);
  } else {
    fcMastered++;
    fcDeck.push(c);
  }
  renderFC();
}

// ── MULTIPLE CHOICE ───────────────────────────────────────────────────────────
let mcTotal = 0, mcCorrect = 0, mcQ = 0, mcCur = null, mcAnswered = false;

function initMC() {
  mcTotal = 0; mcCorrect = 0; mcQ = 0; mcAnswered = false;
  document.getElementById('mc-done').classList.add('hidden');
  renderMCScore(); loadMC();
}

function loadMC() {
  if (mcQ >= ROUNDS) { showMCDone(); return; }
  const its = items();
  if (its.length < 4) { document.getElementById('mc-q').textContent = 'Need at least 4 items.'; return; }
  const item    = its[Math.floor(Math.random() * its.length)];
  const correct = item.def;
  const others  = sample(its.filter(x => x.def !== correct).map(x => x.def), 3);
  const choices = shuffle([...others, correct]);
  mcCur = { term: item.term, correct };
  mcAnswered = false;
  document.getElementById('mc-q').textContent = item.term;
  document.getElementById('mc-fb').classList.add('hidden');
  document.getElementById('mc-next').classList.add('hidden');
  document.getElementById('mc-pos').textContent = `Question ${mcQ + 1} of ${ROUNDS}`;
  const ch = document.getElementById('mc-choices');
  ch.innerHTML = '';
  choices.forEach(c => {
    const b = document.createElement('button');
    b.className = 'c-btn';
    b.textContent = c;
    b.onclick = () => answerMC(b, c, correct);
    ch.appendChild(b);
  });
  renderMCScore();
}

function answerMC(btn, chosen, correct) {
  if (mcAnswered) return;
  mcAnswered = true;
  const ok = chosen.trim().toLowerCase() === correct.trim().toLowerCase();
  if (ok) mcCorrect++;
  mcTotal++; mcQ++;
  document.querySelectorAll('.c-btn').forEach(b => {
    b.disabled = true;
    if (b.textContent.trim().toLowerCase() === correct.trim().toLowerCase()) b.classList.add('correct');
    else if (b === btn && !ok) b.classList.add('wrong');
  });
  const fb = document.getElementById('mc-fb');
  fb.textContent = ok ? '✅ Correct!' : `❌ Wrong! Answer: ${correct}`;
  fb.className = 'fb ' + (ok ? 'fb-ok' : 'fb-bad');
  fb.classList.remove('hidden');
  document.getElementById('mc-next').classList.remove('hidden');
  renderMCScore();
}

function nextMC() { loadMC(); }

function showMCDone() {
  const pct = mcTotal ? Math.round(mcCorrect / mcTotal * 100) : 0;
  document.getElementById('mc-ds').textContent = pct + '%';
  document.getElementById('mc-dp').textContent = `${mcCorrect} correct out of ${mcTotal}`;
  document.getElementById('mc-done').classList.remove('hidden');
  renderMCScore();
}

function renderMCScore() {
  const pct = mcTotal ? Math.round(mcCorrect / mcTotal * 100) : 0;
  document.getElementById('mc-sb').innerHTML =
    `<span class="s-pill sp-t">📋 ${mcTotal}</span>` +
    `<span class="s-pill sp-c">✅ ${mcCorrect}</span>` +
    `<span class="s-pill sp-w">❌ ${mcTotal - mcCorrect}</span>` +
    `<span class="s-pill sp-p">🎯 ${mcTotal ? pct + '%' : '—'}</span>`;
  document.getElementById('mc-bar').style.width = Math.min(mcQ / ROUNDS * 100, 100) + '%';
  document.getElementById('mc-pct').textContent = mcTotal ? pct + '%' : '—';
}

// ── IDENTIFICATION ────────────────────────────────────────────────────────────
let idTotal = 0, idCorrect = 0, idQ = 0, idCur = null, idAnswered = false;

function initID() {
  idTotal = 0; idCorrect = 0; idQ = 0; idAnswered = false;
  document.getElementById('id-done').classList.add('hidden');
  renderIDScore(); loadID();
}

function loadID() {
  if (idQ >= ROUNDS) { showIDDone(); return; }
  const its  = items();
  const item = its[Math.floor(Math.random() * its.length)];
  idCur = item.def; idAnswered = false;
  document.getElementById('id-q').textContent = item.term;
  document.getElementById('id-pos').textContent = `Question ${idQ + 1} of ${ROUNDS}`;
  const inp = document.getElementById('id-inp');
  inp.value = ''; inp.className = 'id-input'; inp.disabled = false; inp.focus();
  document.getElementById('id-fb').classList.add('hidden');
  document.getElementById('id-sub').classList.remove('hidden');
  document.getElementById('id-nxt').classList.add('hidden');
  renderIDScore();
}

function submitID() {
  if (idAnswered || !idCur) return;
  const inp = document.getElementById('id-inp');
  const ok  = inp.value.trim().toLowerCase() === idCur.trim().toLowerCase();
  if (ok) idCorrect++;
  idTotal++; idQ++; idAnswered = true;
  inp.disabled = true;
  inp.className = 'id-input ' + (ok ? 'ok' : 'bad');
  const fb = document.getElementById('id-fb');
  fb.textContent = ok ? '✅ Correct!' : `❌ Wrong! Answer: ${idCur}`;
  fb.className = 'fb ' + (ok ? 'fb-ok' : 'fb-bad');
  fb.classList.remove('hidden');
  document.getElementById('id-sub').classList.add('hidden');
  document.getElementById('id-nxt').classList.remove('hidden');
  renderIDScore();
}

function nextID() { loadID(); }

function showIDDone() {
  const pct = idTotal ? Math.round(idCorrect / idTotal * 100) : 0;
  document.getElementById('id-ds').textContent = pct + '%';
  document.getElementById('id-dp').textContent = `${idCorrect} correct out of ${idTotal}`;
  document.getElementById('id-done').classList.remove('hidden');
  renderIDScore();
}

function renderIDScore() {
  const pct = idTotal ? Math.round(idCorrect / idTotal * 100) : 0;
  document.getElementById('id-sb').innerHTML =
    `<span class="s-pill sp-t">📋 ${idTotal}</span>` +
    `<span class="s-pill sp-c">✅ ${idCorrect}</span>` +
    `<span class="s-pill sp-w">❌ ${idTotal - idCorrect}</span>` +
    `<span class="s-pill sp-p">🎯 ${idTotal ? pct + '%' : '—'}</span>`;
  document.getElementById('id-bar').style.width = Math.min(idQ / ROUNDS * 100, 100) + '%';
  document.getElementById('id-pct').textContent = idTotal ? pct + '%' : '—';
}

// Enter key for ID
document.getElementById('id-inp').addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  if (!document.getElementById('id-nxt').classList.contains('hidden')) nextID();
  else submitID();
});

// ── Boot ──────────────────────────────────────────────────────────────────────
buildSubNav();
setMode('fc', document.querySelector('nav button'));
"""