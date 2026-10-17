"""Streak + contribution heatmap card, read from the public contribution calendar (no token needed).

Private contributions are counted too if "Include private contributions on my profile" is enabled on GitHub.
"""
import html as h, re, urllib.request
from datetime import date, datetime, timedelta, timezone

from build import A, SANS, MONO, G, IN, frame, dark, e

USER = "Ahmed-Raouf-Metwally"


def fetch():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": USER})
    with urllib.request.urlopen(req) as r:
        page = r.read().decode("utf-8")
    cells = {m["id"]: (date.fromisoformat(m["d"]), int(m["lvl"]))
             for m in re.finditer(r'<td[^>]*data-date="(?P<d>[\d-]+)"[^>]*id="(?P<id>[^"]+)"[^>]*data-level="(?P<lvl>\d)"', page)}
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        if m[1] in cells:
            n = re.match(r"([\d,]+)", h.unescape(m[2]))
            counts[m[1]] = int(n[1].replace(",", "")) if n else 0
    return sorted((d, counts.get(i, 0), lvl) for i, (d, lvl) in cells.items())


def streaks(days):
    today = datetime.now(timezone.utc).date()
    by = {d: c for d, c, _ in days}
    cur, d = 0, today if by.get(today, 0) else today - timedelta(days=1)  # today isn't over yet
    while by.get(d, 0):
        cur, d = cur + 1, d - timedelta(days=1)
    best = run = 0
    best_end = None
    for d, c, _ in days:
        run = run + 1 if c else 0
        if run > best:
            best, best_end = run, d
    return cur, best, best_end


def render(days):
    W, H = 920, 250
    total = sum(c for _, c, _ in days)
    cur, best, best_end = streaks(days)
    active = sum(1 for _, c, _ in days if c)
    tiles = [("🔥", str(cur), "day streak", "#F43F5E"),
             ("🏆", str(best), "longest streak", "#F59E0B"),
             ("📈", f"{total:,}", "contributions", G)]
    out = []
    for i, (emo, num, label, col) in enumerate(tiles):
        x, y, w, hh, dl = 28, 26 + i * 68, 250, 56, -(i * .4)
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{dl:.1f}s">
  <rect y="6" width="{w}" height="{hh}" rx="14" fill="{dark(col, .35)}"/>
  <rect width="{w}" height="{hh}" rx="14" fill="url(#face)"/>
  <rect x=".5" y=".5" width="{w - 1}" height="{hh - 1}" rx="13.5" fill="none" stroke="{col}" stroke-opacity=".45"/>
  <rect width="{w}" height="{hh}" rx="14" fill="url(#gloss)"/>
  <text x="20" y="37" font-size="22">{emo}</text>
  <text x="58" y="38" font-family="{SANS}" font-size="24" font-weight="800" fill="#f4f7fb">{e(num)}</text>
  <text x="{58 + len(num) * 13.5 + 10}" y="37" font-family="{SANS}" font-size="13.5" fill="#a9b3c9">{e(label)}</text>
</g></g>""")

    lv = ["#1a2430", dark(G, .32), dark(G, .5), dark(G, .75), G]
    x0, y0, step, sz = 318, 76, 10.6, 8.6
    first = days[0][0]
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # weeks start on Sunday, like GitHub
    cells, months, seen = [], [], set()
    for d, c, lvl in days:
        wk, dow = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = x0 + wk * step, y0 + dow * step
        cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sz}" height="{sz}" rx="2" fill="{lv[lvl]}"/>')
        if d.day <= 7 and dow == 0 and (d.year, d.month) not in seen:
            seen.add((d.year, d.month))
            months.append(f'<text x="{x:.1f}" y="{y0 - 10}">{d.strftime("%b")}</text>')
    weeks = (days[-1][0] - start).days // 7 + 1
    gw = weeks * step
    legend = "".join(f'<rect x="{x0 + gw - 5 * step + k * step - 2:.1f}" y="{y0 + 7 * step + 14}" width="{sz}" height="{sz}" rx="2" fill="{c}"/>' for k, c in enumerate(lv))
    best_txt = f"longest run ended {best_end.strftime('%d %b %Y')}" if best_end else ""
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    out.append(f"""<text x="{x0}" y="44" font-family="{SANS}" font-size="16" font-weight="700" fill="#f4f7fb">Contribution heatmap <tspan font-weight="400" fill="#8b95ab" font-size="13">({active} active days)</tspan></text>
<g font-family="{MONO}" font-size="10.5" fill="#8b95ab">{"".join(months)}</g>
{"".join(cells)}
<rect class="sweep" x="{x0 - 4}" y="{y0 - 4}" width="{step * 2}" height="{7 * step + 6}" rx="4" fill="{G}" fill-opacity=".12"/>
<text x="{x0}" y="{y0 + 7 * step + 22}" font-family="{MONO}" font-size="11" fill="#5b6478">{e(best_txt)}</text>
<text x="{x0 + gw - 5 * step - 10}" y="{y0 + 7 * step + 22}" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="#5b6478">less</text>{legend}
<text x="{x0 + gw + 2}" y="{y0 + 7 * step + 22}" font-family="{MONO}" font-size="10.5" fill="#5b6478">more</text>
<text x="{W - 28}" y="{H - 18}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5b6478">updated {stamp}</text>""")
    (A / "streak.svg").write_text(frame(W, H, "".join(out), f"""
  .sweep {{ animation: sweep 9s linear infinite; }} @keyframes sweep {{ from {{ transform: translateX(0); }} to {{ transform: translateX({gw - step * 2:.0f}px); }} }}"""), encoding="utf-8")


if __name__ == "__main__":
    render(fetch())
