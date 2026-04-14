/* ── State ───────────────────────────────────────────────────────────── */
let currentSid   = null;
let currentMode  = 'fc';
let fcFlipped    = false;

// MC state
let mcTotal = 0, mcCorrect = 0, mcCurrent = null, mcAnswered = false, mcQuestionCount = 0;
// ID state
let idTotal = 0, idCorrect = 0, idCurrent = null, idAnswered = false, idQuestionCount = 0;

const QUESTIONS_PER_ROUND = 10;




/* ── Boot ────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  loadSubjects();
});

/* ── Subject List ─────────────────────────────────────────────────────── */
async function loadSubjects() {
  const res  = await fetch('/api/subjects');
  const list = await res.json();
  renderSubjects(list);
}

function renderSubjects(list) {
  const grid  = document.getElementById('subjects-grid');
  const empty = document.getElementById('empty-state');
  const count = document.getElementById('subject-count');

  count.textContent = list.length + ' subject' + (list.length !== 1 ? 's' : '');
  empty.classList.toggle('hidden', list.length > 0);
  grid.innerHTML = '';

  list.forEach((s, i) => {
    const card = document.createElement('div');
    card.className = 'subject-card';
    card.style.animationDelay = (i * 60) + 'ms';
    card.innerHTML = `
      <div class="card-top">
        <h3 class="subject-name">${esc(s.name)}</h3>
        <button class="delete-btn" title="Delete" onclick="deleteSubject('${s.id}',event)">✕</button>
      </div>
      <div class="subject-meta">
        <span class="meta-pill">${s.count} items</span>
      </div>
      <div class="study-modes-row">
        <button class="mode-chip" onclick="openStudy('${s.id}','fc',event)">📇 Flashcards</button>
        <button class="mode-chip" onclick="openStudy('${s.id}','mc',event)">🔘 MC</button>
        <button class="mode-chip" onclick="openStudy('${s.id}','id',event)">✏️ Identify</button>
      </div>
    `;
    // Clicking the card body (not buttons) opens flashcards
    card.addEventListener('click', () => openStudy(s.id, 'fc'));
    grid.appendChild(card);
  });
}

async function deleteSubject(sid, e) {
  e.stopPropagation();
  if (!confirm('Delete this subject?')) return;
  await fetch('/api/subjects/' + sid, { method: 'DELETE' });
  loadSubjects();
}

/* ── Import Modal ─────────────────────────────────────────────────────── */
function openImport() {
  document.getElementById('import-overlay').classList.remove('hidden');
  document.getElementById('import-name').focus();
}

function closeImport(e) {
  if (e && e.target !== document.getElementById('import-overlay')) return;
  document.getElementById('import-overlay').classList.add('hidden');
  document.getElementById('import-error').classList.add('hidden');
  document.getElementById('import-name').value = '';
  document.getElementById('import-raw').value  = '';
}

async function doImport() {
  const name = document.getElementById('import-name').value.trim();
  const raw  = document.getElementById('import-raw').value.trim();
  const errEl = document.getElementById('import-error');

  if (!name) { showImportErr('Please enter a subject name.'); return; }
  if (!raw)  { showImportErr('Please paste your notes.'); return; }

  const res  = await fetch('/api/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, raw }),
  });
  const data = await res.json();

  if (!res.ok) { showImportErr(data.error); return; }

  errEl.classList.add('hidden');
  closeImport();
  await loadSubjects();

  if (data.errors && data.errors.length) {
    console.warn('Skipped lines:', data.errors);
  }
}

function showImportErr(msg) {
  const el = document.getElementById('import-error');
  el.textContent = '⚠️ ' + msg;
  el.classList.remove('hidden');
}

// Close modal on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeImport();
});

/* ── Study View ───────────────────────────────────────────────────────── */
async function openStudy(sid, mode = 'fc', e) {
  if (e) e.stopPropagation();
  currentSid = sid;

  // Get subject name
  const res  = await fetch('/api/subjects');
  const list = await res.json();
  const subj = list.find(s => s.id === sid);
  if (!subj) return;

  document.getElementById('study-title').textContent = subj.name;
  document.getElementById('dashboard').classList.add('hidden');
  document.getElementById('study-view').classList.remove('hidden');
  window.scrollTo(0,0);

  setMode(mode, document.querySelector(`.mode-tab[data-mode="${mode}"]`));
}

function goBack() {
  document.getElementById('study-view').classList.add('hidden');
  document.getElementById('dashboard').classList.remove('hidden');
  currentSid = null;
}

function setMode(mode, tabEl) {
  currentMode = mode;
  document.querySelectorAll('.study-panel').forEach(p => p.classList.add('hidden'));
  document.getElementById('panel-' + mode).classList.remove('hidden');
  document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
  if (tabEl) tabEl.classList.add('active');

  if (mode === 'fc') initFC();
  if (mode === 'mc') initMC();
  if (mode === 'id') initID();
}

/* ── Export ───────────────────────────────────────────────────────────── */
function exportSubject() {
  if (!currentSid) return;
  window.location.href = '/api/' + currentSid + '/export';
}

