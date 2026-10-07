# Code patterns (adapt them, do not copy a fixed layout)

Small, working building blocks for a self-contained page. Plain HTML/CSS/JS/SVG only.
Change names, colors, and sizes to fit the project. Never ship unused snippets.

## 1. Look: tokens, dark and light
```css
:root{--bg:#0b1020;--panel:#111833;--card:#18223f;--line:#2a3560;--fg:#e6ebff;--mut:#8b96c4;--acc:#38bdf8}
[data-theme=light]{--bg:#f3f5fb;--panel:#fff;--card:#eef1f9;--line:#c9d1ea;--fg:#14182b;--mut:#59638a;--acc:#2563eb}
body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;background:var(--bg);color:var(--fg)}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px}
.part{--c:#38bdf8;border:2px solid var(--c);border-radius:16px;padding:14px;cursor:pointer;transition:.2s;
  background:linear-gradient(160deg,color-mix(in srgb,var(--c) 18%,var(--card)),var(--card))}
.part:hover,.part.active{box-shadow:0 0 0 3px color-mix(in srgb,var(--c) 40%,transparent),0 10px 30px color-mix(in srgb,var(--c) 30%,transparent);transform:translateY(-2px)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
```
Theme toggle: `document.documentElement.dataset.theme = document.documentElement.dataset.theme==='dark'?'light':'dark'`
(set `<html data-theme="dark">`).

## 2. Animated arrow with a label and a moving dot (SVG)
```html
<svg viewBox="0 0 600 120" width="100%">
  <defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">
    <path d="M0,0L10,5L0,10z" fill="#38bdf8"/></marker></defs>
  <path id="p1" d="M120,60 C220,60 260,60 360,60" fill="none" stroke="#38bdf8" stroke-width="2.5"
        stroke-dasharray="7 6" marker-end="url(#ah)">
    <animate attributeName="stroke-dashoffset" from="0" to="-26" dur="1s" repeatCount="indefinite"/></path>
  <circle r="5" fill="#38bdf8"><animateMotion dur="2.4s" repeatCount="indefinite"><mpath href="#p1"/></animateMotion></circle>
  <g><rect x="190" y="47" width="100" height="26" rx="13" fill="#111833" stroke="#38bdf8"/>
     <text x="240" y="64" text-anchor="middle" fill="#e6ebff" font-size="12">POST /chat</text></g>
</svg>
```
Reply dot going back: a second circle with `<animateMotion ... keyPoints="1;0" keyTimes="0;1" calcMode="linear"><mpath href="#p1"/></animateMotion>`.
For boxes made of HTML, measure them with `getBoundingClientRect()` relative to a `position:relative`
container and draw the paths in an absolutely positioned SVG on top (redraw on resize).

## 3. Guided step player ("follow one request")
```html
<div class="card" id="player"><div id="cap"></div>
  <button id="prev">Prev</button><button id="play">Play</button><button id="next">Next</button></div>
```
```js
const steps=[
  {part:'frontend',file:'src/api.js',text:'The app packs the question into JSON and sends it.',data:'{ "question": "..." }'},
  {part:'backend',file:'app/routes.py',text:'The server receives it and asks the model.',data:''}
];
let i=0,timer=null;
function show(n){
  i=(n+steps.length)%steps.length;const s=steps[i];
  document.querySelectorAll('[data-part]').forEach(el=>el.classList.toggle('active',el.dataset.part===s.part));
  document.getElementById('cap').innerHTML='<b>Step '+(i+1)+' of '+steps.length+'</b> '+s.text+
    '<div class="mut">'+s.file+'</div>'+(s.data?'<pre>'+s.data+'</pre>':'');
}
function play(){timer=setInterval(()=>show(i+1),3500);document.getElementById('play').textContent='Pause'}
function pause(){clearInterval(timer);timer=null;document.getElementById('play').textContent='Play'}
document.getElementById('next').onclick=()=>{pause();show(i+1)};
document.getElementById('prev').onclick=()=>{pause();show(i-1)};
document.getElementById('play').onclick=()=>timer?pause():play();
show(0);play();
```
Give each diagram box `data-part="frontend"` so the player lights it up. Escape any text you insert
with innerHTML (use a small `esc()` helper) if it comes from data.

## 4. Details side panel (click a box, file, or arrow)
```js
const INFO={'src/api.js':{what:'Sends questions to the backend.',uses:['backend/routes.py'],proof:'fetch("/api/chat") on line 12'}};
function openInfo(key){const d=INFO[key];if(!d)return;
  panel.innerHTML='<h3>'+key+'</h3><p>'+d.what+'</p><small>Proof: '+d.proof+'</small>';panel.classList.add('open')}
document.addEventListener('click',e=>{const t=e.target.closest('[data-info]');if(t)openInfo(t.dataset.info)});
```
Panel CSS: fixed on the right on desktop (width 340px), a bottom sheet on phones.

## 5. Sticky menu that follows the scroll
```js
const links=[...document.querySelectorAll('nav a')];
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)
  links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+e.target.id))}),{rootMargin:'-40% 0px -55% 0px'});
document.querySelectorAll('section[id]').forEach(s=>io.observe(s));
```
Use `html{scroll-behavior:smooth}` and `section{scroll-margin-top:70px}`.

## 6. Copy button for commands
```js
document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=()=>{navigator.clipboard.writeText(b.dataset.copy);b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1200)});
```

## 7. Dependency view without a hairball
Group files by folder into clusters. Draw only edges of the hovered or clicked file, with moving
dots from the importing file to the imported file. A canvas force layout is fine for 50+ files;
for fewer, columns by depth in plain SVG are clearer.
