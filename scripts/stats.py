"""Stats card that counts private repos too.

With a token that can read your private repos in STATS_TOKEN (or GH_TOKEN), private repos are counted.
Without one it falls back to public repos only. Only totals are written to the SVG, no repo names or code.
"""
import json, os, pathlib, re, urllib.request
from datetime import datetime, timezone

from build import A, SANS, MONO, G as V, IN as CY, frame, dark

USER = "Ahmed-Raouf-Metwally"
TOKEN = os.environ.get("STATS_TOKEN") or os.environ.get("GH_TOKEN")
LANG_COL = {"C#": "#178600", "Python": "#3572A5", "PHP": "#777BB4", "Blade": "#F7523F", "Dart": "#00B4AB", "CSS": "#663399",
            "JavaScript": "#F1E05A", "HTML": "#E34C26", "TypeScript": "#3178C6", "Kotlin": "#A97BFF", "Swift": "#F05138"}


def api(path, raw=False):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com/{path}", headers=headers)
    with urllib.request.urlopen(req) as r:
        return (json.load(r), r.headers) if raw else json.load(r)


def commit_count(repo):
    try:
        data, headers = api(f"repos/{USER}/{repo}/commits?author={USER}&per_page=1", raw=True)
    except urllib.error.HTTPError:  # empty repo
        return 0
    m = re.search(r'page=(\d+)>; rel="last"', headers.get("Link", ""))
    return int(m.group(1)) if m else len(data)


def collect():
    repos, page = [], 1
    listing = "user/repos?affiliation=owner&" if TOKEN else f"users/{USER}/repos?type=owner&"
    while batch := api(f"{listing}per_page=100&page={page}"):
        repos += [r for r in batch if r["name"] != USER and not r["fork"]]
        page += 1
    langs, commits = {}, 0
    for r in repos:
        for k, v in api(f"repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
        if TOKEN:
            commits += commit_count(r["name"])
    if not TOKEN:  # one search call instead of one call per repo, to stay under the anonymous rate limit
        commits = api(f"search/commits?q=author:{USER}&per_page=1")["total_count"]
    # C++/CMake/Swift etc. in Flutter repos are generated platform runners, not code I wrote
    for k in ("C++", "CMake", "Swift", "C", "Objective-C", "Ruby", "Kotlin", "Dockerfile", "Shell", "Makefile"):
        langs.pop(k, None)
    return len(repos), commits, langs


def render(n_repos, commits, langs):
    W, H = 920, 250
    total = sum(langs.values())
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
    other = total - sum(v for _, v in top)
    parts = top + ([("Other", other)] if other else [])

    tiles = [("📦", f"{n_repos}", "repositories", "#F59E0B"),
             ("🔨", f"{commits}+", "commits", V),
             ("🧠", f"{len(langs)}", "languages", CY)]
    out = []
    for i, (emo, num, label, col) in enumerate(tiles):
        x, y, w, h, d = 28, 26 + i * 68, 250, 56, -(i * .4)
        out.append(f"""<g transform="translate({x} {y})"><g class="fl" style="animation-delay:{d:.1f}s">
  <rect y="6" width="{w}" height="{h}" rx="14" fill="{dark(col, .35)}"/>
  <rect width="{w}" height="{h}" rx="14" fill="url(#face)"/>
  <rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="13.5" fill="none" stroke="{col}" stroke-opacity=".45"/>
  <rect width="{w}" height="{h}" rx="14" fill="url(#gloss)"/>
  <text x="20" y="37" font-size="22">{emo}</text>
  <text x="62" y="38" font-family="{SANS}" font-size="26" font-weight="800" fill="#f4f7fb">{num}</text>
  <text x="{62 + len(num) * 16 + 10}" y="37" font-family="{SANS}" font-size="14" fill="#a9b3c9">{label}</text>
</g></g>""")

    # stacked language bar as a 3D slab
    bx, by, bw, bh = 310, 70, 580, 26
    x, seg = bx, []
    for k, v in parts:
        w = bw * v / total
        col = LANG_COL.get(k, "#6b7280")
        seg.append(f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{col}"/>')
        seg.append(f'<rect x="{x:.1f}" y="{by + bh}" width="{w:.1f}" height="8" fill="{dark(col, .45)}"/>')
        x += w
    legend = []
    for i, (k, v) in enumerate(parts):
        c, r = i % 3, i // 3
        col = LANG_COL.get(k, "#6b7280")
        legend.append(f'<g transform="translate({bx + c * 195} {by + 70 + r * 34})">'
                      f'<rect width="14" height="14" y="-12" rx="4" fill="{col}"/>'
                      f'<text x="22" font-family="{SANS}" font-size="14" font-weight="600" fill="#e5e7eb">{k}</text>'
                      f'<text x="{22 + len(k) * 8.6 + 8}" font-family="{MONO}" font-size="13" fill="#8b95ab">{100 * v / total:.1f}%</text></g>')
    stamp = datetime.now(timezone.utc).strftime("%d %b %Y")
    out.append(f"""<text x="{bx}" y="48" font-family="{SANS}" font-size="16" font-weight="700" fill="#f4f7fb">Languages across all my repos <tspan font-weight="400" fill="#8b95ab" font-size="13">({"private included" if TOKEN else "public repos"})</tspan></text>
<defs><clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="{bh + 8}" rx="10"/></clipPath>
<linearGradient id="bsh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".35"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<g class="fl" style="animation-delay:-1s"><g clip-path="url(#bar)">{"".join(seg)}
  <rect x="{bx}" y="{by}" width="{bw}" height="{bh / 2}" fill="#fff" fill-opacity=".14"/>
  <rect class="bs" x="{bx - 120}" y="{by}" width="120" height="{bh + 8}" fill="url(#bsh)"/></g></g>
{"".join(legend)}
<text x="{W - 28}" y="{H - 18}" text-anchor="end" font-family="{MONO}" font-size="11" fill="#5b6478">updated {stamp}</text>""")
    svg = frame(W, H, "".join(out)).replace("</style>", """
  .bs { animation: bs 4.5s ease-in-out infinite; }
  @keyframes bs { 0%,40% { transform: translateX(0); } 100% { transform: translateX(720px); } }
</style>""")
    (A / "stats.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    render(*collect())