/* ════════════════════════════════════════════════════════════════════════
   FLASHCARDS
   ════════════════════════════════════════════════════════════════════════ */
async function initFC() {
  fcFlipped = false;
  const data = await fetchFC();
  renderFC(data);
}

async function fetchFC() {
  const res = await fetch('/api/' + currentSid + '/fc/current');
  return res.json();
}

function renderFC(d) {
  if (d.done) {
    document.getElementById('fc-term').textContent = '🎉 Session complete!';
    document.getElementById('fc-def').textContent  = 'All cards reviewed.';
    document.getElementById('fc-position').textContent = 'Done!';
    document.getElementById('fc-pct').textContent = '100% mastered';
    document.getElementById('fc-bar').style.width = '100%';
    document.getElementById('rating-strip').classList.add('hidden');
    document.getElementById('fc-mastered').textContent   = d.mastered;
    document.getElementById('fc-struggling').textContent = '0';
    document.getElementById('fc-good').textContent       = '0';
    document.getElementById('fc-remaining').textContent  = '0';
    return;
  }
  document.getElementById('fc-term').textContent        = d.term;
  document.getElementById('fc-def').textContent         = d.def;
  document.getElementById('fc-position').textContent    = `Card ${d.position} of ${d.remaining}`;
  document.getElementById('fc-pct').textContent         = `${d.pct}% mastered`;
  document.getElementById('fc-bar').style.width         = d.pct + '%';
  document.getElementById('fc-mastered').textContent    = d.mastered;
  document.getElementById('fc-struggling').textContent  = d.struggling;
  document.getElementById('fc-good').textContent        = d.good;
  document.getElementById('fc-remaining').textContent   = d.remaining;

  // Reset card state
  fcFlipped = false;
  document.getElementById('fc-card').classList.remove('flipped');
  document.getElementById('rating-strip').classList.add('hidden');
}

function flipCard() {
  if (!currentSid) return;
  fcFlipped = !fcFlipped;
  document.getElementById('fc-card').classList.toggle('flipped', fcFlipped);
  document.getElementById('rating-strip').classList.toggle('hidden', !fcFlipped);
}

async function rateCard(rating) {
  if (!fcFlipped) return;
  const res  = await fetch('/api/' + currentSid + '/fc/rate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating }),
  });
  const data = await res.json();
  renderFC(data);
}

async function fcReset() {
  const res  = await fetch('/api/' + currentSid + '/fc/reset', { method: 'POST' });
  const data = await res.json();
  renderFC(data);
}

/* ════════════════════════════════════════════════════════════════════════
   MULTIPLE CHOICE
   ════════════════════════════════════════════════════════════════════════ */
async function initMC() {
  mcTotal = 0; mcCorrect = 0; mcQuestionCount = 0; mcAnswered = false;
  document.getElementById('mc-done').classList.add('hidden');
  await fetch('/api/' + currentSid + '/mc/reset', { method: 'POST' });
  await loadMCQuestion();
}

async function loadMCQuestion() {
  if (mcQuestionCount >= QUESTIONS_PER_ROUND) { showMCDone(); return; }

  const res  = await fetch('/api/' + currentSid + '/mc/question');
  const data = await res.json();
  if (data.error) return;

  mcCurrent  = data;
  mcAnswered = false;

  document.getElementById('mc-question').textContent = data.term;
  document.getElementById('mc-feedback').classList.add('hidden');
  document.getElementById('mc-next-btn').classList.add('hidden');

  const list = document.getElementById('mc-choices');
  list.innerHTML = '';
  data.choices.forEach(c => {
    const btn = document.createElement('button');
    btn.className   = 'choice-btn';
    btn.textContent = c;
    btn.onclick = () => answerMC(btn, c, data.correct);
    list.appendChild(btn);
  });

  renderMCScore();
}

async function answerMC(btn, chosen, correct) {
  if (mcAnswered) return;
  mcAnswered = true;

  const res  = await fetch('/api/' + currentSid + '/mc/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chosen, correct }),
  });
  const data = await res.json();
  const successSound = new Audio('/static/sound/correct.mp3');

  if(data.correct) {
    successSound.currentTime=0; successSound.play().catch(()=>{});
    }
  mcTotal   = data.mc_total;
  mcCorrect = data.mc_correct;
  mcQuestionCount++;

  document.querySelectorAll('.choice-btn').forEach(b => {
    b.disabled = true;
    if (b.textContent.toLowerCase() === correct.toLowerCase()) b.classList.add('correct');
    else if (b === btn && !data.correct) b.classList.add('wrong');
  });

  const fb = document.getElementById('mc-feedback');
  fb.textContent  = data.correct ? '✅ Correct!' : '❌ Wrong! Answer: ' + correct;
  fb.className    = 'feedback-box ' + (data.correct ? 'ok' : 'bad');
  fb.classList.remove('hidden');
  document.getElementById('mc-next-btn').classList.remove('hidden');
  renderMCScore();
}

function mcNext() { loadMCQuestion(); }

async function mcReset() {
  document.getElementById('mc-done').classList.add('hidden');
  await initMC();
}

