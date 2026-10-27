"""Onyx Loans — v3 concept directions in the GoLoans palette.
Usage: python3 onyx_v3.py OUT_DIR FONT_DIR
"""
import math, os, sys
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT, FD = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

# GoLoans palette (from GOLOANS-NEWEST-FINAL-WEBSITE style.css + logo)
GREEN = "#008D05"
GREEN_DK = "#006B04"
GREEN_LT = "#3DAA36"
ONYX = "#0B0F0D"      # near-black with a green undertone = polished onyx
WHITE = "#FFFFFF"
INK = "#1E2F42"        # GoLoans navy, used only for board labels
SHEEN = ["#0B0F0D", "#161D19", "#222B26", "#2F3A34"]   # onyx facet tones
SLANT = math.tan(math.radians(12))


class Font:
    def __init__(self, path):
        f = TTFont(path)
        self.gs, self.cmap = f.getGlyphSet(), f.getBestCmap()
        self.upm = f["head"].unitsPerEm
        self.cap = f["OS/2"].sCapHeight / self.upm

    def path(self, text, size, x=0, base=0, tracking=0.0):
        s = size / self.upm
        pen, cx = SVGPathPen(self.gs), 0.0
        for ch in text:
            if ch == " ":
                cx += self.gs[self.cmap[32]].width * s + tracking
                continue
            g = self.gs[self.cmap[ord(ch)]]
            g.draw(TransformPen(pen, (s, 0, 0, -s, x + cx, base)))
            cx += g.width * s + tracking
        return pen.getCommands(), cx - tracking


BC = f"{FD}/barlow-condensed/files/barlow-condensed-latin-"
BARLOW = Font(BC + "900-italic.woff")
BARLOW8 = Font(BC + "800-italic.woff")
MANROPE = Font(f"{FD}/manrope/files/manrope-latin-800-normal.woff")


def svg(w, h, body, bg=None, rx=0):
    b = f'<rect width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">{b}{body}</svg>')


def para(x0, x1, y0, y1, fill):
    """Forward-slanted parallelogram (GoLoans block)."""
    s = (y1 - y0) * SLANT
    return (f'<polygon points="{x0 + s:.1f},{y0:.1f} {x1 + s:.1f},{y0:.1f} '
            f'{x1:.1f},{y1:.1f} {x0:.1f},{y1:.1f}" fill="{fill}"/>')


# ───────────────────────── Direction 1 — SISTER BLOCK ─────────────────────────
def d1_lockup(mono=None, rev=False):
    H, pad = 120, 24
    size = H * 0.62 / BARLOW.cap
    base = H / 2 + size * BARLOW.cap / 2
    _, w1 = BARLOW.path("ONYX", size, tracking=1)
    _, w2 = BARLOW.path("LOANS", size, tracking=1)
    s = H * SLANT
    b1 = (0, pad + w1 + pad + s * 0.5)
    b2 = (b1[1], b1[1] + pad + w2 + pad + s * 0.5)
    blk1 = mono or (WHITE if rev else ONYX)
    blk2 = mono or GREEN
    txt1 = WHITE if not rev or mono else ONYX
    t1, _ = BARLOW.path("ONYX", size, b1[0] + pad + s * 0.45, base, 1)
    t2, _ = BARLOW.path("LOANS", size, b2[0] + pad + s * 0.45, base, 1)
    gap = 7
    stripes = "".join(para(b2[1] + gap + i * 20, b2[1] + gap + i * 20 + 11, 0, H,
                           mono or (GREEN_LT if i == 0 else GREEN_DK)) for i in range(2))
    body = (para(*b1, 0, H, blk1) + para(b2[0] - 1, b2[1], 0, H, blk2) + stripes +
            f'<path d="{t1}" fill="{WHITE if (mono and not rev) else txt1}"/>'
            f'<path d="{t2}" fill="{WHITE if not rev or mono else ONYX}"/>')
    if mono and rev:
        body = body.replace(f'fill="{WHITE}"', f'fill="{ONYX}"')
    return body, b2[1] + gap + 40 + s, H


