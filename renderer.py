from html import escape
from flags import flag_for


def team_text(name):
    if not name:
        return "RIVAL A DEFINIR"
    s = str(name)
    if s.lower().startswith("ganador") or s.lower().startswith("perdedor") or "definir" in s.lower() or "mejor tercero" in s.lower():
        return escape(s.upper())
    return f"{flag_for(s)} {escape(s.upper())}"


def box(x,y,w,h,title,home,away,sub="",color="#0078ff"):
    return f"""
    <g>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#f7f7f7" stroke="#dfe9ff" stroke-width="1.2"/>
      <rect x="{x}" y="{y}" width="{w}" height="24" rx="9" fill="{color}"/>
      <text x="{x+w/2}" y="{y+17}" class="title">{escape(title)}</text>
      <text x="{x+14}" y="{y+43}" class="team">{team_text(home)}</text>
      <text x="{x+w/2}" y="{y+58}" class="vs">VS</text>
      <text x="{x+14}" y="{y+75}" class="team">{team_text(away)}</text>
      <text x="{x+w/2}" y="{y+h-10}" class="sub">{escape(sub or "")}</text>
    </g>"""


def connector(x1,y1,x2,y2,color):
    mid=(x1+x2)/2
    return f'<path d="M{x1},{y1} C{mid},{y1} {mid},{y2} {x2},{y2}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" filter="url(#glow)"/>'


def render_svg(bracket, subtitle="Promiedos + zonas validadas"):
    W,H=1800,1010; bw,bh=230,82
    left_y=[145,240,335,430,540,635,730,825]; right_y=left_y
    x_l32,x_l16,x_lqf,x_lsf=55,345,555,680
    x_final=830; x_rsf,x_rqf,x_r16,x_r32=1030,1145,1345,1515
    source = bracket.get("source","")
    parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><filter id="glow"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter><linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="#040819"/><stop offset=".5" stop-color="#02040d"/><stop offset="1" stop-color="#080313"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<path d="M36,960 C10,640 10,220 145,36 H650" stroke="#20a8ff" stroke-width="5" fill="none" filter="url(#glow)"/>
