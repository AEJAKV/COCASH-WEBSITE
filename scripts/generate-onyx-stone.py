"""Onyx Loans v6 — the stone. Rough onyx rock, cutaway top, green gem emerging (juxtaposition).
Usage: python3 onyx_stone.py OUT_DIR FONT_DIR
"""
import math, os, sys
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT, FD = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

ONYX = "#0B0F0D"
ROCK = ["#0B0F0D", "#151C18", "#1F2823", "#2A342E"]       # matte rock planes, dark -> lit
ROCK_R = ["#2B3631", "#36433C", "#435149", "#526158"]     # same rock, lifted for dark backgrounds
BAND = ["#2E3833", "#46524B", "#C9D3CC", "#3A4640"]       # onyx banding on the cut face
G_DK, G, G_LT, G_HI = "#005A03", "#008D05", "#2FB52A", "#7CE86F"
ORANGE = "#FF7A00"
WHITE = "#FFFFFF"
INK = "#1E2F42"


class Font:
    def __init__(self, path):
        f = TTFont(path)
        self.gs, self.cmap = f.getGlyphSet(), f.getBestCmap()
        self.upm = f["head"].unitsPerEm
        self.cap = f["OS/2"].sCapHeight / self.upm

    def path(self, text, size, x, base, tracking=0.0):
        s = size / self.upm
        pen, cx = SVGPathPen(self.gs), 0.0
        for ch in text:
            g = self.gs[self.cmap[ord(ch)]]
            if ch != " ":
                g.draw(TransformPen(pen, (s, 0, 0, -s, x + cx, base)))
            cx += g.width * s + tracking
        return pen.getCommands(), cx - tracking


BARLOW = Font(f"{FD}/barlow-condensed/files/barlow-condensed-latin-800-italic.woff")


def poly(pts, fill, extra=""):
    return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}"{extra}/>'


def svg(w, h, body, bg=None, rx=0):
    b = f'<rect width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">{b}{body}</svg>')


# ── shared rock (200 x 200 box). Seen slightly from above; the cut plane is the top.
CUT_L, CUT_R = (24, 98), (176, 86)
FACE = [CUT_L, (58, 74), (142, 68), CUT_R, (142, 106), (58, 110)]          # cut face (top view)
FRONT = [CUT_L, (58, 110), (142, 106), CUT_R]                              # front edge of the cut
BODY = FRONT + [(188, 120), (174, 158), (134, 182), (68, 184), (28, 162), (14, 126)]
PLANES = [  # three matte planes, kept big and simple so they survive small sizes
    ([(58, 110), (142, 106), (126, 146), (78, 150)], 2),
    ([(142, 106), CUT_R, (188, 120), (174, 158), (126, 146)], 3),
    ([CUT_L, (58, 110), (78, 150), (28, 162), (14, 126)], 1),
]


def rock(mono=None, rev=False):
    R = ROCK_R if rev else ROCK
    out = poly(BODY, mono or R[0])
    if not mono:
        for p, i in PLANES:
            out += poly(p, R[i])
    return out


def scale_pts(pts, k, c=(100, 89)):
    return [(c[0] + (x - c[0]) * k, c[1] + (y - c[1]) * k) for x, y in pts]


def face(mono=None, rev=False, green=False):
    """Cut face. Onyx banding (real onyx is layered) — or polished green inside for the lifted lid."""
    if green:
        cols = [G_DK, G, G_LT, G] if not mono else [mono, WHITE, mono, mono]
    else:
        cols = BAND if not mono else [mono, WHITE, mono, mono]
    out = poly(FACE, cols[0])
    for k, c in ((0.82, cols[1]), (0.70, cols[2]), (0.62, cols[3])):
        if mono and c == mono and k != 0.70:
            continue
        out += poly(scale_pts(FACE, k), c)
    return out