def d1_mark(mono=None, rev=False):
    """'O' block: onyx block + green speed block, white italic O."""
    H = 160
    s = H * SLANT
    size = H * 0.66 / BARLOW.cap
    _, wo = BARLOW.path("O", size)
    W1 = wo + 52
    o, _ = BARLOW.path("O", size, 26 + s * 0.45, H / 2 + size * BARLOW.cap / 2)
    a = mono or (WHITE if rev else ONYX)
    b = mono or GREEN
    body = (para(0, W1, 0, H, a) + para(W1 + 7, W1 + 7 + 26, 0, H, b) +
            f'<path d="{o}" fill="{ONYX if rev and not mono else WHITE}"/>')
    return body, W1 + 7 + 26 + s, H


# ───────────────────────── Direction 2 — ONYX GEM ─────────────────────────
def d2_mark(mono=None, rev=False, R=80, r=46, gap=4.5):
    """Octagonal faceted ring — a cut onyx forming the O. One green facet = 'go'."""
    cx = cy = R
    pts = lambda rad: [(cx + rad * math.cos(math.radians(-112.5 + 45 * i)),
                        cy + rad * math.sin(math.radians(-112.5 + 45 * i))) for i in range(8)]
    O, I = pts(R), pts(r)
    # facet i spans vertices i..i+1 ; i=1 is the top-right facet (lit side)
    shade = [SHEEN[2], GREEN, SHEEN[3], SHEEN[1], SHEEN[0], SHEEN[0], SHEEN[1], SHEEN[2]]
    if rev:
        shade = ["#E9EEEA", GREEN, "#FFFFFF", "#D5DDD7", "#C3CDC6", "#C3CDC6", "#D5DDD7", "#E9EEEA"]
    d = gap / (2 * math.sin(math.radians(67.5)))
    out = ""
    for i in range(8):
        j = (i + 1) % 8
        def mv(p, q):   # move p toward q by d
            L = math.dist(p, q)
            return (p[0] + (q[0] - p[0]) * d / L, p[1] + (q[1] - p[1]) * d / L)
        a, b2_, c, e = mv(O[i], O[j]), mv(O[j], O[i]), mv(I[j], I[i]), mv(I[i], I[j])
        # split each facet on its diagonal -> two triangles in different tones = a cut stone
        t1, t2 = [a, b2_, c], [a, c, e]
        if mono:
            f1 = f2 = mono
        elif shade[i] == GREEN:
            f1, f2 = GREEN, GREEN_DK
        else:
            k = SHEEN.index(shade[i]) if shade[i] in SHEEN else None
            f1 = shade[i]
            f2 = SHEEN[max(0, k - 1)] if k is not None else ("#B9C4BC" if rev else shade[i])
        hair = 1.2
        for tri, f in ((t1, f1), (t2, f2)):
            out += f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in tri)}" fill="{f}"/>'
        if mono:   # keep the facet cut visible in one colour
            out += (f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{c[0]:.2f}" y2="{c[1]:.2f}" '
                    f'stroke="{WHITE}" stroke-width="{hair}"/>')
    # table highlight: a thin bright sliver on the top-right inner edge (polish)
    if not mono:
        a, b = I[1], I[2]
        out += (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                f'stroke="{WHITE}" stroke-opacity="0.5" stroke-width="2" stroke-linecap="round" '
                f'transform="translate({-2 * math.cos(math.radians(-67.5)):.2f},{-2 * math.sin(math.radians(-67.5)):.2f})"/>')
    return out, 2 * R, 2 * R


