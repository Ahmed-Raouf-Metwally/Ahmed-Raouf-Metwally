"""Coding-activity card from my public WakaTime stats (no key needed while the profile is public).

Projects and AI/category breakdowns are deliberately left out: client project names stay private.
"""
import json, urllib.request
from datetime import datetime, timezone

from build import A, SANS, MONO, G, IN, frame, dark, e

USER = "ahmedRaouf"
LANG_COL = {"TypeScript": "#3178C6", "JavaScript": "#F1E05A", "Bash": "#89E051", "JSON": "#F59E0B", "Markdown": "#A78BFA",
            "Python": "#3572A5", "C#": "#178600", "HTML": "#E34C26", "CSS": "#663399", "SQL": "#E38C00", "Prisma": "#5A67D8"}


def fetch():
    req = urllib.request.Request(f"https://wakatime.com/api/v1/users/{USER}/stats", headers={"User-Agent": USER})
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]


def hm(sec):
    h, m = divmod(int(sec) // 60, 60)
    return f"{h}h {m:02d}m" if h < 100 else f"{h}h"


def render(d):
    W, H = 920, 250
    langs = [l for l in d.get("languages", []) if l["name"] != "Other"][:5]
    other = 100 - sum(l["percent"] for l in langs)
    parts = [(l["name"], l["percent"]) for l in langs] + ([("Other", other)] if other > .05 else [])
    editors = [x for x in d.get("editors", []) if x["percent"] >= 1][:4]
    rng = d.get("range", "last_year").replace("_", " ")

    tiles = [("⏱️", hm(d["total_seconds"]), f"coded · {rng}", G),
             ("📅", hm(d["daily_average"]), "daily average", IN),
             ("🧠", str(len(d.get("languages", []))), "languages touched", "#F59E0B")]
    out = []
    for i, (emo, num, label, col) in enumerate(tiles):
        x, y, w, h, dl = 28, 26 + i * 68, 250, 56, -(i * .4)
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{dl:.1f}s">
  <rect y="6" width="{w}" height="{h}" rx="14" fill="{dark(col, .35)}"/>
  <rect width="{w}" height="{h}" rx="14" fill="url(#face)"/>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="none" stroke="{col}" stroke-opacity=".45"/>
  <rect width="{w}" height="{h}" rx="14" fill="url(#gloss)"/>
  <text x="20" y="37" font-size="22">{emo}</text>
  <text x="58" y="38" font-family="{SANS}" font-size="24" font-weight="800" fill="#f4f7fb">{e(num)}</text>
  <text x="{58 + len(num) * 13.5 + 10}" y="37" font-family="{SANS}" font-size="13.5" fill="#a9b3c9">{e(label)}</text>
</g></g>""")

    bx, by, bw, bh = 310, 70, 580, 26
    x, seg = bx, []
    for k, v in parts:
        w = bw * v / 100
        col = LANG_COL.get(k, "#6b7280")
        seg.append(f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{col}"/>'
                   f'<rect x="{x:.1f}" y="{by + bh}" width="{w:.1f}" height="8" fill="{dark(col, .45)}"/>')
        x += w
    legend = "".join(
        f'<g transform="translate({bx + (i % 3) * 195} {by + 66 + (i // 3) * 30})"><rect width="14" height="14" y="-12" rx="4" fill="{LANG_COL.get(k, "#6b7280")}"/>'
        f'<text x="22" font-family="{SANS}" font-size="14" font-weight="600" fill="#e5e7eb">{e(k)}</text>'
        f'<text x="176" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="#8b95ab">{v:.1f}%</text></g>'
        for i, (k, v) in enumerate(parts))
    chips, cx = "", bx + 84
    for ed in editors:
        label = f'{ed["name"]} {ed["percent"]:.0f}%'
        w = int(len(label) * 7.2 + 26)
        chips += (f'<rect x="{cx}" y="{H - 52}" width="{w}" height="26" rx="13" fill="{IN}" fill-opacity=".14" stroke="{IN}" stroke-opacity=".5"/>'
                  f'<text x="{cx + w / 2}" y="{H - 34.5}" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="#e5e7eb">{e(label)}</text>')
        cx += w + 8
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    out.append(f"""<text x="{bx}" y="48" font-family="{SANS}" font-size="16" font-weight="700" fill="#f4f7fb">Where the hours went <tspan font-weight="400" fill="#8b95ab" font-size="13">(WakaTime · {e(rng)})</tspan></text>
<defs><clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="{bh + 8}" rx="10"/></clipPath></defs>
<g class="fl" style="animation-delay:-1s"><g clip-path="url(#bar)">{"".join(seg)}<rect x="{bx}" y="{by}" width="{bw}" height="{bh / 2}" fill="#fff" fill-opacity=".14"/></g></g>
{legend}
<text x="{bx}" y="{H - 34}" font-family="{MONO}" font-size="11" fill="#5b6478" letter-spacing="1">EDITORS</text>
{chips}
<text x="{W - 28}" y="22" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="#5b6478">updated {stamp}</text>""")
    (A / "coding.svg").write_text(frame(W, H, "".join(out)), encoding="utf-8")


if __name__ == "__main__":
    render(fetch())