def gem_top(cx, cy, rx, ry, mono=None):
    """Brilliant-cut gem seen from above (perspective-squashed octagon with a table)."""
    O = [(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))) for a in range(-90, 270, 45)]
    T = [(cx + rx * 0.5 * math.cos(math.radians(a)), cy + ry * 0.5 * math.sin(math.radians(a)) - ry * 0.06) for a in range(-90, 270, 45)]
    out = poly(O, mono or G_DK)
    if mono:
        out += poly(T, WHITE) + poly(scale_pts(T, 0.8, (cx, cy - ry * 0.06)), mono)
        return out
    tones = [G_LT, G_HI, G_LT, G, G_DK, G_DK, G, G_LT]
    for i in range(8):
        j = (i + 1) % 8
        out += poly([O[i], O[j], T[j], T[i]], tones[i])
    out += poly(T, G)
    out += poly([T[7], T[0], T[1], (cx, cy - ry * 0.06)], G_LT)
    return out


def gem_side(cx, girdle_y, w, mono=None, tilt=-10):
    """Cut gem rising out of the stone: crown above the girdle, pavilion point sinking into the rock."""
    hw, tw = w / 2, w * 0.27
    crown_h, pav_h = w * 0.36, w * 0.62
    ty, py = girdle_y - crown_h, girdle_y + pav_h
    C = lambda pts: pts
    crown = [(cx - tw, ty), (cx + tw, ty), (cx + hw, girdle_y), (cx - hw, girdle_y)]
    f = [
        ([(cx - hw, girdle_y), (cx - tw, ty), (cx - tw * 0.2, girdle_y)], G),
        ([(cx - tw, ty), (cx + tw, ty), (cx - tw * 0.2, girdle_y)], G_LT),
        ([(cx + tw, ty), (cx + hw, girdle_y), (cx - tw * 0.2, girdle_y)], G_HI),
        ([(cx - hw, girdle_y), (cx - tw * 0.2, girdle_y), (cx, py)], G_DK),
        ([(cx - tw * 0.2, girdle_y), (cx + hw, girdle_y), (cx, py)], G),
    ]
    rot = f' transform="rotate({tilt} {cx:.1f} {girdle_y:.1f})"'
    if mono:
        body = poly(crown + [(cx + hw, girdle_y), (cx, py), (cx - hw, girdle_y)], mono)
        lines = "".join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{WHITE}" stroke-width="1.8"/>'
                        for a, b in (((cx - hw, girdle_y), (cx + hw, girdle_y)), ((cx - tw, ty), (cx - tw * 0.2, girdle_y)),
                                     ((cx + tw, ty), (cx - tw * 0.2, girdle_y)), ((cx - tw * 0.2, girdle_y), (cx, py))))
        return f'<g{rot}>{body}{lines}</g>'
    return f'<g{rot}>' + "".join(poly(p, c) for p, c in f) + '</g>'


def lid(mono=None, rev=False, dx=10, dy=-26, ang=-9):
    """The top of the stone, lifted off up-and-right: rough onyx cap over the polished inside."""
    R = ROCK_R if rev else ROCK
    cap = [CUT_L, (58, 110), (142, 106), CUT_R, (166, 66), (130, 46), (72, 44), (34, 62)]
    planes = [([(58, 110), (142, 106), (130, 72), (72, 74)], 2), ([(142, 106), CUT_R, (166, 66), (130, 46), (130, 72)], 3)]
    out = poly(cap, mono or R[0])
    if not mono:
        for p, i in planes:
            out += poly(p, R[i])
    return f'<g transform="translate({dx},{dy}) rotate({ang} 100 90)">{out}</g>'


def mark(kind, mono=None, rev=False):
    if kind == "geode":
        return rock(mono, rev) + face(mono, rev) + gem_top(100, 88, 30, 17, mono)
    if kind == "emerge":
        # face, then gem, then the stone's front so the pavilion sinks behind the front edge
        front = poly(BODY, mono or (ROCK_R if rev else ROCK)[0])
        if not mono:
            for p, i in PLANES:
                front += poly(p, (ROCK_R if rev else ROCK)[i])
        return face(mono, rev) + gem_side(102, 74, 70, mono) + front
    if kind == "lid":
        return rock(mono, rev) + face(mono, rev, green=True) + lid(mono, rev)
    return ""


MARK_BOX = (12, 18, 180, 168)      # tight bounds (x, y, w, h) of the drawing in the 200 box