# ───────────────────────── Direction 3 — SPLIT O ─────────────────────────
def d3_mark(mono=None, rev=False):
    """Italic O split on the diagonal: onyx half (borrower) + green half (cosigner/lender)
    lifted forward — two parties, one approval, moving up."""
    rx, ry, irx, iry = 50, 62, 23, 36
    cx, cy = 62, 74
    ring = (f"M{cx - rx} {cy} a{rx} {ry} 0 1 0 {2 * rx} 0 a{rx} {ry} 0 1 0 {-2 * rx} 0 Z "
            f"M{cx - irx} {cy} a{irx} {iry} 0 1 1 {2 * irx} 0 a{irx} {iry} 0 1 1 {-2 * irx} 0 Z")
    g = 5   # half gap
    # split line through centre running from upper-left to lower-right
    lo = f"{cx - 200 - g},{cy - 200 + g} {cx + 200 - g},{cy + 200 + g} {cx - 300},{cy + 300} {cx - 300},{cy - 100}"
    hi = f"{cx - 200 + g},{cy - 200 - g} {cx + 200 + g},{cy + 200 - g} {cx + 300},{cy + 100} {cx + 300},{cy - 300}"
    c1 = mono or (WHITE if rev else ONYX)
    c2 = mono or GREEN
    sk = f"matrix(1 0 {-SLANT:.4f} 1 {cy * SLANT + 2:.2f} 0)"
    uid = f"{int(bool(mono))}{int(rev)}{abs(hash(mono)) % 997}"
    body = f'''<defs>
  <clipPath id="lo{uid}"><polygon points="{lo}"/></clipPath>
  <clipPath id="hi{uid}"><polygon points="{hi}"/></clipPath>
</defs>
<g transform="{sk}">
  <path d="{ring}" fill-rule="evenodd" fill="{c1}" clip-path="url(#lo{uid})"/>
  <g transform="translate(6,-6)"><path d="{ring}" fill-rule="evenodd" fill="{c2}" clip-path="url(#hi{uid})"/></g>
</g>'''
    return body, 2 * cx + 22, 2 * cy + 2


# ───────────────────────── lockups ─────────────────────────
def lockup(mark_fn, font, words, cases, mono=None, rev=False, gap_k=0.42):
    mb, mw, mh = mark_fn(mono=mono, rev=rev)
    size = mh * 0.62 / font.cap
    base = mh / 2 + size * font.cap / 2
    x = mw + size * gap_k
    c1 = mono or (WHITE if rev else ONYX)
    c2 = mono or GREEN
    d1, w1 = font.path(words[0], size, x, base, cases[0])
    d2, w2 = font.path(words[1], size, x + w1 + size * 0.22, base, cases[1])
    body = mb + f'<path d="{d1}" fill="{c1}"/><path d="{d2}" fill="{c2}"/>'
    return body, x + w1 + size * 0.22 + w2 + 6, mh


DIRS = {
    "d1-sister-block": dict(
        title="01 — SISTER BLOCK",
        why="Mirrors the GoLoans block lockup (GO green / LOANS black, so ONYX black / LOANS green). "
            "Instant family recognition; the forward slant and speed stripes = funds fast.",
        lock=lambda **k: d1_lockup(**k), mark=d1_mark),
    "d2-onyx-gem": dict(
        title="02 — ONYX GEM",
        why="The O is a cut onyx: eight facets = transparent loan terms, the stone = security and real value. "
            "One green facet is the 'GO' — approval, the GoLoans spark.",
        lock=lambda **k: lockup(d2_mark, MANROPE, ("Onyx", "Loans"), (-1.5, -1.5), **k), mark=d2_mark),
    "d3-split-o": dict(
        title="03 — SPLIT O",
        why="One O, two parties: the onyx half is the borrower, the green half is the cosigner/lender, "
            "lifted up and forward — a match that moves you ahead. GoLoans italic DNA.",
        lock=lambda **k: lockup(d3_mark, BARLOW8, ("ONYX", "LOANS"), (1.5, 1.5), gap_k=0.32, **k), mark=d3_mark),
}


def place(body, w, h, x, y, box_w, box_h):
    s = min(box_w / w, box_h / h)
    return f'<g transform="translate({x + (box_w - w * s) / 2:.1f},{y + (box_h - h * s) / 2:.1f}) scale({s:.4f})">{body}</g>'