<path d="M1764,960 C1790,640 1790,220 1655,36 H1150" stroke="#ff1d68" stroke-width="5" fill="none" filter="url(#glow)"/>
<text x="900" y="62" class="main">MUNDIAL 2026 · CUADRO PROYECTADO HOY</text>
<text x="900" y="98" class="subtitle">{escape(subtitle)}</text>
<text x="37" y="610" class="vertical" transform="rotate(-90 37 610)">CAMINO 1</text>
<text x="1763" y="610" class="vertical" transform="rotate(90 1763 610)">CAMINO 2</text>
<text x="900" y="230" class="trophy">🏆</text>''']
    def header(txt,x,y,w): return f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="10" fill="#050915" stroke="#31466e"/><text x="{x+w/2}" y="{y+18}" class="head">{txt}</text>'
    for txt,x,w in [("DIECISEISAVOS",55,230),("OCTAVOS",345,160),("CUARTOS",555,135),("SEMIS",680,155),("FINAL",835,130),("SEMIS",1015,160),("CUARTOS",1145,135),("OCTAVOS",1345,160),("DIECISEISAVOS",1515,230)]:
        parts.append(header(txt,x,108,w))
    for no,y in zip([74,77,73,75,83,84,81,82],left_y):
        m=bracket["r32"][no]; color="#0b78dd" if no in [74,77,73,75,81,82] else "#00a0a8"; parts.append(box(x_l32,y,bw,bh,f"M{no} | {m.get('venue','')}",m["home"],m["away"],m.get("sub",""),color))
    for no,y in [(89,200),(90,380),(93,595),(94,780)]:
        m=bracket["r16"][no]; parts.append(box(x_l16,y,160,bh,f"M{no} | {m.get('venue','')}",m["home"],m["away"],"", "#0b78dd" if no in [89,90] else "#00a0a8"))
    for no,y in [(97,330),(98,680)]:
        m=bracket["qf"][no]; parts.append(box(x_lqf,y,135,bh,f"M{no} | {m.get('venue','')}",m["home"],m["away"],"", "#0b78dd" if no==97 else "#00a0a8"))
    parts.append(box(x_lsf,500,155,bh,"M101 | DAL",bracket["sf"][101]["home"],bracket["sf"][101]["away"],"","#6a2bc9"))
    parts.append(box(x_final,500,150,bh,"M104 | NYNJ",bracket["final"][104]["home"],bracket["final"][104]["away"],"","#c89416"))
    parts.append('<text x="910" y="690" class="thirdtitle">3° PUESTO / TERCER PUESTO</text>')
    parts.append(box(830,705,150,bh,"M103 | MIA",bracket["third"][103]["home"],bracket["third"][103]["away"],"","#e37812"))
    parts.append(box(x_rsf,500,155,bh,"M102 | ATL",bracket["sf"][102]["home"],bracket["sf"][102]["away"],"","#d11169"))
    for no,y in [(99,330),(100,680)]:
        m=bracket["qf"][no]; parts.append(box(x_rqf,y,135,bh,f"M{no} | {m.get('venue','')}",m["home"],m["away"],"","#d11169"))
    for no,y in [(91,200),(92,380),(95,595),(96,780)]:
        m=bracket["r16"][no]; parts.append(box(x_r16,y,160,bh,f"M{no} | {m.get('venue','')}",m["home"],m["away"],"","#e0004d"))
    for no,y in zip([76,78,79,80,86,88,85,87],right_y):
        m=bracket["r32"][no]; parts.append(box(x_r32,y,bw,bh,f"M{no} | {m.get('venue','')}",m["home"],m["away"],m.get("sub",""),"#e0004d"))
    pairs_left=[((x_l32+bw,left_y[0]+bh/2),(x_l16,200+bh/2)),((x_l32+bw,left_y[1]+bh/2),(x_l16,200+bh/2)),((x_l32+bw,left_y[2]+bh/2),(x_l16,380+bh/2)),((x_l32+bw,left_y[3]+bh/2),(x_l16,380+bh/2)),((x_l32+bw,left_y[4]+bh/2),(x_l16,595+bh/2)),((x_l32+bw,left_y[5]+bh/2),(x_l16,595+bh/2)),((x_l32+bw,left_y[6]+bh/2),(x_l16,780+bh/2)),((x_l32+bw,left_y[7]+bh/2),(x_l16,780+bh/2)),((x_l16+160,200+bh/2),(x_lqf,330+bh/2)),((x_l16+160,380+bh/2),(x_lqf,330+bh/2)),((x_l16+160,595+bh/2),(x_lqf,680+bh/2)),((x_l16+160,780+bh/2),(x_lqf,680+bh/2)),((x_lqf+135,330+bh/2),(x_lsf,500+bh/2)),((x_lqf+135,680+bh/2),(x_lsf,500+bh/2)),((x_lsf+155,500+bh/2),(x_final,500+bh/2))]
    for a,b in pairs_left: parts.append(connector(a[0],a[1],b[0],b[1],"#54b8ff"))
    pairs_right=[((x_r32,right_y[0]+bh/2),(x_r16+160,200+bh/2)),((x_r32,right_y[1]+bh/2),(x_r16+160,200+bh/2)),((x_r32,right_y[2]+bh/2),(x_r16+160,380+bh/2)),((x_r32,right_y[3]+bh/2),(x_r16+160,380+bh/2)),((x_r32,right_y[4]+bh/2),(x_r16+160,595+bh/2)),((x_r32,right_y[5]+bh/2),(x_r16+160,595+bh/2)),((x_r32,right_y[6]+bh/2),(x_r16+160,780+bh/2)),((x_r32,right_y[7]+bh/2),(x_r16+160,780+bh/2)),((x_r16,200+bh/2),(x_rqf+135,330+bh/2)),((x_r16,380+bh/2),(x_rqf+135,330+bh/2)),((x_r16,595+bh/2),(x_rqf+135,680+bh/2)),((x_r16,780+bh/2),(x_rqf+135,680+bh/2)),((x_rqf,330+bh/2),(x_rsf+155,500+bh/2)),((x_rqf,680+bh/2),(x_rsf+155,500+bh/2)),((x_rsf,500+bh/2),(x_final+150,500+bh/2))]
    for a,b in pairs_right: parts.append(connector(a[0],a[1],b[0],b[1],"#ff4a8c"))
    parts.append(f'''<text x="900" y="958" class="foot">{escape(source)}</text><text x="900" y="980" class="foot">Pantalla horizontal · zoom móvil · Promiedos + zonas validadas</text><style>
.main{{font:700 42px Arial,sans-serif;fill:#fff;text-anchor:middle}}.subtitle{{font:700 24px Arial,sans-serif;fill:#ddd;text-anchor:middle}}.head{{font:700 13px Arial,sans-serif;fill:#fff;text-anchor:middle}}.title{{font:700 14px Arial,sans-serif;fill:#fff;text-anchor:middle}}.team{{font:700 13px Arial,sans-serif;fill:#111}}.vs{{font:700 10px Arial,sans-serif;fill:#222;text-anchor:middle}}.sub{{font:700 11px Arial,sans-serif;fill:#111;text-anchor:middle}}.vertical{{font:800 34px Arial,sans-serif;fill:#fff;text-anchor:middle;letter-spacing:2px}}.trophy{{font:90px Arial,sans-serif;fill:#d9a323;text-anchor:middle}}.thirdtitle{{font:700 14px Arial,sans-serif;fill:#ffcc44;text-anchor:middle}}.foot{{font:italic 700 15px Arial,sans-serif;fill:#eee;text-anchor:middle}}</style></svg>''')
    return "\n".join(parts)