def lockup(kind, mono=None, rev=False):
    x0, y0, mw, mh = MARK_BOX
    m = f'<g transform="translate({-x0},{-y0})">{mark(kind, mono, rev)}</g>'
    size = mh * 0.40 / BARLOW.cap
    cap = size * BARLOW.cap
    base = mh * 0.62 + cap / 2
    x = mw + size * 0.30
    c1 = mono or (WHITE if rev else ONYX)
    d1, a = BARLOW.path("ONYX", size, x, base, 1.5)
    d2, b = BARLOW.path("LOANS", size, x + a + size * 0.22, base, 1.5)
    body = m + f'<path d="{d1}" fill="{c1}"/><path d="{d2}" fill="{mono or G}"/>'
    return body, x + a + size * 0.22 + b + 6, mh


def place(body, w, h, x, y, bw, bh):
    s = min(bw / w, bh / h)
    return f'<g transform="translate({x + (bw - w * s) / 2:.1f},{y + (bh - h * s) / 2:.1f}) scale({s:.4f})">{body}</g>'


def label(t, x, y, size=16, fill="#5B6B7C", ls=4, anchor="middle", weight=500):
    return (f'<text x="{x}" y="{y}" font-family="Poppins" font-weight="{weight}" font-size="{size}" '
            f'letter-spacing="{ls}" fill="{fill}" text-anchor="{anchor}">{t}</text>')


def export(name, body, w, h, bg=None, pad=24):
    s = svg(w + 2 * pad, h + 2 * pad, f'<g transform="translate({pad},{pad})">{body}</g>', bg=bg)
    open(f"{OUT}/{name}.svg", "w").write(s)
    cairosvg.svg2png(bytestring=s.encode(), write_to=f"{OUT}/{name}.png", scale=2)


KINDS = [("geode", "1 — GEODE CUT", "A clean cut through rough onyx reveals its real banded layers, with a green gem set at the heart."),
         ("emerge", "2 — EMERGING GEM", "A cut green gem rises out of the rough stone, leaning forward: hidden value revealed, growth."),
         ("lid", "3 — LIFTED LID", "The top of the stone lifts up and forward, revealing polished green inside. Rough outside, value within.")]

for k, _, _ in KINDS:
    export(f"onyx-stone-{k}-logo-horizontal", *lockup(k))
    export(f"onyx-stone-{k}-logo-reversed", *lockup(k, rev=True), bg=ONYX)
    export(f"onyx-stone-{k}-logo-one-colour", *lockup(k, mono=ONYX))
    mb = f'<g transform="translate({-MARK_BOX[0]},{-MARK_BOX[1]})">{mark(k)}</g>'
    export(f"onyx-stone-{k}-mark", mb, MARK_BOX[2], MARK_BOX[3])

W, H = 1600, 1250
b = f'<rect width="{W}" height="{H}" fill="#FAFBFA"/>'
b += label("ONYX LOANS — THE STONE", 80, 80, 22, INK, 6, "start", 600)
b += label("Juxtapose: rough, matte onyx outside / a polished, faceted GoLoans-green gem inside, revealed by a clean cut across the top.", 80, 112, 15, "#5B6B7C", 0, "start", 400)
for i, (k, t, d) in enumerate(KINDS):
    y = 150 + i * 360
    b += label(t, 80, y + 22, 16, INK, 4, "start", 600) + label(d, 80, y + 48, 15, "#5B6B7C", 0, "start", 400)
    b += place(*lockup(k), 80, y + 70, 820, 250)
    b += f'<rect x="950" y="{y + 70}" width="260" height="250" rx="18" fill="{ONYX}"/>'
    mk = f'<g transform="translate({-MARK_BOX[0]},{-MARK_BOX[1]})">{mark(k, rev=True)}</g>'
    b += place(mk, MARK_BOX[2], MARK_BOX[3], 975, y + 90, 210, 210)
    mm = f'<g transform="translate({-MARK_BOX[0]},{-MARK_BOX[1]})">{mark(k, ONYX)}</g>'
    b += place(mm, MARK_BOX[2], MARK_BOX[3], 1250, y + 100, 190, 190)
    b += f'<image href="{OUT}/onyx-stone-{k}-mark.png" x="1470" y="{y + 180}" width="32" height="32"/>'
    b += f'<image href="{OUT}/onyx-stone-{k}-mark.png" x="1510" y="{y + 196}" width="16" height="16"/>'
cairosvg.svg2png(bytestring=svg(W, H, b).encode(), write_to=f"{OUT}/board-stone.png", unsafe=True)
print("ok")