def label(t, x, y, size=17, fill="#5B6B7C", ls=4, anchor="middle", weight=500):
    return (f'<text x="{x}" y="{y}" font-family="Poppins" font-weight="{weight}" font-size="{size}" '
            f'letter-spacing="{ls}" fill="{fill}" text-anchor="{anchor}">{t}</text>')


def wrap(t, n):
    out, line = [], ""
    for w in t.split():
        if len(line) + len(w) + 1 > n:
            out.append(line); line = w
        else:
            line = (line + " " + w).strip()
    return out + [line]


for key, D in DIRS.items():
    files = {}
    files["logo-horizontal"] = D["lock"]()
    files["logo-reversed"] = D["lock"](rev=True)
    files["logo-one-colour"] = D["lock"](mono=ONYX)
    files["mark"] = D["mark"]()
    for name, (b, w, h) in files.items():
        bg = ONYX if name == "logo-reversed" else None
        pad = 24
        s = svg(w + 2 * pad, h + 2 * pad, f'<g transform="translate({pad},{pad})">{b}</g>', bg=bg)
        open(f"{OUT}/onyx-{key}-{name}.svg", "w").write(s)
        cairosvg.svg2png(bytestring=s.encode(), write_to=f"{OUT}/onyx-{key}-{name}.png", scale=2)

    # app icon: mark on onyx rounded square (D1 uses green tile so the black block shows)
    mb, mw, mh = D["mark"](rev=(key != "d1-sister-block"))
    tile = GREEN if key == "d1-sister-block" else ONYX
    icon_body = place(mb, mw, mh, 36, 36, 128, 128)
    icon = svg(200, 200, icon_body, bg=tile, rx=44)
    open(f"{OUT}/onyx-{key}-app-icon.svg", "w").write(icon)
    cairosvg.svg2png(bytestring=icon.encode(), write_to=f"{OUT}/onyx-{key}-app-icon.png", scale=2)

    # ── presentation board 1600 x 1000 ──
    W, H = 1600, 1000
    b = f'<rect width="{W}" height="{H}" fill="#FAFBFA"/>'
    b += label(D["title"], 80, 92, 22, INK, 6, "start", 600)
    for i, ln in enumerate(wrap(D["why"], 120)):
        b += label(ln, 80, 128 + i * 26, 16, "#5B6B7C", 0, "start", 400)
    lb, lw, lh = D["lock"]()
    b += place(lb, lw, lh, 160, 200, 1280, 300)
    b += f'<line x1="80" y1="560" x2="1520" y2="560" stroke="#E2E6E3"/>'
    tiles = [("PRIMARY MARK", D["mark"](), None),
             ("ONE COLOUR", D["lock"](mono=ONYX), None),
             ("REVERSED", D["lock"](rev=True), ONYX),
             ("DIGITAL ICON", None, None)]
    tw = 1440 / 4
    for i, (name, data, bg) in enumerate(tiles):
        x0 = 80 + i * tw
        if bg:
            b += f'<rect x="{x0 + 14}" y="600" width="{tw - 28}" height="250" rx="18" fill="{bg}"/>'
        if data:
            bb, bw, bh = data
            b += place(bb, bw, bh, x0 + 40, 630, tw - 80, 190)
        else:
            b += f'<rect x="{x0 + tw / 2 - 95}" y="630" width="190" height="190" rx="42" fill="{tile}"/>'
            b += place(mb, mw, mh, x0 + tw / 2 - 60, 665, 120, 120)
        b += label(name, x0 + tw / 2, 900, 16)
        if i:
            b += f'<line x1="{x0}" y1="610" x2="{x0}" y2="860" stroke="#E2E6E3"/>'
    # favicon reality check
    b += label("16 px", 1452, 952, 11, "#8A979F", 1)
    b += f'<image href="{OUT}/onyx-{key}-app-icon.png" x="1480" y="938" width="16" height="16"/>'
    b += f'<image href="{OUT}/onyx-{key}-app-icon.png" x="1504" y="930" width="32" height="32"/>'
    board = svg(W, H, b)
    cairosvg.svg2png(bytestring=board.encode(), write_to=f"{OUT}/board-{key}.png", unsafe=True)
print("ok")
