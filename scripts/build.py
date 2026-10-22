"""Genera le card SVG del README del profilo SusannaKay.

    python3 scripts/build.py          # rigenera le card dai dati in data/
    python3 scripts/build.py --fetch  # prima scarica i contributi da GitHub (serve GITHUB_TOKEN)

Input:  data/avatar.txt         48x48 cifre 0-9, luminosità dell'avatar (ritratto ASCII)
        data/contributions.json [{"date": "AAAA-MM-GG", "count": N}, ...] ultimo anno
Output: assets/hero.svg, assets/constellation.svg, assets/city.svg
"""
import json
import os
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
LOGIN = "SusannaKay"

BG = "#0d0b10"
PANEL = "#141118"
LINE = "#2a2430"
INK = "#ece7f1"
INK2 = "#b9b0c4"
INK3 = "#7d7488"
PINK = "#ff6fae"
PINK_DIM = "#7a3555"
MONO = "'JetBrains Mono','SFMono-Regular',Menlo,Consolas,monospace"

W = 900


def frame(h, body, label, right=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" font-family="{MONO}">
<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="14" fill="{BG}" stroke="{LINE}"/>
<text x="32" y="38" font-size="11" letter-spacing="2.2" fill="{INK3}">{escape(label)}</text>
<text x="{W-32}" y="38" font-size="11" letter-spacing="1" fill="{INK3}" text-anchor="end">{escape(right)}</text>
{body}
<text x="{W-32}" y="{h-18}" font-size="9" fill="{INK3}" text-anchor="end" opacity="0.7">skayed.dev</text>
</svg>
"""


# ---------- caratteri a puntini (5x7) ----------
GLYPHS = {
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
}


def dot_word(word, x0, y0, pitch, color):
    out = []
    for i, ch in enumerate(word):
        g = GLYPHS[ch]
        gx = x0 + i * 6 * pitch
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                cx, cy = gx + c * pitch, y0 + r * pitch
                if bit == "1":
                    out.append(f'<circle cx="{cx}" cy="{cy}" r="{pitch*0.38:.2f}" fill="{color}"/>')
                else:
                    out.append(f'<circle cx="{cx}" cy="{cy}" r="{pitch*0.12:.2f}" fill="{LINE}"/>')
    return "\n".join(out)


# ---------- ritratto ASCII ----------
RAMP = {"0": "@", "1": "@", "2": "#", "3": "%", "4": "*", "5": "+", "6": "=", "7": "-", "8": " ", "9": "."}


def ascii_portrait(cx, cy, cell):
    rows = (DATA / "avatar.txt").read_text().split()
    rows = rows[6:43]               # solo la testa
    rows = [r[8:41] for r in rows]  # colonne utili
    n_r, n_c = len(rows), len(rows[0])
    w, h = n_c * cell, n_r * cell
    x0, y0 = cx - w / 2, cy - h / 2
    out = [f'<circle cx="{cx}" cy="{cy}" r="{max(w,h)/2+10}" fill="none" stroke="{PINK_DIM}" stroke-dasharray="2 5"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{max(w,h)/2+20}" fill="none" stroke="{LINE}"/>']
    for i, r in enumerate(rows):
        line = "".join(RAMP[c] for c in r)
        if not line.strip():
            continue
        out.append(
            f'<text x="{x0:.1f}" y="{y0 + (i+1)*cell:.1f}" font-size="{cell*1.15:.1f}" '
            f'textLength="{w:.1f}" lengthAdjust="spacing" fill="{INK}" xml:space="preserve">{escape(line)}</text>'
        )
    return "\n".join(out)


def hero():
    stats = [("3", "LIVE PRODUCTS"), ("10", "YEARS IN MARKETING"), ("14", "42 PROJECTS, BY HAND"), ("3", "HACKATHONS & JAMS")]
    body = [
        f'<text x="32" y="86" font-size="11" letter-spacing="2.2" fill="{INK3}">HELLO, WORLD. I\'M</text>',
        dot_word("SUSANNA", 36, 112, 8, INK),
        dot_word("KAYED", 36, 186, 8, PINK),
        f'<text x="32" y="268" font-size="15" font-weight="700" fill="{INK}">Builder · ex performance marketer</text>',
        f'<text x="32" y="290" font-size="12" fill="{INK3}">42 Roma · Rome, IT</text>',
        ascii_portrait(712, 180, 6.4),
        f'<line x1="32" y1="330" x2="{W-32}" y2="330" stroke="{LINE}"/>',
    ]
    cw = (W - 64) / 4
    for i, (n, lab) in enumerate(stats):
        x = 32 + i * cw
        body.append(f'<text x="{x}" y="356" font-size="10" letter-spacing="1.6" fill="{INK3}">{escape(lab)}</text>')
        body.append(f'<text x="{x}" y="392" font-size="30" font-weight="700" fill="{INK}">{n}</text>')
    return frame(420, "\n".join(body), "SKAYED.DEV / BUILDER", "@SusannaKay")


def constellation():
    ai = [("steam companion", 320, 248, 1), ("CineMatch", 105, 178, 1), ("homelab", 255, 162, 1),
          ("atlante", 140, 318, 1), ("ingorgo", 70, 360, 0), ("ampolle", 290, 362, 0)]
    hand = ["libft", "born2beroot", "get_next_line", "ft_printf", "so_long", "pipex", "push_swap",
            "philosophers", "netpractice", "minishell", "cub3d", "cpp modules", "inception", "ft_irc"]
    body = [f'<text x="32" y="74" font-size="20" fill="{INK}">Two ways of building</text>',
            f'<line x1="32" y1="96" x2="{W-32}" y2="96" stroke="{LINE}" stroke-dasharray="3 4"/>',
            f'<text x="32" y="124" font-size="10" letter-spacing="1.8" fill="{PINK}">BUILT WITH AI</text>',
            f'<text x="470" y="124" font-size="10" letter-spacing="1.8" fill="{INK2}">WRITTEN BY HAND · 42 ROMA</text>']
    hub = (200, 250)
    for name, x, y, live in ai:
        body.append(f'<line x1="{hub[0]}" y1="{hub[1]}" x2="{x}" y2="{y}" stroke="{PINK_DIM if live else LINE}" stroke-dasharray="2 4"/>')
    body.append(f'<circle cx="{hub[0]}" cy="{hub[1]}" r="5" fill="{PINK}"/>')
    for name, x, y, live in ai:
        r = 15 if live else 11
        body.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PANEL}" stroke="{PINK if live else INK3}"/>')
        if live:
            body.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{PINK}"/>')
        body.append(f'<text x="{x}" y="{y + r + 15}" font-size="{11 if live else 10}" fill="{INK if live else INK3}" text-anchor="middle">{escape(name)}</text>')

    # percorso di 42: un sentiero a serpentina, in ordine
    cols, x0, y0, dx, dy = 5, 490, 158, 84, 66
    pts = []
    for i, name in enumerate(hand):
        row, col = divmod(i, cols)
        if row % 2:
            col = cols - 1 - col
        pts.append((x0 + col * dx, y0 + row * dy, name))
    nx, ny, _ = pts[-1]
    path = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y, _) in enumerate(pts))
    body.append(f'<line x1="{nx}" y1="{ny}" x2="{nx + dx}" y2="{ny}" stroke="{INK3}" stroke-dasharray="2 4"/>')
    body.append(f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="2"/>')
    for i, (x, y, name) in enumerate(pts):
        last = i == len(pts) - 1
        body.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{INK if last else INK2}"/>')
        body.append(f'<text x="{x}" y="{y + 22}" font-size="10" fill="{INK2}" text-anchor="middle">{escape(name)}</text>')
    nx, ny, _ = pts[-1]
    body.append(f'<circle cx="{nx + dx}" cy="{ny}" r="6" fill="none" stroke="{INK3}" stroke-dasharray="2 3"/>')
    body.append(f'<text x="{nx + dx}" y="{ny + 22}" font-size="10" fill="{INK3}" text-anchor="middle">next…</text>')
    return frame(420, "\n".join(body), "PROJECTS")


def city():
    days = json.loads((DATA / "contributions.json").read_text())
    counts = [d["count"] for d in days]
    start = date.fromisoformat(days[0]["date"])
    first_sunday = start - timedelta(days=(start.weekday() + 1) % 7)
    total = sum(counts)
    active = sum(1 for c in counts if c)
    best_i = max(range(len(counts)), key=lambda i: counts[i])
    best_day = start + timedelta(days=best_i)
    peak = max(counts) or 1

    ux, uy = 8.4, 3.5     # asse delle settimane: verso destra-basso
    vx, vy = -8.6, 4.3     # asse dei giorni: verso sinistra-basso
    ox, oy = 410, 130
    s = 0.84

    def shade(hexcol, f):
        r, g, b = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
        return "#%02x%02x%02x" % tuple(min(255, int(c * f)) for c in (r, g, b))

    cells = []
    for i, c in enumerate(counts):
        d = start + timedelta(days=i)
        w = (d - first_sunday).days // 7
        r = (d.weekday() + 1) % 7
        cells.append((w, r, c))
    cells.sort(key=lambda t: (t[0] * uy + t[1] * vy, t[0]))

    out = []
    for w, r, c in cells:
        px, py = ox + w * ux + r * vx, oy + w * uy + r * vy
        h = 2.0 if c == 0 else 6 + 74 * (c / peak) ** 0.55
        a = (px, py)
        b = (px + ux * s, py + uy * s)
        cc = (px + (ux + vx) * s, py + (uy + vy) * s)
        dd = (px + vx * s, py + vy * s)
        up = lambda p: (p[0], p[1] - h)
        if c == 0:
            top, left, right = "#2a1d29", "#1c141d", "#221823"
        else:
            t = c / peak
            base = PINK if t > 0.35 else ("#d9578f" if t > 0.12 else "#a94573")
            top, left, right = shade(base, 1.18), shade(base, 0.62), shade(base, 0.82)
        pts = lambda *ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
        out.append(f'<polygon points="{pts(dd, cc, up(cc), up(dd))}" fill="{left}"/>')
        out.append(f'<polygon points="{pts(b, cc, up(cc), up(b))}" fill="{right}"/>')
        out.append(f'<polygon points="{pts(up(a), up(b), up(cc), up(dd))}" fill="{top}"/>')

    body = [
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#1d1220"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect x="1" y="1" width="{W-2}" height="418" rx="14" fill="url(#g)"/>',
        f'<text x="36" y="70" font-size="11" letter-spacing="2.4" font-weight="700" fill="{PINK}">CONTRIBUTION CITY</text>',
        f'<text x="36" y="112" font-size="38" font-weight="700" fill="{INK}">{total}</text>',
        f'<text x="36" y="136" font-size="12" fill="{INK2}">contributions in the last year</text>',
        f'<text x="36" y="172" font-size="12" font-weight="700" fill="{INK}">{active} active days</text>',
        f'<text x="36" y="192" font-size="12" font-weight="700" fill="{INK}">Busiest day: {peak}</text>',
        f'<text x="36" y="210" font-size="11" fill="{INK3}">{best_day:%b %-d, %Y}</text>',
        f'<text x="36" y="380" font-size="11" fill="{INK3}">@SusannaKay</text>',
        "\n".join(out),
    ]
    return frame(420, "\n".join(body), "", "")


QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def fetch():
    """Scarica dal GraphQL di GitHub i contributi giornalieri dell'ultimo anno."""
    token = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        res = json.load(r)
    if "errors" in res:
        sys.exit(f"GitHub API: {res['errors']}")
    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [{"date": d["date"], "count": d["contributionCount"]} for w in weeks for d in w["contributionDays"]]
    (DATA / "contributions.json").write_text(json.dumps(days, indent=0) + "\n")
    print(f"fetched {len(days)} days, {sum(d['count'] for d in days)} contributions")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    ASSETS.mkdir(exist_ok=True)
    for name, fn in [("hero", hero), ("constellation", constellation), ("city", city)]:
        (ASSETS / f"{name}.svg").write_text(fn())
        print("wrote", name)
