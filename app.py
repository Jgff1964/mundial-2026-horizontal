from datetime import datetime
from flask import Flask, jsonify, render_template_string, request, Response
from bracket_logic import make_bracket
from fifa_client import FifaOfficialClient
from renderer import render_svg

app = Flask(__name__)
STATE = {"matches": [], "last_update": None, "last_error": None, "include_thirds": False}

PAGE = '''
<!doctype html><html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes, viewport-fit=cover">
<title>Mundial 2026 Horizontal</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#050816">
<style>
*{box-sizing:border-box} html,body{margin:0;background:#050816;color:#fff;font-family:Arial,sans-serif;height:100%;overflow:hidden}
body{display:flex;flex-direction:column}
header{height:62px;flex:0 0 auto;background:linear-gradient(90deg,#07142f,#090315);border-bottom:1px solid rgba(255,255,255,.14);display:flex;align-items:center;gap:8px;padding:8px;overflow-x:auto}
h1{font-size:15px;margin:0;white-space:nowrap;line-height:1.05}
button,.chip{border:0;border-radius:999px;background:#1d2a4a;color:#fff;padding:9px 11px;font-weight:800;font-size:12px;white-space:nowrap}
.primary{background:linear-gradient(90deg,#159cff,#ff2b6d)}
.zoom{display:flex;gap:5px;align-items:center}
label{display:flex;align-items:center;gap:4px;font-size:12px}
#status{position:absolute;top:68px;left:8px;right:8px;z-index:5;background:rgba(7,13,31,.88);border:1px solid rgba(255,255,255,.16);border-radius:10px;padding:8px;font-size:12px;color:#dce6ff;display:none}
#status.show{display:block}.error{background:rgba(255,43,109,.22)!important;border-color:#ff2b6d!important}
.viewport{flex:1;overflow:auto;-webkit-overflow-scrolling:touch;touch-action:pan-x pan-y pinch-zoom;background:#02040d}
#canvas{transform-origin:top left;display:inline-block;min-width:1800px;min-height:1010px}
.empty{padding:40px;color:#cad4ee;font-size:24px;line-height:1.3;min-width:900px}
.rotate{display:none}
@media (orientation:portrait){
  .rotate{display:flex;position:fixed;inset:0;z-index:20;background:#050816;color:#fff;align-items:center;justify-content:center;text-align:center;padding:28px;font-size:24px;font-weight:800;line-height:1.25}
}
</style></head>
<body>
<div class="rotate">Girá el celular en horizontal<br><span style="font-size:15px;color:#aeb8d0">El cuadro está diseñado para landscape con zoom.</span></div>
<header>
  <h1>Mundial 2026<br>Horizontal</h1>
  <button class="primary" onclick="updateData()">Actualizar FIFA</button>
  <button onclick="fitWidth()">Ajustar</button>
  <div class="zoom">
    <button onclick="setZoom(.5)">50%</button>
    <button onclick="setZoom(.75)">75%</button>
    <button onclick="setZoom(1)">100%</button>
    <button onclick="setZoom(1.25)">125%</button>
    <button onclick="setZoom(1.5)">150%</button>
  </div>
  <label class="chip"><input id="thirds" type="checkbox" onchange="setThirds()"> Terceros</label>
</header>
<div id="status"></div>
<main class="viewport" id="vp"><div id="canvas">{{ svg|safe }}</div></main>
<script>
let zoom = 1;
const canvas = document.getElementById('canvas');
const vp = document.getElementById('vp');
function showStatus(msg, err=false){
  const s=document.getElementById('status'); s.textContent=msg; s.className='show'+(err?' error':''); setTimeout(()=>{s.className=''}, 4500);
}
function applyZoom(){canvas.style.transform='scale('+zoom+')';canvas.style.width=(1800*zoom)+'px';canvas.style.height=(1010*zoom)+'px';}
function setZoom(z){zoom=z;applyZoom();}
function fitWidth(){zoom=Math.max(.35, Math.min(1.5, vp.clientWidth/1800));applyZoom();}
async function updateData(){
  showStatus('Actualizando desde FIFA...');
  try{const r=await fetch('/api/update',{method:'POST'});const j=await r.json();if(!j.ok)throw new Error(j.error||'Error');await loadBracket();showStatus('Actualizado: '+j.last_update);}
  catch(e){showStatus('Error: '+e.message,true);}
}
async function setThirds(){
  await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({include_thirds:document.getElementById('thirds').checked})});
  await loadBracket();
}
async function loadBracket(){
  const r=await fetch('/api/render'); const j=await r.json();
  canvas.innerHTML=j.svg; document.getElementById('thirds').checked=j.include_thirds; applyZoom();
}
window.addEventListener('resize',()=>{});
fitWidth(); loadBracket();
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(()=>{});}
</script>
</body></html>
'''

def current_svg():
    if not STATE["matches"]:
        return '<div class="empty">Tocá “Actualizar FIFA” para cargar los datos reales y generar el cuadro completo.</div>'
    bracket = make_bracket(STATE["matches"], include_thirds=STATE["include_thirds"])
    subtitle = "Con mejores terceros · horizontal" if STATE["include_thirds"] else "Sin terceros · horizontal"
    return render_svg(bracket, subtitle=subtitle)

@app.route("/")
def index():
    return render_template_string(PAGE, svg=current_svg())

@app.route("/api/update", methods=["POST"])
def update():
    try:
        STATE["matches"] = FifaOfficialClient().fetch_matches()
        STATE["last_update"] = datetime.now().isoformat(timespec="seconds")
        STATE["last_error"] = None
        return jsonify({"ok": True, "last_update": STATE["last_update"], "matches": len(STATE["matches"])})
    except Exception as exc:
        STATE["last_error"] = str(exc)
        return jsonify({"ok": False, "error": str(exc)}), 500

@app.route("/api/settings", methods=["POST"])
def settings():
    data = request.get_json(force=True, silent=True) or {}
    STATE["include_thirds"] = bool(data.get("include_thirds"))
    return jsonify({"ok": True, "include_thirds": STATE["include_thirds"]})

@app.route("/api/render")
def render():
    return jsonify({"svg": current_svg(), "include_thirds": STATE["include_thirds"]})

@app.route("/bracket.svg")
def bracket_svg():
    return Response(current_svg(), mimetype="image/svg+xml")

@app.route("/manifest.json")
def manifest():
    return jsonify({"name":"Mundial 2026 Horizontal","short_name":"Mundial 2026","start_url":"/","display":"standalone","orientation":"landscape","background_color":"#050816","theme_color":"#050816","icons":[]})

@app.route("/sw.js")
def sw():
    return app.response_class('self.addEventListener("install",e=>self.skipWaiting());self.addEventListener("activate",e=>self.clients.claim());', mimetype="application/javascript")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
