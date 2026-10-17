"""Builds every animated SVG in assets/ (except stats.svg, see stats.py).

Run: python3 scripts/build.py
"""
import colorsys, html, pathlib, re, textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / "assets"
ICONS = ROOT / "scripts" / "icons"
(A / "projects").mkdir(parents=True, exist_ok=True)
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', Consolas, 'Courier New', monospace"
G, IN = "#10D59A", "#6366F1"  # emerald + indigo, the brand pair
PV = "#7F75E8"  # current-company accent
e = html.escape


def dark(hexc, f):
    r, g, b = (int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb(h, max(0, l * f), s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


STYLE = """
  .fl { animation: fl 4s ease-in-out infinite; }
  @keyframes fl { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-7px); } }
  .sh { animation: sh 4s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes sh { 0%,100% { transform: scaleX(1); opacity: .45; } 50% { transform: scaleX(.8); opacity: .2; } }
  .fp { animation: fp 9s cubic-bezier(.45,0,.2,1) infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes fp { 0%,78% { transform: scaleX(1) skewY(0); } 83% { transform: scaleX(.02) skewY(-12deg); } 88% { transform: scaleX(-1) skewY(0); }
                  93% { transform: scaleX(.02) skewY(12deg); } 98%,100% { transform: scaleX(1) skewY(0); } }
  .glow { animation: glow 6s ease-in-out infinite; }
  @keyframes glow { 0%,100% { opacity: .35; } 50% { opacity: .6; } }
  .up { animation: up .8s cubic-bezier(.2,.7,.2,1) backwards; }
  @keyframes up { from { transform: translateY(14px); } to { transform: none; } }  /* no opacity: frame 0 must be readable */
"""

DEFS = f"""
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#070d14"/><stop offset=".55" stop-color="#0a1a1c"/><stop offset="1" stop-color="#0f1030"/></linearGradient>
  <linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14202a"/><stop offset="1" stop-color="#0d141c"/></linearGradient>
  <linearGradient id="gloss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".2"/><stop offset=".45" stop-color="#fff" stop-opacity=".03"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G}"/><stop offset="1" stop-color="{IN}"/></linearGradient>
  <radialGradient id="o1"><stop offset="0" stop-color="{G}" stop-opacity=".45"/><stop offset="1" stop-color="{G}" stop-opacity="0"/></radialGradient>
  <radialGradient id="o2"><stop offset="0" stop-color="{IN}" stop-opacity=".45"/><stop offset="1" stop-color="{IN}" stop-opacity="0"/></radialGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.1" fill="#fff" fill-opacity=".06"/></pattern>
  <filter id="bl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
  <linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".85" stop-color="{G}" stop-opacity=".05"/><stop offset="1" stop-color="{G}" stop-opacity=".22"/></linearGradient>
"""


def frame(w, h, body, style="", defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>{STYLE}{style}</style>
<defs>{DEFS}{defs}<clipPath id="c"><rect width="{w}" height="{h}" rx="20"/></clipPath></defs>
<g clip-path="url(#c)">
  <rect width="{w}" height="{h}" fill="url(#bg)"/>
  <rect width="{w}" height="{h}" fill="url(#dots)"/>
  <circle class="glow" cx="{w - 60}" cy="50" r="280" fill="url(#o2)"/>
  <circle class="glow" style="animation-delay:-3s" cx="70" cy="{h - 30}" r="240" fill="url(#o1)"/>
  {body}
  {hud(w, h)}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="19.5" fill="none" stroke="#fff" stroke-opacity=".1"/>
</svg>"""


def hud(w, h, inset=10, arm=20, col=G):
    """HUD corner brackets plus a slow scan line; shared by every dark card."""
    i, a = inset, arm
    corners = (f"M{i},{i + a} V{i} H{i + a} M{w - i - a},{i} H{w - i} V{i + a} "
               f"M{w - i},{h - i - a} V{h - i} H{w - i - a} M{i + a},{h - i} H{i} V{h - i - a}")
    return f"""<path d="{corners}" fill="none" stroke="{col}" stroke-width="2" stroke-opacity=".55" stroke-linecap="round"/>
  <rect class="scan" x="0" y="0" width="{w}" height="70" fill="url(#scan)" style="animation-name:scan{h}"/>
  <style>.scan {{ animation: scan{h} 8s linear infinite; }} @keyframes scan{h} {{ from {{ transform: translateY(-80px); }} to {{ transform: translateY({h + 10}px); }} }}</style>"""


def tile3d(w, h, col, r=14, depth=6):
    """The raised card face every section uses."""
    return f"""<rect y="{depth}" width="{w}" height="{h}" rx="{r}" fill="{dark(col, .35)}"/>
    <rect y="{depth / 2}" width="{w}" height="{h}" rx="{r}" fill="{dark(col, .5)}"/>
    <rect width="{w}" height="{h}" rx="{r}" fill="url(#face)"/>
    <rect width="{w}" height="{h}" rx="{r}" fill="{col}" fill-opacity=".06"/>
    <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r - .5}" fill="none" stroke="{col}" stroke-opacity=".38"/>"""


def icon_tile(emoji, col, size, delay):
    r = size * .25
    return f"""<g class="fp" style="animation-delay:{delay:.2f}s">
    <rect y="{size * .12:.1f}" width="{size}" height="{size}" rx="{r}" fill="{dark(col, .4)}"/>
    <rect y="{size * .06:.1f}" width="{size}" height="{size}" rx="{r}" fill="{dark(col, .65)}"/>
    <rect width="{size}" height="{size}" rx="{r}" fill="#1a2430"/>
    <rect width="{size}" height="{size}" rx="{r}" fill="{col}" fill-opacity=".18"/>
    <text x="{size / 2}" y="{size * .68:.1f}" text-anchor="middle" font-size="{size * .48:.0f}">{emoji}</text>
    <rect width="{size}" height="{size}" rx="{r}" fill="url(#gloss)"/>
    <rect x=".5" y=".5" width="{size - 1}" height="{size - 1}" rx="{r - .5}" fill="none" stroke="{col}" stroke-opacity=".6"/>
  </g>"""


def write(name, svg):
    (A / name).write_text(svg, encoding="utf-8")


# ---------------- header ----------------
def header():
    W, H = 1200, 380
    # terminal lines appear one by one, then the whole thing loops
    term = [
        ("#6b7280", "$ ", "#e5e7eb", "git push origin main"),
        ("#10D59A", "✓ ", "#a9b3c9", "lint & tests passed"),
        ("#10D59A", "✓ ", "#a9b3c9", "nest build · api ready"),
        ("#10D59A", "✓ ", "#a9b3c9", "prisma migrate deploy"),
        ("#10D59A", "✓ ", "#a9b3c9", "next build · admin dashboard"),
        ("#818CF8", "→ ", "#e5e7eb", "shipped to production 🚀"),
    ]
    n = len(term)
    rows = "".join(
        f'<text x="24" y="{76 + i * 25}" class="tl t{i}"><tspan fill="{c1}">{e(p)}</tspan><tspan fill="{c2}">{e(t)}</tspan></text>'
        for i, (c1, p, c2, t) in enumerate(term))
    cyc = 12  # lines show from frame 0, blank briefly, then retype one by one
    tl_css = "".join(
        f".t{i} {{ animation: tl{i} {cyc}s steps(1) infinite; }} @keyframes tl{i} {{ 0%,72% {{ opacity: 1; }} 74% {{ opacity: 0; }} {76 + i * 4}%,100% {{ opacity: 1; }} }}\n"
        for i in range(n))
    chips = [("🧭", "Team Lead @ QeemaTech", 236, PV), ("⚡", "4+ yrs in production", 206, "#fff"), ("📍", "Cairo, Egypt", 146, "#fff")]
    cx, ch = 72, ""
    for emo, label, w, col in chips:
        hl = col != "#fff"
        ch += (f'<rect x="{cx}" y="290" width="{w}" height="36" rx="18" fill="{col}" fill-opacity="{.2 if hl else .06}" stroke="{col}" stroke-opacity="{.7 if hl else .12}"/>'
               f'<text x="{cx + w / 2}" y="313" text-anchor="middle" fill="{"#e6e3ff" if hl else "#aab3c8"}" font-weight="{600 if hl else 400}">{emo}  {e(label)}</text>')
        cx += w + 12
    # tron-style floor: rays to a vanishing point, horizontal lines sliding toward the viewer
    vx, hz = 600, 300
    rays = "".join(f'<line x1="{vx}" y1="{hz}" x2="{vx + k * 160}" y2="{H}"/>' for k in range(-9, 10))
    rungs = "".join(f'<line class="rung" style="animation-delay:{-k * .8:.1f}s" x1="0" x2="{W}" y1="{hz}" y2="{hz}"/>' for k in range(5))
    floor = f'''<g stroke="{G}" stroke-opacity=".09" stroke-width="1"><clipPath id="fl"><rect y="{hz}" width="{W}" height="{H - hz}"/></clipPath>
    <g clip-path="url(#fl)">{rays}{rungs}</g></g>'''
    glyph_list = [("</>", 640, 70, 22), ("{ }", 700, 340, 18), ("=>", 40, 40, 16), ("async", 560, 200, 14), ("[ ]", 1160, 330, 18), ("0x1F", 470, 60, 13)]
    glyphs = "".join(f'<text class="gl" style="animation-delay:{-i * 1.3:.1f}s" x="{x}" y="{y}" font-family="{MONO}" font-size="{s}" fill="{G if i % 2 else IN}" fill-opacity=".28">{e(t)}</text>'
                     for i, (t, x, y, s) in enumerate(glyph_list))
    body = f"""
  <circle class="orb" cx="1000" cy="90" r="160" fill="{IN}" opacity=".5" filter="url(#blur)"/>
  <circle class="orb o2" cx="1130" cy="300" r="120" fill="{G}" opacity=".35" filter="url(#blur)"/>
  <circle class="orb o3" cx="720" cy="360" r="100" fill="#22D3EE" opacity=".18" filter="url(#blur)"/>
  <rect class="shine" x="0" y="0" width="300" height="{H}" fill="url(#shg)" transform="skewX(-20)"/>
  {floor}
  {glyphs}
  <g transform="translate({W - 60} 30)" font-family="{MONO}" font-size="12">
    <rect x="-150" y="-2" width="150" height="24" rx="12" fill="{G}" fill-opacity=".1" stroke="{G}" stroke-opacity=".5"/>
    <circle class="live" cx="-134" cy="10" r="4" fill="{G}"/>
    <text x="-122" y="14" fill="#c9f7e6">status: shipping</text>
  </g>

  <g transform="translate(770 62)"><g class="up" style="animation-delay:1s">
    <rect width="370" height="236" rx="14" fill="#0b1117" fill-opacity=".88" stroke="#fff" stroke-opacity=".1"/>
    <path d="M.5 14.5a14 14 0 0 1 14-14h341a14 14 0 0 1 14 14V40H.5z" fill="#121a22"/>
    <circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
    <text x="350" y="25" text-anchor="end" font-family="{MONO}" font-size="12" fill="#6b7280">~/stockship — deploy</text>
    <g font-family="{MONO}" font-size="13.5" xml:space="preserve">{rows}</g>
    <rect class="cur" x="24" y="{76 + n * 25 - 14}" width="9" height="17" fill="{G}"/>
  </g></g>

  <text class="up" style="animation-delay:.15s" x="72" y="104" font-family="{MONO}" font-size="18" fill="{G}">// hello world, I'm</text>
  <text class="up" style="animation-delay:.4s" x="68" y="178" font-family="{SANS}" font-size="68" font-weight="800" fill="#f4f7fb" letter-spacing="-1.5">Ahmed Raouf</text>
  <rect class="bar" x="72" y="198" width="200" height="6" rx="3" fill="url(#ac)"/>
  <text class="up" style="animation-delay:.7s" x="72" y="250" font-family="{SANS}" font-size="27" font-weight="600" fill="#d7dcf0"><tspan fill="#A9A3FF">Technical Team Lead</tspan> <tspan fill="#6b7280">·</tspan> Full-stack</text>
  <g class="up" style="animation-delay:1s" font-family="{SANS}" font-size="15.5">{ch}</g>
"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{STYLE}
  .orb {{ animation: orb 9s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }}
  .o2 {{ animation-duration: 12s; animation-delay: -4s; }} .o3 {{ animation-duration: 15s; animation-delay: -7s; }}
  @keyframes orb {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(-30px,18px) scale(1.12); }} }}
  .bar {{ animation: grow 1.2s .6s cubic-bezier(.2,.7,.2,1) both; transform-origin: left; transform-box: fill-box; }}
  @keyframes grow {{ from {{ transform: scaleX(.15); }} to {{ transform: scaleX(1); }} }}
  .cur {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .shine {{ animation: shine 7s linear infinite; }} @keyframes shine {{ from {{ transform: translateX(-400px); }} to {{ transform: translateX(1700px); }} }}
  .rung {{ animation: rung 4s cubic-bezier(.55,0,1,.45) infinite; }} @keyframes rung {{ from {{ transform: translateY(0); }} to {{ transform: translateY({H - 300}px); }} }}
  .gl {{ animation: gl 7s ease-in-out infinite; }} @keyframes gl {{ 0%,100% {{ transform: translateY(0); opacity: 1; }} 50% {{ transform: translateY(-12px); opacity: .4; }} }}
  .live {{ animation: blink 1.6s ease-in-out infinite; }}
  {tl_css}
</style>
<defs>{DEFS}
  <linearGradient id="shg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="42"/></filter>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>
  {body}
  {hud(W, H, 14, 26)}
</g>
</svg>"""
    write("header.svg", svg)


# ---------------- impact numbers ----------------
IMPACT = [
    ("⏳", "4+", "years shipping", "from C# desktop to NestJS + Next.js", G),
    ("🧭", "Lead", "Technical Team Lead", "QeemaTech · reviews · architecture", IN),
    ("🚀", "5", "products shipped", "Orbex · Tarteel AI · Stockship", "#F59E0B"),
    ("⚡", "75%", "faster CRM queries", "query response time, ERP / CRM", "#22D3EE"),
    ("🏢", "5", "companies", "01 Electronics → QeemaTech", "#EC4899"),
    ("🤖", "AI", "LLM features", "integrated into real products", "#F43F5E"),
]


def impact():
    W, cols, cw, ch, gx, gy, x0, y0 = 920, 3, 276, 118, 18, 26, 22, 26
    rows = (len(IMPACT) + cols - 1) // cols
    H = y0 + rows * (ch + gy) + 4
    out = []
    for i, (emo, num, label, sub, col) in enumerate(IMPACT):
        r, c = divmod(i, cols)
        x, y, d = x0 + c * (cw + gx), y0 + r * (ch + gy), -(r * .5 + c * .35)
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{d:.2f}s">
  {tile3d(cw, ch, col)}
  <g transform="translate(20 20)">{icon_tile(emo, col, 42, i * .9)}</g>
  <text class="pop" style="animation-delay:{.2 + i * .15:.2f}s" x="76" y="50" font-family="{SANS}" font-size="34" font-weight="800" fill="#f4f7fb">{e(num)}</text>
  <text x="76" y="76" font-family="{SANS}" font-size="14" font-weight="600" fill="{col}">{e(label)}</text>
  <text x="20" y="102" font-family="{SANS}" font-size="13.5" fill="#a9b3c9">{e(sub)}</text>
</g></g>""")
    write("impact.svg", frame(W, H, "".join(out), """
  .pop { animation: pop .9s cubic-bezier(.2,1.6,.4,1) backwards; transform-box: fill-box; transform-origin: left center; }
  @keyframes pop { from { transform: scale(.7); } to { transform: none; } }"""))


# ---------------- about code card ----------------
def about():
    K, S, F, N, C, T, P = "#c678dd", "#98c379", "#61afef", "#d19a66", "#6b7280", "#e5e7eb", "#e06c75"
    Y = "#e5c07b"
    rows = [
        [(F, "@Injectable"), (T, "()")],
        [(K, "export class "), (Y, "AhmedRaouf "), (K, "implements "), (Y, "Engineer"), (T, " {")],
        [(P, "  role"), (T, "    = "), (S, "'Technical Team Lead'"), (T, ";")],
        [(P, "  company"), (T, " = "), (S, "'QeemaTech'"), (T, ";")],
        [(P, "  stack"), (T, "   = ["), (S, "'NestJS'"), (T, ", "), (S, "'Next.js'"), (T, ", "), (S, "'MySQL'"), (T, "];")],
        [(P, "  years"), (T, "   = "), (N, "4"), (T, "; "), (C, "// and counting")],
        [(T, "")],
        [(F, "  focus"), (T, "(): "), (Y, "string"), (T, "[] {")],
        [(K, "    return "), (T, "["), (S, "'clean APIs'"), (T, ", "), (S, "'dashboards'"), (T, ",")],
        [(T, "            "), (S, "'AI features'"), (T, ", "), (S, "'team delivery'"), (T, "];")],
        [(T, "  }")],
        [(T, "")],
        [(K, "  async "), (F, "ship"), (T, "(idea: "), (Y, "Idea"), (T, "): "), (Y, "Promise"), (T, "<"), (Y, "Product"), (T, "> {")],
        [(K, "    return "), (P, "idea"), (T, "."), (F, "design"), (T, "()."), (F, "test"), (T, "()."), (F, "deploy"), (T, "();")],
        [(T, "  }")],
        [(T, "}")],
    ]
    body = ""
    for i, r in enumerate(rows):
        ts = "".join(f'<tspan fill="{c}">{e(t)}</tspan>' for c, t in r)
        body += f'<text x="16" y="{72 + i * 22}" xml:space="preserve" class="l" style="animation-delay:{.12 * i:.2f}s"><tspan fill="#3f4a56">{i + 1:>2}  </tspan>{ts}</text>'
    aw, ah = 560, 72 + len(rows) * 22 + 12
    write("about.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{aw}" height="{ah}" viewBox="0 0 {aw} {ah}">
<style>.l{{animation:in .5s ease backwards}}@keyframes in{{from{{transform:translateX(-8px)}}to{{transform:none}}}}
.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}</style>
<rect x=".5" y=".5" width="{aw - 1}" height="{ah - 1}" rx="14" fill="#0b1117" stroke="#fff" stroke-opacity=".12"/>
<path d="M.5 14.5a14 14 0 0 1 14-14h{aw - 29}a14 14 0 0 1 14 14V40H.5z" fill="#121a22"/>
<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
<text x="{aw / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="#8b95ab">src/engineers/ahmed-raouf.ts</text>
<g font-family="{MONO}" font-size="13.5">{body}</g>
<rect class="cur" x="40" y="{72 + (len(rows) - 1) * 22 + 6}" width="8" height="15" fill="{G}"/>
</svg>''')


# ---------------- what I bring ----------------
SERVICES = [
    ("🔌", "APIs & Backends", "#E0234E", "NestJS, Express and Node.js services with REST, GraphQL and WebSockets, cleanly modular."),
    ("🗄️", "Database Design", "#3B82F6", "MySQL, PostgreSQL and SQL Server schemas with Prisma and TypeORM, shaped by real queries."),
    ("🖥️", "Web Front-ends", "#22D3EE", "Fast, responsive React and Next.js apps built on top of the APIs I design."),
    ("📊", "Admin Dashboards", G, "Super Admin dashboards that let a team manage and monitor a whole web and mobile platform."),
    ("🤖", "AI / LLM Integration", "#A78BFA", "Plugging AI and LLM APIs into products to ship AI-powered features people actually use."),
    ("🧭", "Team Leadership", "#EC4899", "Task planning, code review, architecture decisions and Agile/Scrum delivery on schedule."),
]


def services():
    W, cols, cw, ch, gx, gy, x0, y0 = 920, 3, 272, 156, 22, 34, 25, 28
    rows = (len(SERVICES) + cols - 1) // cols
    H = y0 + rows * (ch + gy) + 6
    out = []
    for i, (emo, title, col, desc) in enumerate(SERVICES):
        r, c = divmod(i, cols)
        x, y, d = x0 + c * (cw + gx), y0 + r * (ch + gy), -(r * .5 + c * .35)
        lines = "".join(f'<text x="22" y="{96 + k * 19}">{e(l)}</text>' for k, l in enumerate(textwrap.wrap(desc, 36)[:3]))
        out.append(f"""<g transform="translate({x} {y})">
  <ellipse class="sh" style="animation-delay:{d:.2f}s" cx="{cw / 2}" cy="{ch + 16}" rx="{cw / 2 - 26}" ry="5" fill="{col}" filter="url(#bl)"/>
  <g class="fl" style="animation-delay:{d:.2f}s">
    {tile3d(cw, ch, col, 16, 7)}
    <g transform="translate(22 18)">{icon_tile(emo, col, 44, i * .8)}</g>
    <text x="80" y="47" font-family="{SANS}" font-size="17" font-weight="700" fill="#f4f7fb">{e(title)}</text>
    <g font-family="{SANS}" font-size="13" fill="#a9b3c9">{lines}</g>
  </g>
</g>""")
    write("services.svg", frame(W, H, "".join(out)))


# ---------------- career timeline ----------------
CAREER = [
    ("2021", "01 Electronics", "Intern → Jr. SWE", "Dec 2021 – Jun 2023", "#F43F5E",
     ["C# · WPF desktop", "ERP & CRM modules", "CRM queries −75%"]),
    ("2024", "BookSportz", "Node.js · Scrum", "Jan – Mar 2024", "#F59E0B",
     ["NestJS · GraphQL", "PostgreSQL", "Scrum Master"]),
    ("2024", "FiveM Tech", "Backend Dev", "Dec 2024 – Apr 2025", "#22D3EE",
     ["NestJS REST APIs", "Prisma + MySQL", "SmoothERP"]),
    ("2025", "Triasols", "Full-stack Dev", "May – Dec 2025", "#EC4899",
     ["Scalable APIs", "NestJS · Prisma", "Modular design"]),
    ("2026", "QeemaTech", "Full-stack Dev", "Jan – Aug 2026", G,
     ["Orbex · Tarteel AI", "Stockship · Akfeek", "Admin dashboards"]),
    ("2026", "QeemaTech", "Tech Team Lead", "Aug 2026 – now", PV,
     ["Lead the team", "Code review", "Architecture"]),
]


def career():
    W, x0, colw, top, cardh = 920, 16, 148, 104, 164
    H = top + cardh + 34
    ax = 44
    out = [f'<line x1="{ax}" x2="{W - ax}" y1="56" y2="56" stroke="#fff" stroke-opacity=".12" stroke-width="3" stroke-linecap="round"/>',
           f'<line class="run" x1="{ax}" x2="{W - ax}" y1="56" y2="56" stroke="url(#run)" stroke-width="3" stroke-linecap="round"/>']
    for m, (year, co, role, where, col, pts) in enumerate(CAREER):
        cx = x0 + m * colw + colw / 2
        now = m == len(CAREER) - 1
        out.append(f"""<g transform="translate({cx} 56)">
  <circle class="pl" style="animation-delay:{m * .5:.1f}s" r="16" fill="{col}" fill-opacity=".25"/>
  <circle r="10" fill="{dark(col, .5)}"/><circle r="8" cy="-1.5" fill="{col}"/>
</g>
<text x="{cx}" y="30" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" fill="{col}">{year}{" → NOW" if now else ""}</text>
<text x="{cx}" y="90" text-anchor="middle" font-family="{SANS}" font-size="12" fill="#8b95ab">{e(where)}</text>""")
        x, w, d = x0 + m * colw + 6, colw - 12, -(m * .4)
        fs = 15.5 if len(co) < 13 else 14
        bl = "".join(f'<text x="14" y="{86 + k * 22}"><tspan fill="{col}">▸ </tspan>{e(p)}</text>'
                     for k, p in enumerate(pts))
        out.append(f"""<g transform="translate({x} {top})"><g class="fl" style="animation-delay:{d:.2f}s">
  {tile3d(w, cardh, col, 12, 6)}
  <rect width="{w}" height="4" rx="2" fill="{col}"/>
  <rect width="{w}" height="{cardh}" rx="12" fill="url(#gloss)" opacity=".5"/>
  <text x="14" y="32" font-family="{SANS}" font-size="{fs}" font-weight="700" fill="#f4f7fb">{e(co)}</text>
  <text x="14" y="54" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{col}">{e(role.upper())}</text>
  <g font-family="{SANS}" font-size="11" fill="#a9b3c9">{bl}</g>
</g></g>""")
    write("career.svg", frame(W, H, "".join(out), """
  .run { stroke-dasharray: 140 2000; animation: run 5s linear infinite; }
  @keyframes run { from { stroke-dashoffset: 140; } to { stroke-dashoffset: -900; } }
  .pl { animation: pl 2.4s ease-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes pl { 0% { transform: scale(.6); opacity: .9; } 100% { transform: scale(1.9); opacity: 0; } }""",
                                f'<linearGradient id="run" gradientUnits="userSpaceOnUse" x1="44" x2="876"><stop offset="0" stop-color="{IN}"/><stop offset="1" stop-color="{G}"/></linearGradient>'))


# ---------------- architecture: how the platforms are built ----------------
def architecture():
    W, H = 920, 470
    nodes = {  # key: (x, y, w, h, emoji, title, sub, colour)
        "web": (24, 70, 170, 62, "🖥️", "Web app", "Next.js · React", "#22D3EE"),
        "mob": (24, 156, 170, 62, "📱", "Mobile app", "iOS · Android", "#22D3EE"),
        "adm": (24, 242, 170, 62, "📊", "Super Admin", "Next.js dashboard", "#22D3EE"),
        "svc": (300, 130, 250, 118, "🔌", "NestJS API", "Node.js · TypeScript · REST", G),
        "db": (686, 30, 210, 58, "🗄️", "MySQL", "Prisma / TypeORM", "#3B82F6"),
        "ai": (686, 104, 210, 58, "🤖", "AI / LLM APIs", "AI-powered features", "#A78BFA"),
        "ws": (686, 178, 210, 58, "⚡", "Realtime", "WebSockets", "#F59E0B"),
        "auth": (300, 314, 250, 58, "🔐", "Auth & roles", "JWT · guards · RBAC", "#F43F5E"),
        "doc": (686, 314, 210, 58, "📘", "API docs", "Swagger / OpenAPI", "#EC4899"),
    }
    edges = [("web", "svc"), ("mob", "svc"), ("adm", "svc"), ("svc", "db"), ("svc", "ai"), ("svc", "ws"),
             ("svc", "auth"), ("auth", "doc")]

    def anchor(k, side):
        x, y, w, h = nodes[k][:4]
        return {"r": (x + w, y + h / 2), "l": (x, y + h / 2), "b": (x + w / 2, y + h), "t": (x + w / 2, y)}[side]

    out = []
    for i, (a, b) in enumerate(edges):
        if a == "svc" and b == "auth":
            (x1, y1), (x2, y2) = anchor(a, "b"), anchor(b, "t")
            path = f"M{x1},{y1} L{x2},{y2}"
        else:
            (x1, y1), (x2, y2) = anchor(a, "r"), anchor(b, "l")
            mx = (x1 + x2) / 2
            path = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
        col = nodes[b][7]
        dur = 2.4 + (i % 3) * .4
        out.append(f'<path d="{path}" fill="none" stroke="#fff" stroke-opacity=".1" stroke-width="2"/>'
                   f'<path class="flow" style="animation-duration:{dur}s" d="{path}" fill="none" stroke="{col}" stroke-opacity=".75" stroke-width="2" stroke-dasharray="6 10"/>'
                   f'<circle r="4.5" fill="{col}"><animateMotion dur="{dur}s" begin="{-i * .37:.2f}s" repeatCount="indefinite" path="{path}"/></circle>')
    for k, (x, y, w, h, emo, title, sub, col) in nodes.items():
        big = k == "svc"
        d = -(hash(k) % 10) * .3
        out.append(f"""<g transform="translate({x} {y})"><g class="{"fl" if big else ""}" style="animation-delay:{d:.1f}s">
  {tile3d(w, h, col, 12, 5)}
  {'<rect class="ring" x="-4" y="-4" width="%d" height="%d" rx="15" fill="none" stroke="%s" stroke-width="2"/>' % (w + 8, h + 8, col) if big else ""}
  <text x="16" y="{h / 2 + (-6 if big else 7)}" font-size="{30 if big else 20}">{emo}</text>
  <text x="{58 if big else 48}" y="{h / 2 - (8 if big else 3)}" font-family="{SANS}" font-size="{18 if big else 14}" font-weight="700" fill="#f4f7fb">{e(title)}</text>
  <text x="{58 if big else 48}" y="{h / 2 + (14 if big else 15)}" font-family="{MONO}" font-size="{12 if big else 11}" fill="{col}">{e(sub)}</text>
  {f'<text x="16" y="{h - 16}" font-family="{SANS}" font-size="12" fill="#8b95ab">modules · DTO validation · services</text>' if big else ""}
</g></g>""")
    # deploy lane
    out.append(f"""<g transform="translate(24 404)">
  <rect width="872" height="44" rx="12" fill="#fff" fill-opacity=".04" stroke="#fff" stroke-opacity=".1" stroke-dasharray="4 6"/>
  <g font-family="{MONO}" font-size="12.5" fill="#a9b3c9">
    <text x="18" y="27"><tspan fill="{G}">⬢ </tspan>Git · code review</text>
    <text x="196" y="27">→</text>
    <text x="222" y="27"><tspan fill="#22D3EE">⚙ </tspan>CI/CD pipeline</text>
    <text x="386" y="27">→</text>
    <text x="412" y="27"><tspan fill="{IN}">🐳 </tspan>Docker + Nginx on Linux</text>
    <text x="664" y="27">→</text>
    <text x="690" y="27"><tspan fill="#F59E0B">🚀 </tspan>Web · stores · admin</text>
  </g>
</g>
<text x="24" y="{H - 2}" font-family="{SANS}" font-size="1" fill="none">.</text>""")
    write("architecture.svg", frame(W, H, "".join(out), """
  .flow { animation: flow 2.4s linear infinite; }
  @keyframes flow { to { stroke-dashoffset: -32; } }
  .ring { animation: ring 2.6s ease-in-out infinite; }
  @keyframes ring { 0%,100% { opacity: .15; } 50% { opacity: .8; } }"""))


# ---------------- project cards ----------------
PROJECTS = [
    ("orbex", "📈", "Orbex", "Forex & CFD trading app", "#F59E0B",
     "Mobile trading app for Orbex, an online forex and CFD broker, live on Google Play. I built the backend APIs and the Super Admin dashboard.",
     ["NestJS", "MySQL", "Next.js", "Mobile"]),
    ("tarteel", "📖", "Tarteel AI", "AI-powered Quran app", G,
     "Listens to a user's recitation, detects mistakes in real time and supports memorization. I built its APIs and admin dashboard.",
     ["NestJS", "MySQL", "AI", "Next.js"]),
    ("stockship", "📦", "Stockship", "End to end · AI features", "#3B82F6",
     "Built end to end: NestJS APIs, a responsive Next.js front-end, AI/LLM-powered features and the Super Admin dashboard.",
     ["NestJS", "Next.js", "AI/LLM", "MySQL"]),
    ("akfeek", "🧩", "Akfeek", "Platform backend & admin", "#EC4899",
     "Backend services and RESTful APIs for the platform, plus the Super Admin dashboard used to manage and monitor it.",
     ["NestJS", "MySQL", "REST", "Next.js"]),
    ("smootherp", "🏭", "SmoothERP", "ERP system · FiveM Tech", IN,
     "ERP for core business operations across multiple modules. I built backend services and REST APIs for its modules.",
     ["NestJS", "Prisma", "MySQL", "ERP"]),
    ("qr-attendance", "🎓", "QR Attendance", "Graduation project · A+", "#22D3EE",
     "Attendance by QR scanning plus an eLearning system: my graduation project at Modern Academy Maadi, graded A+ (Excellent).",
     ["QR scanning", "eLearning", "Full-stack"]),
]


NOT_LIVE = {"qr-attendance"}  # academic project, no public page


def projects(items=None, badge="LIVE"):
    W, H = 440, 230
    PAD, EDGE = 10, 9
    CW, CH = W, H + PAD + EDGE + 16
    for n, (slug, icon, name, kind, col, desc, tags) in enumerate(items or PROJECTS):
        dl_ = -(n * .55)
        dl = "".join(f'<text x="26" y="{112 + i * 22}">{e(l)}</text>' for i, l in enumerate(textwrap.wrap(desc, 56)[:4]))
        x, tg = 26, ""
        for t in tags:
            w = int(len(t) * 7.4 + 22)
            tg += f'<rect x="{x}" y="{H - 44}" width="{w}" height="24" rx="12" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".45"/><text x="{x + w / 2}" y="{H - 27.5}" text-anchor="middle">{e(t)}</text>'
            x += w + 8
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}">
<style>
  .fl {{ animation: fl 4.2s ease-in-out infinite; animation-delay: {dl_:.2f}s; }}
  @keyframes fl {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-{PAD}px); }} }}
  .sh {{ animation: sh 4.2s ease-in-out infinite; animation-delay: {dl_:.2f}s; transform-box: fill-box; transform-origin: center; }}
  @keyframes sh {{ 0%,100% {{ transform: scaleX(1); opacity: .45; }} 50% {{ transform: scaleX(.86); opacity: .2; }} }}
  .fp {{ animation: fp 9s cubic-bezier(.45,0,.2,1) infinite; animation-delay: {n * .7:.2f}s; transform-box: fill-box; transform-origin: center; }}
  @keyframes fp {{ 0%,78% {{ transform: scaleX(1) skewY(0); }} 83% {{ transform: scaleX(.02) skewY(-12deg); }} 88% {{ transform: scaleX(-1) skewY(0); }}
                   93% {{ transform: scaleX(.02) skewY(12deg); }} 98%,100% {{ transform: scaleX(1) skewY(0); }} }}
  .g {{ animation: pulse 4s ease-in-out infinite; }} @keyframes pulse {{ 0%,100% {{ opacity: .35; }} 50% {{ opacity: .6; }} }}
  .sw {{ animation: sw 7s ease-in-out infinite; animation-delay: {n * .9:.2f}s; }}
  @keyframes sw {{ 0%,70% {{ transform: translateX(-260px); }} 100% {{ transform: translateX({W + 260}px); }} }}
  .live {{ animation: live 1.6s ease-in-out infinite; }} @keyframes live {{ 50% {{ opacity: .25; }} }}
</style>
<defs>
  <linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#121c26"/><stop offset="1" stop-color="#0b1117"/></linearGradient>
  <radialGradient id="r" cx="1" cy="0" r="1"><stop offset="0" stop-color="{col}" stop-opacity=".5"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".45" stop-color="#fff" stop-opacity=".04"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="swg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="ed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{dark(col, .35)}"/><stop offset=".5" stop-color="{dark(col, .55)}"/><stop offset="1" stop-color="{dark(col, .3)}"/></linearGradient>
  <clipPath id="c"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16"/></clipPath>
  <filter id="bl" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
<ellipse class="sh" filter="url(#bl)" cx="{W / 2}" cy="{CH - 9}" rx="{W / 2 - 30}" ry="7" fill="{col}" opacity=".4"/>
<g class="fl"><g transform="translate(0 {PAD})">
  <rect x="0" y="{EDGE}" width="{W}" height="{H}" rx="16" fill="url(#ed)"/>
  <rect x="0" y="{EDGE / 2}" width="{W}" height="{H}" rx="16" fill="{dark(col, .45)}"/>
  <g clip-path="url(#c)">
    <rect width="{W}" height="{H}" fill="url(#b)"/>
    <rect class="g" width="{W}" height="{H}" fill="url(#r)"/>
    <rect width="{W}" height="4" fill="{col}"/>
    <rect class="sw" x="0" y="0" width="180" height="{H}" fill="url(#swg)" transform="skewX(-20)"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="#fff" stroke-opacity=".12"/>
  <g transform="translate(26 22)"><g class="fp">
    <rect x="0" y="6" width="48" height="48" rx="12" fill="{dark(col, .4)}"/>
    <rect x="0" y="3" width="48" height="48" rx="12" fill="{dark(col, .65)}"/>
    <rect width="48" height="48" rx="12" fill="#1a2430"/>
    <rect width="48" height="48" rx="12" fill="{col}" fill-opacity=".16"/>
    <text x="24" y="32" text-anchor="middle" font-size="23">{icon}</text>
    <rect width="48" height="48" rx="12" fill="url(#gl)"/>
    <rect x=".5" y=".5" width="47" height="47" rx="11.5" fill="none" stroke="{col}" stroke-opacity=".6"/>
  </g></g>
  <text x="88" y="46" font-family="{SANS}" font-size="19" font-weight="700" fill="#f4f7fb">{e(name)}</text>
  <text x="88" y="67" font-family="{MONO}" font-size="11.5" fill="{col}" letter-spacing=".4">{e(kind.upper())}</text>
  {"" if slug in NOT_LIVE else f'''<g transform="translate({W - 22 - (len(badge) * 7 + 30)} 26)"><rect width="{len(badge) * 7 + 30}" height="20" rx="10" fill="#10D59A" fill-opacity=".12" stroke="#10D59A" stroke-opacity=".5"/>
    <circle class="live" cx="12" cy="10" r="3.5" fill="#10D59A"/><text x="{(len(badge) * 7 + 30) / 2 + 6}" y="14" text-anchor="middle" font-family="{MONO}" font-size="10" font-weight="700" fill="#10D59A">{badge}</text></g>'''}
  <g font-family="{SANS}" font-size="14" fill="#a9b3c9">{dl}</g>
  <g font-family="{SANS}" font-size="11.5" font-weight="600" fill="#e5e7eb">{tg}</g>
</g></g>
</svg>"""
        write(f"projects/{slug}.svg", svg)


# ---------------- tech stack ----------------
TILE = "#1f2833"


def sk(name, pfx):
    s = (ICONS / f"sk_{name}.svg").read_text(encoding="utf-8")
    inner = re.search(r"<g transform=\"translate\(0, 0\)\">\s*(<svg.*</svg>)\s*</g>", s, re.S).group(1)
    for i in set(re.findall(r'id="([^"]+)"', inner)):
        inner = inner.replace(f'id="{i}"', f'id="{pfx}{i}"').replace(f"url(#{i})", f"url(#{pfx}{i})").replace(f'href="#{i}"', f'href="#{pfx}{i}"')
    head, rest = inner.strip().split(">", 1)
    head = re.sub(r'\s(width|height)="[^"]*"', "", head)
    return head.replace("<svg", '<svg x="0" y="0" width="72" height="72"', 1) + ">" + rest


def si(name, color):
    s = (ICONS / f"si_{name}.svg").read_text(encoding="utf-8")
    d = re.search(r'<path d="([^"]+)"', s).group(1)
    tf = "translate(22 22) scale(8.833)" if name == "filament" else "translate(60 60) scale(5.667)"  # filament's path is 24px-wide art
    return (f'<svg x="0" y="0" width="72" height="72" viewBox="0 0 256 256"><rect width="256" height="256" rx="60" fill="{TILE}"/>'
            f'<path transform="{tf}" fill="{color}" d="{d}"/></svg>')


STACK = [
    ("Backend", "⚙️", [("Node.js", "sk", "nodejs", "#5FA04E"), ("NestJS", "sk", "nestjs", "#E0234E"), ("Express", "si", "express", "#E6EDF3"),
                       ("TypeScript", "sk", "ts", "#3178C6"), ("JavaScript", "sk", "js", "#F0DB4F"), ("C#", "sk", "cs", "#9B4F96"),
                       (".NET", "si", "dotnet", "#9B6FE0")]),
    ("Frontend", "🎨", [("React", "sk", "react", "#61DAFB"), ("Next.js", "sk", "nextjs", "#E6EDF3"), ("Angular", "sk", "angular", "#DD0031"),
                        ("Tailwind", "sk", "tailwind", "#38BDF8"), ("Bootstrap", "sk", "bootstrap", "#7952B3"), ("HTML", "sk", "html", "#E34F26"),
                        ("CSS", "sk", "css", "#1572B6")]),
    ("Data", "🗄️", [("MySQL", "sk", "mysql", "#4479A1"), ("PostgreSQL", "sk", "postgres", "#4169E1"), ("MongoDB", "sk", "mongodb", "#47A248"),
                    ("Prisma", "si", "prisma", "#E6EDF3"), ("TypeORM", "si", "typeorm", "#FE0803")]),
    ("APIs & AI", "🔌", [("GraphQL", "sk", "graphql", "#E10098"), ("Socket.io", "si", "socketdotio", "#E6EDF3"), ("Swagger", "si", "swagger", "#85EA2D"),
                         ("JWT", "si", "jsonwebtokens", "#D63AFF"), ("OpenAI / LLM", "si", "openai", "#E6EDF3")]),
    ("DevOps", "☁️", [("Docker", "sk", "docker", "#2496ED"), ("Nginx", "sk", "nginx", "#009639"), ("Linux", "sk", "linux", "#FCC624"),
                      ("GitHub Actions", "si", "githubactions", "#2088FF"), ("AWS", "sk", "aws", "#FF9900"), ("Vercel", "si", "vercel", "#E6EDF3")]),
    ("Workflow", "🧰", [("Git", "sk", "git", "#F05032"), ("GitHub", "sk", "github", "#E6EDF3"), ("GitLab", "si", "gitlab", "#FC6D26"),
                        ("Jira", "si", "jira", "#2684FF"), ("Postman", "sk", "postman", "#FF6C37"), ("VS Code", "sk", "vscode", "#23A9F2")]),
]


def tech():
    W, LBL, X0, STEP, ROWH, TOP = 920, 170, 196, 100, 128, 30
    H = TOP + ROWH * len(STACK) + 10
    out = []
    for r, (cat, emo, items) in enumerate(STACK):
        y = TOP + r * ROWH
        if r:
            out.append(f'<line x1="24" x2="{W - 24}" y1="{y - 10}" y2="{y - 10}" stroke="#fff" stroke-opacity=".06"/>')
        out.append(f'<g transform="translate(24 {y + 20})"><rect width="{LBL - 20}" height="40" rx="20" fill="{G}" fill-opacity=".1" stroke="{G}" stroke-opacity=".45"/>'
                   f'<text x="{(LBL - 20) / 2}" y="26" text-anchor="middle" font-family="{SANS}" font-size="15" font-weight="700" fill="#d7fbe9">{emo} {e(cat)}</text></g>')
        for c, (name, src, key, col) in enumerate(items):
            x, d = X0 + c * STEP, r * .35 + c * .22
            icon = sk(key, f"t{r}{c}_") if src == "sk" else si(key, col)
            out.append(f'''<g transform="translate({x} {y})">
  <ellipse class="sh" style="animation-delay:-{d:.2f}s" cx="36" cy="92" rx="30" ry="5" fill="{col}" opacity=".35"/>
  <g class="fl" style="animation-delay:-{d:.2f}s"><g class="fp" style="animation-delay:{d * 1.6:.2f}s">
    <rect x="0" y="7" width="72" height="72" rx="17" fill="{dark(col, .45)}"/>
    <rect x="0" y="3.5" width="72" height="72" rx="17" fill="{dark(col, .7)}"/>
    {icon}
    <rect width="72" height="72" rx="17" fill="url(#gloss)"/>
    <rect x=".5" y=".5" width="71" height="71" rx="16.5" fill="none" stroke="{col}" stroke-opacity=".55"/>
  </g></g>
  <text x="36" y="112" text-anchor="middle" font-family="{SANS}" font-size="11.5" font-weight="600" fill="#9aa4bb">{name}</text>
</g>''')
    write("tech-stack.svg", frame(W, H, "".join(out)))


# ---------------- current company ----------------
COMPANY_LIVE = ["Orbex", "Tarteel AI", "Stockship", "Akfeek"]


def company():
    W, H = 920, 318
    stats = [("🚢", "4", "platforms shipped"), ("🧩", "3", "layers: API · web · admin"), ("🤖", "AI", "LLM features in production")]
    out = [f"""<g class="up">
  <text x="36" y="62" font-family="{SANS}" font-size="46" font-weight="800" fill="#f4f7fb" letter-spacing="-1">Qeema<tspan fill="{PV}">Tech</tspan></text>
  <text x="36" y="92" font-family="{MONO}" font-size="13" fill="{PV}" letter-spacing="1.5">CURRENTLY · SINCE JAN 2026</text>
  <rect x="36" y="110" width="200" height="30" rx="15" fill="{PV}" fill-opacity=".2" stroke="{PV}" stroke-opacity=".7"/>
  <text x="136" y="130" text-anchor="middle" font-family="{SANS}" font-size="13.5" font-weight="700" fill="#e6e3ff">Technical Team Lead</text>
  <g font-family="{SANS}" font-size="14" fill="#a9b3c9">
    <text x="36" y="172">Leading the dev team: planning tasks, reviewing</text>
    <text x="36" y="194">code and owning architecture, while still shipping</text>
    <text x="36" y="216">APIs, web apps and dashboards hands-on.</text>
  </g>
</g>"""]
    for i, (emo, num, label) in enumerate(stats):
        x, y = 470, 28 + i * 64
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{-i * .4:.1f}s">
  {tile3d(414, 50, PV, 12, 5)}
  <text x="18" y="33" font-size="20">{emo}</text>
  <text x="56" y="35" font-family="{SANS}" font-size="24" font-weight="800" fill="#f4f7fb">{num}</text>
  <text x="{56 + len(num) * 16 + 12}" y="33" font-family="{SANS}" font-size="14.5" fill="#c9c5ff">{label}</text>
</g></g>""")
    # ticker of live products
    chips, x = "", 0
    for name in COMPANY_LIVE * 4:
        w = int(len(name) * 8 + 44)
        chips += (f'<rect x="{x}" width="{w}" height="30" rx="15" fill="#fff" fill-opacity=".05" stroke="{PV}" stroke-opacity=".45"/>'
                  f'<circle class="live" cx="{x + 16}" cy="15" r="4" fill="{G}"/><text x="{x + 28}" y="20" font-family="{SANS}" font-size="13" font-weight="600" fill="#e5e7eb">{e(name)}</text>')
        x += w + 10
    half = x / 2
    out.append(f"""<text x="36" y="{H - 52}" font-family="{MONO}" font-size="11.5" fill="#8b95ab" letter-spacing="1">LIVE IN PRODUCTION</text>
<svg x="200" y="{H - 72}" width="{W - 236}" height="34"><g class="tk">{chips}</g></svg>""")
    write("company.svg", frame(W, H, "".join(out), f"""
  .tk {{ animation: tk 26s linear infinite; }} @keyframes tk {{ to {{ transform: translateX(-{half:.0f}px); }} }}
  .live {{ animation: lv 1.6s ease-in-out infinite; }} @keyframes lv {{ 50% {{ opacity: .25; }} }}""",
        f'<radialGradient id="pv"><stop offset="0" stop-color="{PV}" stop-opacity=".5"/><stop offset="1" stop-color="{PV}" stop-opacity="0"/></radialGradient>').replace(
        'fill="url(#o2)"', 'fill="url(#pv)"', 1))


# ---------------- divider + footer ----------------
def divider():
    write("divider.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="6" viewBox="0 0 1200 6">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{G}" stop-opacity="0"/><stop offset=".5" stop-color="{G}"/><stop offset=".75" stop-color="{IN}"/><stop offset="1" stop-color="{IN}" stop-opacity="0"/></linearGradient></defs>
<rect width="1200" height="6" rx="3" fill="url(#g)"/></svg>''')


def footer():
    W, H = 1200, 170
    wave = lambda y, a: f"M0 {y} C300 {y - a} 600 {y + a} 900 {y} S1200 {y - a} 1500 {y} V{H} H0Z"
    write("footer.svg", f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.w{{animation:w 8s ease-in-out infinite alternate}}.w2{{animation-duration:11s;animation-delay:-3s}}
@keyframes w{{from{{transform:translateX(0)}}to{{transform:translateX(-300px)}}}}
.t{{animation:t 3s ease-in-out infinite}}@keyframes t{{50%{{opacity:.75}}}}</style>
<defs><linearGradient id="a" x1="0" x2="1"><stop offset="0" stop-color="{G}"/><stop offset="1" stop-color="{IN}"/></linearGradient></defs>
<path class="w w2" d="{wave(70, 40)}" fill="url(#a)" opacity=".35"/>
<path class="w" d="{wave(88, 30)}" fill="url(#a)"/>
<text class="t" x="600" y="140" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="800" fill="#fff">Let’s build something reliable together</text>
</svg>''')


# ---------------- developer ID card (photo embedded, GitHub blocks external images in SVG) ----------------
def idcard():
    import base64, io
    from PIL import Image
    im = Image.open(A / "profile.jpg").convert("RGB").resize((360, 360), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=84, optimize=True)
    photo = base64.b64encode(buf.getvalue()).decode()
    W, H, cx, cy, r = 360, 544, 180, 196, 112
    rows = [("BASE", "Cairo, Egypt"), ("STACK", "NestJS · Next.js"), ("XP", "4+ years · since 2021"), ("LANG", "Arabic · English B1+")]
    info = "".join(f'<text x="34" y="{410 + k * 24}"><tspan fill="#5b6478">{e(k_)}</tspan><tspan x="112" fill="#e5e7eb">{e(v)}</tspan></text>'
                   for k, (k_, v) in enumerate(rows))
    bars = "".join(f'<rect x="{34 + k * 6}" y="{H - 34}" width="{2 if (k * 7) % 3 else 4}" height="16" fill="#fff" fill-opacity=".35"/>' for k in range(22))
    body = f"""
  <text x="26" y="40" font-family="{MONO}" font-size="12" fill="#8b95ab" letter-spacing="1.5">DEV_ID // AR-2021</text>
  <circle class="live" cx="{W - 96}" cy="36" r="4.5" fill="{G}"/>
  <text x="{W - 84}" y="40" font-family="{MONO}" font-size="12" font-weight="700" fill="{G}" letter-spacing="1">ONLINE</text>
  <circle class="spin" cx="{cx}" cy="{cy}" r="{r + 14}" fill="none" stroke="url(#ac)" stroke-width="3" stroke-dasharray="120 40 18 40" stroke-linecap="round"/>
  <circle class="spin rev" cx="{cx}" cy="{cy}" r="{r + 24}" fill="none" stroke="{IN}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="2 9"/>
  <circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="#0b1117" stroke="#fff" stroke-opacity=".12"/>
  <clipPath id="ph"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  <g clip-path="url(#ph)">
    <image x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" href="data:image/jpeg;base64,{photo}" xlink:href="data:image/jpeg;base64,{photo}"/>
    <rect class="pscan" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="40" fill="url(#scan)"/>
  </g>
  <text x="{cx}" y="{cy + r + 62}" text-anchor="middle" font-family="{SANS}" font-size="28" font-weight="800" fill="#f4f7fb">Ahmed Raouf</text>
  <text x="{cx}" y="{cy + r + 86}" text-anchor="middle" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{G}" letter-spacing="2">TECHNICAL TEAM LEAD</text>
  <line x1="34" x2="{W - 34}" y1="{cy + r + 102}" y2="{cy + r + 102}" stroke="#fff" stroke-opacity=".08"/>
  <g font-family="{MONO}" font-size="12.5">{info}</g>
  {bars}
  <text x="{W - 34}" y="{H - 21}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5b6478">@Ahmed-Raouf-Metwally</text>"""
    write("id-card.svg", frame(W, H, body, f"""
  .spin {{ animation: spin 14s linear infinite; transform-origin: {cx}px {cy}px; }} .rev {{ animation-duration: 22s; animation-direction: reverse; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .pscan {{ animation: ps 3.5s ease-in-out infinite alternate; }} @keyframes ps {{ from {{ transform: translateY(0); }} to {{ transform: translateY({2 * r - 40}px); }} }}
  .live {{ animation: lv 1.6s ease-in-out infinite; }} @keyframes lv {{ 50% {{ opacity: .25; }} }}"""))


# ---------------- "query me" API card ----------------
def api():
    W = 920
    K, S, N, P, T = "#61afef", "#98c379", "#d19a66", "#c678dd", "#a9b3c9"

    def arr(items):
        return [(T, "[")] + sum(([(S, f'"{x}"')] + ([(T, ", ")] if i < len(items) - 1 else []) for i, x in enumerate(items)), []) + [(T, "]")]

    def kv(ind, k, v, comma=True):
        return [(T, "  " * ind), (K, f'"{k}"'), (T, ": ")] + v + ([(T, ",")] if comma else [])

    lines = [
        [(T, "{")],
        kv(1, "name", [(S, '"Ahmed Raouf"')]),
        kv(1, "role", [(S, '"Technical Team Lead"')]),
        kv(1, "company", [(S, '"QeemaTech"')]),
        kv(1, "location", [(S, '"Cairo, Egypt"')]),
        kv(1, "experience_years", [(N, "4")]),
        kv(1, "stack", [(T, "{")], False),
        kv(2, "backend", arr(["Node.js", "NestJS", "Express", "TypeScript"])),
        kv(2, "frontend", arr(["React", "Next.js", "Angular"])),
        kv(2, "data", arr(["MySQL", "PostgreSQL", "Prisma", "TypeORM"]), False),
        [(T, "  },")],
        kv(1, "shipped", arr(["Orbex", "Tarteel AI", "Stockship", "Akfeek"])),
        kv(1, "ai_features", [(P, "true")]),
        kv(1, "open_to_collab", [(P, "true")], False),
        [(T, "}")],
    ]
    n = len(lines)
    jx, jy, lh = 344, 112, 21
    H = jy + n * lh + 34
    cyc = 14
    css = "".join(f".j{i} {{ animation: j{i} {cyc}s steps(1) infinite; }} @keyframes j{i} {{ 0%,74% {{ opacity: 1; }} 75% {{ opacity: 0; }} {77 + i * 1.4:.1f}%,100% {{ opacity: 1; }} }}\n"
                  for i in range(n))
    js = "".join(f'<text class="j{i}" x="{jx}" y="{jy + i * lh}" xml:space="preserve"><tspan fill="#3f4a56">{i + 1:>2}  </tspan>'
                 + "".join(f'<tspan fill="{c}">{e(t)}</tspan>' for c, t in ln) + "</text>" for i, ln in enumerate(lines))
    # latency sparkline
    pts = [18, 26, 14, 30, 22, 12, 24, 16, 28, 11, 20, 15, 25, 13]
    spark = " ".join(f"{24 + k * 19},{H - 60 - v}" for k, v in enumerate(pts))
    left = f"""
  <text x="24" y="40" font-family="{MONO}" font-size="12" fill="#8b95ab" letter-spacing="1.5">REQUEST</text>
  <rect x="24" y="54" width="46" height="24" rx="6" fill="{G}" fill-opacity=".18" stroke="{G}" stroke-opacity=".6"/>
  <text x="47" y="71" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="{G}">GET</text>
  <text x="80" y="71" font-family="{MONO}" font-size="12.5" fill="#e5e7eb">/v1/engineers/ahmed</text>
  <g font-family="{MONO}" font-size="11.5" fill="#8b95ab">
    <text x="24" y="104"><tspan fill="{K}">Host</tspan>: localhost:3000</text>
    <text x="24" y="124"><tspan fill="{K}">Accept</tspan>: application/json</text>
    <text x="24" y="144"><tspan fill="{K}">Authorization</tspan>: Bearer ••••••</text>
  </g>
  <line x1="24" x2="300" y1="168" y2="168" stroke="#fff" stroke-opacity=".08"/>
  <text x="24" y="196" font-family="{MONO}" font-size="12" fill="#8b95ab" letter-spacing="1.5">RESPONSE</text>
  <rect x="24" y="210" width="86" height="26" rx="13" fill="{G}" fill-opacity=".15" stroke="{G}" stroke-opacity=".6"/>
  <circle class="live" cx="40" cy="223" r="4" fill="{G}"/>
  <text x="52" y="228" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{G}">200 OK</text>
  <g font-family="{MONO}" font-size="12" fill="#a9b3c9">
    <text x="24" y="266">time  <tspan fill="#f4f7fb">42 ms</tspan></text>
    <text x="24" y="288">size  <tspan fill="#f4f7fb">0.6 kB</tspan></text>
    <text x="24" y="310">type  <tspan fill="#f4f7fb">application/json</tspan></text>
  </g>
  <text x="24" y="{H - 104}" font-family="{MONO}" font-size="11" fill="#5b6478" letter-spacing="1">LATENCY · p95 &lt; 50 ms</text>
  <polyline points="{spark}" fill="none" stroke="{G}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
  <circle r="4" fill="#f4f7fb" stroke="{G}" stroke-width="2"><animateMotion dur="5s" repeatCount="indefinite" path="M{spark.replace(" ", " L")}"/></circle>
  <line x1="24" x2="{24 + 13 * 19}" y1="{H - 60}" y2="{H - 60}" stroke="#fff" stroke-opacity=".08"/>"""
    right = f"""
  <rect x="{jx - 24}" y="24" width="{W - jx}" height="{H - 48}" rx="14" fill="#0b1117" fill-opacity=".85" stroke="#fff" stroke-opacity=".1"/>
  <path d="M{jx - 23.5},38 a14 14 0 0 1 14-14 h{W - jx - 29} a14 14 0 0 1 14 14 V64 H{jx - 23.5}z" fill="#121a22"/>
  <circle cx="{jx - 2}" cy="44" r="6" fill="#ff5f57"/><circle cx="{jx + 18}" cy="44" r="6" fill="#febc2e"/><circle cx="{jx + 38}" cy="44" r="6" fill="#28c840"/>
  <text x="{W - 40}" y="49" text-anchor="end" font-family="{MONO}" font-size="12" fill="#6b7280">$ curl -s localhost:3000/v1/engineers/ahmed | jq</text>
  <g font-family="{MONO}" font-size="13">{js}</g>
  <rect class="cur" x="{jx + 30}" y="{jy + (n - 1) * lh + 8}" width="8" height="15" fill="{G}"/>"""
    write("api.svg", frame(W, H, left + right, f"""
  {css}
  .cur {{ animation: blink 1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .live {{ animation: lv 1.6s ease-in-out infinite; }} @keyframes lv {{ 50% {{ opacity: .25; }} }}"""))


# ---------------- learning & certifications ----------------
LEARNING = [
    ("🎓", "B.Sc. Computer Science", "Modern Academy Maadi", "2018 – 2022", G,
     ["Faculty of Computing & Information", "Graduation project graded A+"]),
    ("🧩", "MEAN Stack Diploma", "Route IT Training Center", "2021 – 2022", "#F43F5E",
     ["MongoDB · Express · Angular · Node.js", "Where the backend journey started"]),
    ("🔁", "Scrum Product Owner", "O'Reilly", "2024", IN,
     ["Backlogs, priorities, Agile delivery", "Paired with Scrum Master work"]),
    ("🏅", "MEAN Stack Scholarship", "Orange Digital Center × AMIT", "2024", "#F59E0B",
     ["96 hours of hands-on training", "Finished with a 95% grade"]),
]


def learning():
    W, cols, cw, ch, gx, gy, x0, y0 = 920, 2, 425, 142, 22, 30, 24, 26
    rows = (len(LEARNING) + cols - 1) // cols
    H = y0 + rows * (ch + gy) + 2
    out = []
    for i, (emo, title, org, when, col, pts) in enumerate(LEARNING):
        r, c = divmod(i, cols)
        x, y, d = x0 + c * (cw + gx), y0 + r * (ch + gy), -(r * .5 + c * .35)
        cw_ = int(len(when) * 7.6 + 24)
        bl = "".join(f'<text x="22" y="{96 + k * 22}"><tspan fill="{col}">▸ </tspan>{e(t)}</text>' for k, t in enumerate(pts))
        out.append(f"""<g transform="translate({x} {y})">
  <ellipse class="sh" style="animation-delay:{d:.2f}s" cx="{cw / 2}" cy="{ch + 16}" rx="{cw / 2 - 30}" ry="5" fill="{col}" filter="url(#bl)"/>
  <g class="fl" style="animation-delay:{d:.2f}s">
    {tile3d(cw, ch, col, 16, 7)}
    <g transform="translate(22 18)">{icon_tile(emo, col, 44, i * .8)}</g>
    <text x="80" y="38" font-family="{SANS}" font-size="17" font-weight="700" fill="#f4f7fb">{e(title)}</text>
    <text x="80" y="60" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{col}">{e(org.upper())}</text>
    <rect x="{cw - 20 - cw_}" y="20" width="{cw_}" height="24" rx="12" fill="{col}" fill-opacity=".14" stroke="{col}" stroke-opacity=".5"/>
    <text x="{cw - 20 - cw_ / 2}" y="36.5" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="#e5e7eb">{e(when)}</text>
    <g font-family="{SANS}" font-size="13" fill="#a9b3c9">{bl}</g>
  </g>
</g>""")
    write("learning.svg", frame(W, H, "".join(out)))


# ---------------- section titles ----------------
TITLES = [  # slug, english, arabic
    ("about", "About Me", "نبذة عني"),
    ("api", "Query Me", "استعلم عني"),
    ("company", "Currently @ QeemaTech", "حاليًا في QeemaTech"),
    ("services", "What I Bring", "ما أقدمه"),
    ("career", "Career Path", "المسار المهني"),
    ("architecture", "How I Build a Platform", "إزاي بابني منصة"),
    ("work", "Selected Work", "أعمال مختارة"),
    ("stack", "Tech Stack", "التقنيات"),
    ("learning", "Learning & Certifications", "التعليم والشهادات"),
    ("analytics", "GitHub Analytics", "إحصائيات GitHub"),
    ("music", "Coding Soundtrack", "بسمع إيه وأنا بكود"),
    ("snake", "Contribution Flow", "المساهمات"),
]


def titles():
    (A / "titles").mkdir(exist_ok=True)
    W, H = 920, 64
    line = (f'<linearGradient id="tl" gradientUnits="userSpaceOnUse" x1="28" x2="{W - 28}"><stop offset="0" stop-color="{G}" stop-opacity=".9"/>'
            f'<stop offset=".6" stop-color="{IN}" stop-opacity=".6"/><stop offset="1" stop-color="{IN}" stop-opacity="0"/></linearGradient>')
    for n, (slug, en, ar) in enumerate(TITLES, 1):
        num = f"0x{n:02X}"
        for lang, text in (("en", en), ("ar", ar)):
            rtl = lang == "ar"
            if rtl:  # in an rtl run, "start" is the right edge
                label = (f'<text x="{W - 30}" y="38" direction="rtl" text-anchor="start" font-family="{SANS}" font-size="24" font-weight="800" fill="#f4f7fb">{e(text)}</text>'
                         f'<text x="30" y="37" font-family="{MONO}" font-size="12" fill="#5b6478" letter-spacing="1"><tspan fill="{G}">{num}</tspan> // section_{n:02d}</text>')
                path, grad = f"M{W - 28},52 H28", line.replace('x1="28" x2="%d"' % (W - 28), 'x1="%d" x2="28"' % (W - 28))
            else:
                label = (f'<text x="30" y="38" font-family="{SANS}" font-size="24" font-weight="800" fill="#f4f7fb">'
                         f'<tspan font-family="{MONO}" font-size="14" font-weight="400" fill="{G}">// {num}  </tspan>{e(text)}<tspan class="cur" fill="{G}"> ▍</tspan></text>'
                         f'<text x="{W - 30}" y="37" text-anchor="end" font-family="{MONO}" font-size="12" fill="#5b6478" letter-spacing="1">section_{n:02d}</text>')
                path, grad = f"M28,52 H{W - 28}", line
            body = f"""{label}
  <path d="{path}" stroke="url(#tl)" stroke-width="2"/>
  <circle r="3" fill="{G}"><animateMotion dur="4s" repeatCount="indefinite" path="{path}"/></circle>"""
            svg = frame(W, H, body, """
  .cur { animation: blink 1s steps(1) infinite; } @keyframes blink { 50% { opacity: 0; } }""", grad)
            svg = svg.replace(hud(W, H), hud(W, H, 6, 12))  # tighter brackets on the slim bar
            write(f"titles/{lang}-{slug}.svg", svg)


if __name__ == "__main__":
    for f in (header, company, impact, about, idcard, api, learning, titles, services, career, architecture, projects, tech, divider, footer):
        f()
    print("assets built:", sorted(p.name for p in A.rglob("*.svg")))
