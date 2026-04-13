import json

def generate_html_string(subject_name, data):
    json_data = json.dumps(data, ensure_ascii=False)
    safe_name = subject_name.replace('"', "'")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Halo-Halo — {safe_name}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
:root{{--ube:#633971;--ube-dk:#4a2856;--mango:#FFC300;--milk:#FFFDD0;--white:#fff;--text:#1a0f22;--muted:#7a5a8a;--green:#22c55e;--red:#ef4444;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--milk);font-family:'DM Sans',sans-serif;color:var(--text);min-height:100vh}}
header{{background:var(--ube);color:var(--milk);padding:20px 32px;display:flex;align-items:center;justify-content:space-between}}
header h1{{font-family:'Playfair Display',serif;font-size:1.6rem}}
nav{{display:flex;gap:8px;justify-content:center;padding:16px;background:var(--ube-dk)}}
nav button{{background:transparent;border:2px solid var(--mango);color:var(--mango);padding:8px 24px;border-radius:999px;cursor:pointer;font-family:'DM Sans',sans-serif;font-size:.9rem;font-weight:600;transition:all .2s}}
nav button.active,nav button:hover{{background:var(--mango);color:var(--text)}}
#app{{max-width:700px;margin:36px auto;padding:0 20px 80px}}
.hidden{{display:none!important}}
.progress-wrap{{background:rgba(99,57,113,.15);border-radius:8px;height:8px;margin-bottom:16px;overflow:hidden}}
.progress-bar{{height:100%;background:linear-gradient(90deg,var(--ube),var(--mango));border-radius:8px;transition:width .5s ease}}
.score-row{{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}}
.badge{{padding:5px 14px;border-radius:999px;font-size:.8rem;font-weight:600}}
.b-total{{background:var(--ube);color:var(--milk)}}
.b-correct{{background:#dcfce7;color:#166534}}
.b-wrong{{background:#fee2e2;color:#991b1b}}
.b-pct{{background:var(--mango);color:var(--text)}}
.card-wrap{{perspective:1000px;height:240px;margin:12px 0 20px;cursor:pointer}}
.card{{width:100%;height:100%;position:relative;transform-style:preserve-3d;transition:transform .6s cubic-bezier(.4,0,.2,1)}}
.card.flipped{{transform:rotateY(180deg)}}
.card-face{{position:absolute;width:100%;height:100%;backface-visibility:hidden;border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:32px;text-align:center;box-shadow:0 8px 32px rgba(99,57,113,.15)}}
.card-front{{background:var(--white);border:3px solid var(--mango)}}
.card-back{{background:var(--ube);color:var(--milk);border:3px solid var(--mango);transform:rotateY(180deg)}}
.card-tag{{font-size:.7rem;letter-spacing:3px;text-transform:uppercase;opacity:.5;margin-bottom:12px}}
.card-text{{font-family:'Playfair Display',serif;font-size:1.4rem;line-height:1.5}}
.card-hint{{font-size:.8rem;opacity:.4;margin-top:16px}}
.rating-row{{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:16px}}
.r-btn{{padding:9px 18px;border:none;border-radius:12px;cursor:pointer;font-weight:700;font-family:'DM Sans',sans-serif;font-size:.85rem;color:#fff;transition:transform .1s,opacity .15s}}
.r-btn:hover{{transform:translateY(-3px)}}
.fc-stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}}
.fc-stat{{background:var(--white);border:2px solid var(--mango);border-radius:16px;padding:16px;text-align:center}}
.fc-stat .num{{font-family:'Playfair Display',serif;font-size:2rem;color:var(--ube)}}
.fc-stat .lbl{{font-size:.75rem;color:var(--muted);margin-top:4px}}
.q-box{{background:var(--white);border:3px solid var(--mango);border-radius:20px;padding:32px;text-align:center;font-family:'Playfair Display',serif;font-size:1.3rem;min-height:100px;display:flex;align-items:center;justify-content:center;margin-bottom:20px;box-shadow:0 4px 20px rgba(99,57,113,.1)}}
.choices{{display:flex;flex-direction:column;gap:10px}}
.c-btn{{background:var(--white);border:2px solid var(--ube);color:var(--text);padding:14px 20px;border-radius:14px;cursor:pointer;font-family:'DM Sans',sans-serif;font-size:1rem;text-align:left;transition:all .18s}}
.c-btn:hover:not(:disabled){{background:var(--milk);border-color:var(--mango)}}
.c-btn.correct{{background:#dcfce7;border-color:var(--green);color:#166534;font-weight:600}}
.c-btn.wrong{{background:#fee2e2;border-color:var(--red);color:#991b1b}}
.c-btn:disabled{{cursor:default}}
.fb{{text-align:center;padding:10px 16px;border-radius:12px;font-weight:600;margin:12px 0;display:none}}
.fb.ok{{background:#dcfce7;color:#166534;display:block}}
.fb.bad{{background:#fee2e2;color:#991b1b;display:block}}
.id-input{{width:100%;padding:14px 18px;border:2px solid var(--ube);border-radius:14px;font-family:'DM Sans',sans-serif;font-size:1rem;margin-bottom:12px;outline:none;transition:border-color .2s;background:var(--white)}}
.id-input:focus{{border-color:var(--mango)}}
.id-input.ok{{border-color:var(--green);background:#dcfce7}}
.id-input.bad{{border-color:var(--red);background:#fee2e2}}
.btn{{padding:11px 28px;border:none;border-radius:12px;cursor:pointer;font-family:'DM Sans',sans-serif;font-weight:600;font-size:.95rem;transition:all .18s}}
.btn-p{{background:var(--ube);color:var(--milk)}}
.btn-p:hover{{background:var(--ube-dk)}}
.btn-s{{background:var(--mango);color:var(--text)}}
.btn-s:hover{{background:#e6a800}}
.done-box{{background:var(--white);border:3px solid var(--mango);border-radius:24px;padding:48px;text-align:center;box-shadow:0 8px 32px rgba(99,57,113,.15)}}
.done-box h2{{font-family:'Playfair Display',serif;color:var(--ube);font-size:2rem;margin-bottom:8px}}
.done-big{{font-family:'Playfair Display',serif;font-size:4rem;color:var(--ube);margin:12px 0}}
</style>
</head>
<body>
<header>
  <h1>🍧 Halo-Halo</h1>
  <span style="font-size:.9rem;opacity:.7">{safe_name}</span>
</header>
<nav>
  <button class="active" onclick="setMode('fc')">📇 Flashcards</button>
  <button onclick="setMode('mc')">🔘 Multiple Choice</button>
  <button onclick="setMode('id')">✏️ Identification</button>
</nav>
<div id="app">
  <div id="mode-fc">
    <div style="font-size:.85rem;color:var(--muted);margin-bottom:6px" id="fc-meta"></div>
    <div class="progress-wrap"><div class="progress-bar" id="fc-bar" style="width:0%"></div></div>
    <div class="card-wrap" onclick="flipCard()">
      <div class="card" id="fc-card">
        <div class="card-face card-front"><div class="card-tag">term</div><div class="card-text" id="fc-term"></div><div class="card-hint">click to flip</div></div>
        <div class="card-face card-back"><div class="card-tag" style="color:rgba(255,253,208,.5)">definition</div><div class="card-text" id="fc-def"></div></div>
      </div>
    </div>
    <div class="rating-row hidden" id="fc-ratings">
      <button class="r-btn" style="background:#ef4444" onclick="rate(1)">1 · Again</button>
      <button class="r-btn" style="background:#f97316" onclick="rate(2)">2 · Hard</button>
      <button class="r-btn" style="background:#eab308;color:#1a0f22" onclick="rate(3)">3 · Okay</button>
      <button class="r-btn" style="background:#84cc16;color:#1a0f22" onclick="rate(4)">4 · Good</button>
      <button class="r-btn" style="background:#22c55e" onclick="rate(5)">5 · Easy</button>
    </div>
    <div class="fc-stats">
      <div class="fc-stat"><div class="num" id="fc-mastered">0</div><div class="lbl">✅ Mastered</div></div>
      <div class="fc-stat"><div class="num" id="fc-struggling">0</div><div class="lbl">🔴 Struggling</div></div>
      <div class="fc-stat"><div class="num" id="fc-remaining">0</div><div class="lbl">📋 Remaining</div></div>
    </div>
  </div>
  <div id="mode-mc" class="hidden">
    <div class="score-row" id="mc-scores"></div>
    <div class="progress-wrap"><div class="progress-bar" id="mc-bar" style="width:0%"></div></div>
    <div class="q-box" id="mc-q"></div>
    <div class="choices" id="mc-choices"></div>
    <div class="fb" id="mc-fb"></div>
    <div style="text-align:right;margin-top:12px"><button class="btn btn-s hidden" id="mc-next" onclick="nextMC()">Next →</button></div>
    <div class="done-box hidden" id="mc-done"><h2>Quiz Complete 🎉</h2><div class="done-big" id="mc-dscore"></div><p id="mc-dsub" style="color:var(--muted);margin-bottom:24px"></p><button class="btn btn-p" onclick="resetMC()">Try Again</button></div>
  </div>
  <div id="mode-id" class="hidden">
    <div class="score-row" id="id-scores"></div>
    <div class="progress-wrap"><div class="progress-bar" id="id-bar" style="width:0%"></div></div>
    <div class="q-box" id="id-q"></div>
    <input class="id-input" id="id-inp" placeholder="Type the definition…"/>
    <div class="fb" id="id-fb"></div>
    <div style="display:flex;gap:10px">
      <button class="btn btn-p" id="id-sub" onclick="submitID()">Submit</button>
      <button class="btn btn-s hidden" id="id-next" onclick="nextID()">Next →</button>
    </div>
    <div class="done-box hidden" id="id-done"><h2>Round Complete 🎉</h2><div class="done-big" id="id-dscore"></div><p id="id-dsub" style="color:var(--muted);margin-bottom:24px"></p><button class="btn btn-p" onclick="resetID()">Try Again</button></div>
  </div>
</div>
<script>
const D={json_data};
let fcFlipped=false,mcTotal=0,mcCorrect=0,mcCurrent=null,mcAnswered=false;
let idTotal=0,idCorrect=0,idCurrent=null,idAnswered=false;
function shuffle(a){{for(let i=a.length-1;i>0;i--){{const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}}return a}}
function sample(a,n){{return shuffle([...a]).slice(0,n)}}
function setMode(m){{['fc','mc','id'].forEach(k=>document.getElementById('mode-'+k).classList.toggle('hidden',k!==m));document.querySelectorAll('nav button').forEach((b,i)=>b.classList.toggle('active',['fc','mc','id'][i]===m));if(m==='fc')initFC();if(m==='mc')initMC();if(m==='id')initID()}}
let fcDeck,fcIdx,fcMastered=0,fcStruggling=0;
function initFC(){{fcDeck=shuffle([...D]);fcIdx=0;fcMastered=0;fcStruggling=0;renderFC()}}
function renderFC(){{if(fcIdx>=fcDeck.length){{document.getElementById('fc-term').textContent='🎉 All done!';document.getElementById('fc-def').textContent='Great job!';document.getElementById('fc-meta').textContent='Session complete';document.getElementById('fc-bar').style.width='100%';document.getElementById('fc-ratings').classList.add('hidden');updateFCStats(fcDeck.length,0);return}}const c=fcDeck[fcIdx];document.getElementById('fc-term').textContent=c.term;document.getElementById('fc-def').textContent=c['def'];document.getElementById('fc-meta').textContent='Card '+(fcIdx+1)+' of '+fcDeck.length;document.getElementById('fc-bar').style.width=Math.round(fcIdx/D.length*100)+'%';document.getElementById('fc-card').classList.remove('flipped');document.getElementById('fc-ratings').classList.add('hidden');fcFlipped=false;updateFCStats(fcMastered,fcStruggling,fcDeck.length-fcIdx)}}
function flipCard(){{if(fcIdx>=fcDeck.length)return;fcFlipped=!fcFlipped;document.getElementById('fc-card').classList.toggle('flipped',fcFlipped);document.getElementById('fc-ratings').classList.toggle('hidden',!fcFlipped)}}
function rate(r){{if(!fcFlipped)return;const c=fcDeck.splice(fcIdx,1)[0];if(r<=2){{fcStruggling++;fcDeck.splice(Math.min(fcIdx+3,fcDeck.length),0,c)}}else if(r<=4){{fcDeck.splice(Math.max(fcIdx,Math.floor((fcIdx+fcDeck.length)/2)),0,c)}}else{{fcMastered++;fcDeck.push(c)}}renderFC()}}
function updateFCStats(m,s,rem){{document.getElementById('fc-mastered').textContent=m||0;document.getElementById('fc-struggling').textContent=s||0;document.getElementById('fc-remaining').textContent=rem!==undefined?rem:0}}
function scoreBadges(total,correct,pct,tid,cid,wid,pid){{const wrong=total-correct;document.getElementById(tid).innerHTML='<span class="badge b-total">📋 '+total+' Qs</span><span class="badge b-correct">✅ '+correct+'</span><span class="badge b-wrong">❌ '+wrong+'</span><span class="badge b-pct">🎯 '+(total?pct+'%':'—')+'</span>'}}
function initMC(){{mcTotal=0;mcCorrect=0;document.getElementById('mc-done').classList.add('hidden');loadMC()}}
function loadMC(){{const item=D[Math.floor(Math.random()*D.length)];const correct=item['def'];const distractors=sample(D.filter(x=>x['def'].toLowerCase()!==correct.toLowerCase()).map(x=>x['def']),3);const choices=shuffle([...distractors,correct]);mcCurrent={{term:item.term,correct}};mcAnswered=false;document.getElementById('mc-q').textContent=item.term;document.getElementById('mc-fb').className='fb';document.getElementById('mc-next').classList.add('hidden');const ch=document.getElementById('mc-choices');ch.innerHTML='';choices.forEach(c=>{{const b=document.createElement('button');b.className='c-btn';b.textContent=c;b.onclick=()=>answerMC(b,c,correct,choices);ch.appendChild(b)}});renderMCScore()}}
function renderMCScore(){{const pct=mcTotal?Math.round(mcCorrect/mcTotal*100):0;document.getElementById('mc-scores').innerHTML='<span class="badge b-total">📋 '+mcTotal+' Qs</span><span class="badge b-correct">✅ '+mcCorrect+'</span><span class="badge b-wrong">❌ '+(mcTotal-mcCorrect)+'</span><span class="badge b-pct">🎯 '+(mcTotal?pct+'%':'—')+'</span>'}}
function answerMC(btn,chosen,correct){{if(mcAnswered)return;mcAnswered=true;const ok=chosen.toLowerCase()===correct.toLowerCase();if(ok)mcCorrect++;mcTotal++;document.querySelectorAll('.c-btn').forEach(b=>{{b.disabled=true;if(b.textContent.toLowerCase()===correct.toLowerCase())b.classList.add('correct');else if(b===btn&&!ok)b.classList.add('wrong')}});const fb=document.getElementById('mc-fb');fb.textContent=ok?'✅ Correct!':'❌ Wrong! Answer: '+correct;fb.className='fb '+(ok?'ok':'bad');document.getElementById('mc-next').classList.remove('hidden');renderMCScore()}}
function nextMC(){{if(mcTotal>=D.length&&D.length>1){{const pct=Math.round(mcCorrect/mcTotal*100);document.getElementById('mc-dscore').textContent=pct+'%';document.getElementById('mc-dsub').textContent=mcCorrect+' correct out of '+mcTotal;document.getElementById('mc-done').classList.remove('hidden');return}}loadMC()}}
function resetMC(){{document.getElementById('mc-done').classList.add('hidden');initMC()}}
function initID(){{idTotal=0;idCorrect=0;document.getElementById('id-done').classList.add('hidden');loadID()}}
function loadID(){{const item=D[Math.floor(Math.random()*D.length)];idCurrent=item['def'];idAnswered=false;document.getElementById('id-q').textContent=item.term;const inp=document.getElementById('id-inp');inp.value='';inp.className='id-input';inp.disabled=false;document.getElementById('id-fb').className='fb';document.getElementById('id-sub').classList.remove('hidden');document.getElementById('id-next').classList.add('hidden');renderIDScore();inp.focus()}}
function renderIDScore(){{const pct=idTotal?Math.round(idCorrect/idTotal*100):0;document.getElementById('id-scores').innerHTML='<span class="badge b-total">📋 '+idTotal+' Qs</span><span class="badge b-correct">✅ '+idCorrect+'</span><span class="badge b-wrong">❌ '+(idTotal-idCorrect)+'</span><span class="badge b-pct">🎯 '+(idTotal?pct+'%':'—')+'</span>'}}
function submitID(){{if(idAnswered||!idCurrent)return;const inp=document.getElementById('id-inp');const ok=inp.value.trim().toLowerCase()===idCurrent.trim().toLowerCase();if(ok)idCorrect++;idTotal++;idAnswered=true;inp.disabled=true;inp.className='id-input '+(ok?'ok':'bad');const fb=document.getElementById('id-fb');fb.textContent=ok?'✅ Correct!':'❌ Wrong! Answer: '+idCurrent;fb.className='fb '+(ok?'ok':'bad');document.getElementById('id-sub').classList.add('hidden');document.getElementById('id-next').classList.remove('hidden');renderIDScore()}}
function nextID(){{if(idTotal>=D.length&&D.length>1){{const pct=Math.round(idCorrect/idTotal*100);document.getElementById('id-dscore').textContent=pct+'%';document.getElementById('id-dsub').textContent=idCorrect+' correct out of '+idTotal;document.getElementById('id-done').classList.remove('hidden');return}}loadID()}}
function resetID(){{document.getElementById('id-done').classList.add('hidden');initID()}}
document.getElementById('id-inp').addEventListener('keydown',e=>{{if(e.key==='Enter'){{if(!document.getElementById('id-next').classList.contains('hidden'))nextID();else submitID()}}}}); 
setMode('fc');
</script>
</body>
</html>"""