function showMCDone() {
  const pct = mcTotal ? Math.round(mcCorrect / mcTotal * 100) : 0;
  document.getElementById('mc-done-score').textContent = pct + '%';
  document.getElementById('mc-done-sub').textContent   = mcCorrect + ' correct out of ' + mcTotal + ' questions';
  document.getElementById('mc-done').classList.remove('hidden');
  renderMCScore();
}

function renderMCScore() {
  const pct   = mcTotal ? Math.round(mcCorrect / mcTotal * 100) : 0;
  const wrong = mcTotal - mcCorrect;
  document.getElementById('mc-score-bar').innerHTML = `
    <span class="score-pill sp-total">📋 ${mcTotal} Qs</span>
    <span class="score-pill sp-correct">✅ ${mcCorrect}</span>
    <span class="score-pill sp-wrong">❌ ${wrong}</span>
    <span class="score-pill sp-pct">🎯 ${mcTotal ? pct + '%' : '—'}</span>
  `;
  const prog = Math.min(mcQuestionCount / QUESTIONS_PER_ROUND * 100, 100);
  document.getElementById('mc-bar').style.width = prog + '%';
}

/* ════════════════════════════════════════════════════════════════════════
   IDENTIFICATION
   ════════════════════════════════════════════════════════════════════════ */
async function initID() {
  idTotal = 0; idCorrect = 0; idQuestionCount = 0; idAnswered = false;
  document.getElementById('id-done').classList.add('hidden');
  await fetch('/api/' + currentSid + '/id/reset', { method: 'POST' });
  await loadIDQuestion();
}

async function loadIDQuestion() {
  if (idQuestionCount >= QUESTIONS_PER_ROUND) { showIDDone(); return; }

  const res  = await fetch('/api/' + currentSid + '/id/question');
  const data = await res.json();
  if (data.error) return;

  idCurrent  = data.correct;
  idAnswered = false;

  document.getElementById('id-question').textContent = data.term;

  const inp = document.getElementById('id-input');
  inp.value    = '';
  inp.className = 'answer-input';
  inp.disabled  = false;
  inp.focus();

  document.getElementById('id-feedback').classList.add('hidden');
  document.getElementById('id-submit-btn').classList.remove('hidden');
  document.getElementById('id-next-btn').classList.add('hidden');
  renderIDScore();
}

async function submitID() {
  if (idAnswered || !idCurrent) return;
  const inp   = document.getElementById('id-input');
  const given = inp.value;
  const successSound = new Audio('/static/sound/correct.mp3');


  const res  = await fetch('/api/' + currentSid + '/id/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ given, correct: idCurrent }),
  });
  const data = await res.json();

  if(data.correct) {
    successSound.currentTime=0; successSound.play().catch(()=>{});
  }

  idTotal    = data.id_total;
  idCorrect  = data.id_correct;
  idAnswered = true;
  idQuestionCount++;

  inp.disabled  = true;
  inp.className = 'answer-input ' + (data.correct ? 'ok' : 'bad');

  const fb = document.getElementById('id-feedback');
  fb.textContent  = data.correct ? '✅ Correct!' : '❌ Wrong! Answer: ' + idCurrent;
  fb.className    = 'feedback-box ' + (data.correct ? 'ok' : 'bad');
  fb.classList.remove('hidden');

  document.getElementById('id-submit-btn').classList.add('hidden');
  document.getElementById('id-next-btn').classList.remove('hidden');
  renderIDScore();
}

function idNext() { loadIDQuestion(); }

async function idReset() {
  document.getElementById('id-done').classList.add('hidden');
  await initID();
}

function showIDDone() {
  const pct = idTotal ? Math.round(idCorrect / idTotal * 100) : 0;
  document.getElementById('id-done-score').textContent = pct + '%';
  document.getElementById('id-done-sub').textContent   = idCorrect + ' correct out of ' + idTotal + ' questions';
  document.getElementById('id-done').classList.remove('hidden');
  renderIDScore();
}

function renderIDScore() {
  const pct   = idTotal ? Math.round(idCorrect / idTotal * 100) : 0;
  const wrong = idTotal - idCorrect;
  document.getElementById('id-score-bar').innerHTML = `
    <span class="score-pill sp-total">📋 ${idTotal} Qs</span>
    <span class="score-pill sp-correct">✅ ${idCorrect}</span>
    <span class="score-pill sp-wrong">❌ ${wrong}</span>
    <span class="score-pill sp-pct">🎯 ${idTotal ? pct + '%' : '—'}</span>
  `;
  const prog = Math.min(idQuestionCount / QUESTIONS_PER_ROUND * 100, 100);
  document.getElementById('id-bar').style.width = prog + '%';
}

// Enter key support for ID
document.addEventListener('keydown', e => {
  if (document.getElementById('panel-id').classList.contains('hidden')) return;
  if (e.key !== 'Enter') return;
  if (!document.getElementById('id-next-btn').classList.contains('hidden')) idNext();
  else if (!document.getElementById('id-submit-btn').classList.contains('hidden')) submitID();
});

/* ── Util ─────────────────────────────────────────────────────────────── */
function esc(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}