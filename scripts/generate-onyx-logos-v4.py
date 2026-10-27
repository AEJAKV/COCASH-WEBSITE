"""Onyx Loans v4 — Hex Split O (Split O x segmented-hexagon reference), GoLoans palette.
Usage: python3 onyx_v4.py OUT_DIR FONT_DIR
"""
import math, os, re, sys
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen

OUT, FD = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

GREEN, GREEN_DK = "#008D05", "#006B04"
GREEN_LT = "#3DAA36"
ORANGE = "#FF7A00"
ONYX = "#0B0F0D"
WHITE = "#FFFFFF"
INK = "#1E2F42"
SLANT = math.tan(math.radians(12))


class Font:
    def __init__(self, path):
        f = TTFont(path)
        self.gs, self.cmap = f.getGlyphSet(), f.getBestCmap()
        self.upm = f["head"].unitsPerEm
        self.cap = f["OS/2"].sCapHeight / self.upm
        self.xh = f["OS/2"].sxHeight / self.upm

    def glyph(self, ch):
        return self.gs[self.cmap[ord(ch)]]

    def runs(self, text, size, x, base, tracking=0.0):
        """Yield (char, svg path, glyph bounds in page coords) per glyph; return width."""
        s = size / self.upm
        cx, out = 0.0, []
        for ch in text:
            g = self.glyph(ch)
            if ch != " ":
                pen = SVGPathPen(self.gs)
                g.draw(TransformPen(pen, (s, 0, 0, -s, x + cx, base)))
                rp = RecordingPen(); g.draw(TransformPen(rp, (s, 0, 0, -s, x + cx, base)))
                PTS[d_key(pen)] = [pt for _, args in rp.value for pt in args if isinstance(pt, tuple)]
                cs, cur = [], []
                for op, args in rp.value:
                    cur += [pt for pt in args if isinstance(pt, tuple)]
                    if op in ("closePath", "endPath"):
                        cs.append(cur); cur = []
                CONT[d_key(pen)] = cs
                bp = BoundsPen(self.gs); g.draw(bp)
                xmin, ymin, xmax, ymax = bp.bounds
                out.append((ch, pen.getCommands(),
                            (x + cx + xmin * s, base - ymax * s, x + cx + xmax * s, base - ymin * s)))
            cx += g.width * s + tracking
        return out, cx - tracking


BARLOW = Font(f"{FD}/barlow-condensed/files/barlow-condensed-latin-800-italic.woff")
BARLOW9 = Font(f"{FD}/barlow-condensed/files/barlow-condensed-latin-900-italic.woff")
MANROPE = Font(f"{FD}/manrope/files/manrope-latin-800-normal.woff")


def svg(w, h, body, bg=None, rx=0):
    b = f'<rect width="{w:.0f}" height="{h:.0f}" rx="{rx}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">{b}{body}</svg>')


_uid = [0]


def uid():
    _uid[0] += 1
    return f"u{_uid[0]}"


# ───────── the mark: segmented hexagon O, split + lifted ─────────
def hex_o(colors, italic=True, R=60, r=31, gap=5, lift=4):
    """Pointy-top hexagon ring, 6 segments with gaps at the corners.
    Segments (clockwise from top): S0 top→upper-right, S1 right side, S2 lower-right,
    S3 lower-left, S4 left side, S5 upper-left→top.
    Lower half (S2,S3,S4) = onyx  — the borrower, the solid base.
    Upper half (S0,S1)    = green — the cosigner / lender (GoLoans green), lifted up & forward.
    S5                    = orange — the rising 'GO' stroke, same angle as the X's orange stroke.
    """
    cx, cy = R + 8, R + 8
    V = lambda rad: [(cx + rad * math.cos(math.radians(-90 + 60 * k)),
                      cy + rad * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    O, I = V(R), V(r)
    d = gap / (2 * math.sin(math.radians(60)))

    def mv(p, q):
        L = math.dist(p, q)
        return (p[0] + (q[0] - p[0]) * d / L, p[1] + (q[1] - p[1]) * d / L)

    lifted = {0, 1, 5}
    out = ""
    for k in range(6):
        j = (k + 1) % 6
        poly = [mv(O[k], O[j]), mv(O[j], O[k]), mv(I[j], I[k]), mv(I[k], I[j])]
        dx, dy = (lift, -lift) if k in lifted else (0, 0)
        pts = " ".join(f"{x + dx:.2f},{y + dy:.2f}" for x, y in poly)
        out += f'<polygon points="{pts}" fill="{colors[k]}"/>'
    out += nib(cx, cy + 2, r * 0.66, colors[2])
    w, h = 2 * R + 16 + lift, 2 * R + 16
    if italic:
        sk = f"matrix(1 0 {-SLANT:.4f} 1 {cy * SLANT:.2f} 0)"
        out = f'<g transform="{sk}">{out}</g>'
        w += 0
    # shift down by lift so nothing clips at the top
    return f'<g transform="translate(0,{lift})">{out}</g>', w + 4, h + lift


def nib(cx, cy, k, colour, _unused=None):
    """Classic fountain-pen nib pointing up (the Cosign pen, carried over).
    Convex sides flare to shoulders, then taper to a neat rounded base. Slit runs from the
    breather hole to (not through) the tip. Single colour; cuts are real holes."""
    tip, base = cy - k, cy + k
    shy, sw_ = cy + 0.22 * k, 0.52 * k          # shoulder height / half-width
    bw = 0.30 * k                               # base half-width
    body = (f"M{cx:.2f} {tip:.2f} "
            f"C{cx + 0.16 * k:.2f} {tip + 0.50 * k:.2f} {cx + sw_:.2f} {cy - 0.18 * k:.2f} {cx + sw_:.2f} {shy:.2f} "
            f"L{cx + bw + 0.04 * k:.2f} {base - 0.16 * k:.2f} "
            f"Q{cx + bw:.2f} {base:.2f} {cx + bw - 0.14 * k:.2f} {base:.2f} "
            f"L{cx - bw + 0.14 * k:.2f} {base:.2f} "
            f"Q{cx - bw:.2f} {base:.2f} {cx - bw - 0.04 * k:.2f} {base - 0.16 * k:.2f} "
            f"L{cx - sw_:.2f} {shy:.2f} "
            f"C{cx - sw_:.2f} {cy - 0.18 * k:.2f} {cx - 0.16 * k:.2f} {tip + 0.50 * k:.2f} {cx:.2f} {tip:.2f} Z")
    hr, hy, sl = 0.12 * k, cy + 0.10 * k, 0.045 * k
    hole = f"M{cx + hr:.2f} {hy:.2f} a{hr:.2f} {hr:.2f} 0 1 0 {-2 * hr:.2f} 0 a{hr:.2f} {hr:.2f} 0 1 0 {2 * hr:.2f} 0 Z"
    slit = (f"M{cx - sl:.2f} {hy:.2f} L{cx + sl:.2f} {hy:.2f} L{cx + sl * 0.4:.2f} {tip + 0.10 * k:.2f} "
            f"L{cx - sl * 0.4:.2f} {tip + 0.10 * k:.2f} Z")
    return f'<path d="{body} {hole} {slit}" fill="{colour}" fill-rule="evenodd"/>'


def palette(mono=None, rev=False):
    base = mono or (WHITE if rev else ONYX)
    g = mono or GREEN
    o = mono or ORANGE
    return [g, g, base, base, base, o]          # S0..S5


# ───────── wordmarks ─────────
PTS = {}
CONT = {}


def d_key(pen):
    return pen.getCommands()


XMODE = ["gradient-green"]
GRAD = [[(0.0, "#005A03"), (0.55, GREEN), (1.0, "#2FD12A")]]   # green glow (single hue)   # optional custom stops: [(offset, colour), ...]


def word(font, text, size, x, base, fill, tracking=0.0, orange_x=None):
    """Render text; if orange_x is a colour, the X's rising stroke is painted in it."""
    glyphs, w = font.runs(text, size, x, base, tracking)
    out = ""
    for ch, d, (x0, y0, x1, y1) in glyphs:
        out += f'<path d="{d}" fill="{fill}"/>'
        if ch in "xX" and orange_x:
            # band along the rising diagonal (bottom-left -> top-right)
            gw = x1 - x0
            band = gw * 0.30
            pts = (f"{x0 - band:.2f},{y1:.2f} {x0 + band:.2f},{y1 + 2:.2f} "
                   f"{x1 + band:.2f},{y0:.2f} {x1 - band:.2f},{y0 - 2:.2f}")
            # widen into a proper strip around the diagonal
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            nx, ny = (y1 - y0), (x1 - x0)
            L = math.hypot(nx, ny); nx, ny = nx / L * gw * 0.15, ny / L * gw * 0.15
            pts = (f"{x0 - nx - 4:.2f},{y1 - ny + 4:.2f} {x1 - nx + 4:.2f},{y0 - ny - 4:.2f} "
                   f"{x1 + nx + 4:.2f},{y0 + ny - 4:.2f} {x0 + nx - 4:.2f},{y1 + ny + 4:.2f}")
            # band that follows the real rising stroke: foot at bottom-left, head at top-right
            f, e, ext = gw * 0.41, 0.6, (y1 - y0) * 0.06
            k = (x1 - f - x0) / (y1 - y0)            # horizontal drift per unit height
            yb, yt = y1 + ext, y0 - ext
            xb, xt = x0 - k * ext, x1 - f + k * ext   # left edge of the stroke at bottom / top
            pts = (f"{xb - e:.2f},{yb:.2f} {xb + f + e:.2f},{yb:.2f} "
                   f"{xt + f + e:.2f},{yt:.2f} {xt - e:.2f},{yt:.2f}")
            cid, mode = uid(), XMODE[0]
            band = f'<polygon points="{pts}"/>'
            if mode == "none":
                pass
            elif mode in ("gradient", "gradient-green"):
                gid = uid()
                # exact rising stroke from the outline: foot = leftmost points on the baseline,
                # head = rightmost points on the cap line
                P = PTS[d]
                tol = (y1 - y0) * 0.03
                midx = (x0 + x1) / 2
                foot = [px for px, py in P if py > y1 - tol and px < midx]
                head = [px for px, py in P if py < y0 + tol and px > midx]
                fl, fr, hl, hr = min(foot), max(foot), min(head), max(head)
                stroke = f"{fl:.2f},{y1:.2f} {fr:.2f},{y1:.2f} {hr:.2f},{y0:.2f} {hl:.2f},{y0:.2f}"
                gh = gw * 0.07
                ext = (y1 - y0) * 0.1
                kx = ((hl - fl) / (y1 - y0))           # drift of the stroke edges per unit height
                pts_k = (f"{fl - gh - kx * ext:.2f},{y1 + ext:.2f} {fr + gh - kx * ext:.2f},{y1 + ext:.2f} "
                         f"{hr + gh + kx * ext:.2f},{y0 - ext:.2f} {hl - gh + kx * ext:.2f},{y0 - ext:.2f}")
                # remove the black "/" under the gradient: redraw the black X with the band cut out
                out = out[: out.rfind('<path d=')]
                knock = uid()
                out += (f'<clipPath id="{knock}"><path clip-rule="evenodd" d="M{x0 - 50:.1f} {y0 - 50:.1f} '
                        f'H{x1 + 50:.1f} V{y1 + 50:.1f} H{x0 - 50:.1f} Z M{pts_k.replace(" ", " L")} Z"/></clipPath>'
                        f'<path d="{d}" fill="{fill}" clip-path="url(#{knock})"/>')
                out += (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x0 + f / 2:.1f}" y1="{y1:.1f}" x2="{x1 - f / 2:.1f}" y2="{y0:.1f}">' +
                        ("".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GRAD[0]) if GRAD[0] else
                         f'<stop offset="0.2" stop-color="{GREEN if mode == "gradient-green" else fill}"/><stop offset="0.9" stop-color="{orange_x}"/>')
                        + '</linearGradient>'
                        f'<polygon points="{stroke}" fill="url(#{gid})" stroke="url(#{gid})" stroke-width="0.6" stroke-linejoin="round"/>')
            elif mode == "tip":
                # only the upper-right end of the rising stroke, cut square across the stroke
                tx, ty = x0 + (x1 - x0) * 0.62, y1 + (y0 - y1) * 0.62
                ux, uy = (x1 - x0), (y0 - y1); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
                big = gw
                tip = (f"{tx - uy * big:.2f},{ty + ux * big:.2f} {tx + uy * big:.2f},{ty - ux * big:.2f} "
                       f"{tx + uy * big + ux * big:.2f},{ty - ux * big + uy * big:.2f} {tx - uy * big + ux * big:.2f},{ty + ux * big + uy * big:.2f}")
                c2 = uid()
                out += (f'<clipPath id="{cid}">{band}</clipPath><clipPath id="{c2}"><polygon points="{tip}"/></clipPath>'
                        f'<g clip-path="url(#{c2})"><path d="{d}" fill="{orange_x}" clip-path="url(#{cid})"/></g>')
            elif mode == "gap":
                # orange stroke crosses OVER the black one with a small cut, like the hex corners
                out = out[: out.rfind('<path d=')]          # drop the solid X just drawn
                gpad = gw * 0.07
                nx2, ny2 = nx / math.hypot(nx, ny) * (math.hypot(nx, ny) + gpad), ny / math.hypot(nx, ny) * (math.hypot(nx, ny) + gpad)
                wide = (f"{x0 - nx2 - 4:.2f},{y1 - ny2 + 4:.2f} {x1 - nx2 + 4:.2f},{y0 - ny2 - 4:.2f} "
                        f"{x1 + nx2 + 4:.2f},{y0 + ny2 - 4:.2f} {x0 + nx2 - 4:.2f},{y1 + ny2 + 4:.2f}")
                c2 = uid()
                out += (f'<clipPath id="{c2}"><path clip-rule="evenodd" d="M{x0 - 50:.1f} {y0 - 50:.1f} H{x1 + 50:.1f} V{y1 + 50:.1f} H{x0 - 50:.1f} Z '
                        f'M{wide.replace(" ", " L")} Z"/></clipPath>'
                        f'<path d="{d}" fill="{fill}" clip-path="url(#{c2})"/>'
                        f'<clipPath id="{cid}">{band}</clipPath><path d="{d}" fill="{orange_x}" clip-path="url(#{cid})"/>')
            else:
                out += (f'<clipPath id="{cid}">{band}</clipPath>'
                        f'<path d="{d}" fill="{orange_x}" clip-path="url(#{cid})"/>')
    return out, w


def word_oa(font, text, size, x, base, fill, tracking=0.0, mono=None, overlap=-0.25, gap_k=0.07):
    """O and A interlock: the A's left leg crosses OVER the O's right side with a clean cut
    (same cut language as the X and the hex). The A's tip is split like a pen nib."""
    glyphs, w = font.runs(text, size, x, base, tracking)
    io = next(i for i, g in enumerate(glyphs) if g[0] in "Oo")
    ia = io + 1
    (_, dO, (ox0, oy0, ox1, oy1)), (_, dA, (ax0, ay0, ax1, ay1)) = glyphs[io], glyphs[ia]
    bbox = lambda c: (min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c))
    area = lambda c: (bbox(c)[2] - bbox(c)[0]) * (bbox(c)[3] - bbox(c)[1])
    cO, cA = sorted(CONT[dO], key=area), sorted(CONT[dA], key=area)
    o_out, o_in, a_out, a_in = cO[-1], cO[0], cA[-1], cA[0]
    stem = bbox(o_out)[2] - bbox(o_in)[2]                       # O right-side thickness
    tol = (oy1 - oy0) * 0.03
    H = ay1 - ay0
    foot = [p[0] for p in a_out if p[1] > ay1 - tol and p[0] < (ax0 + ax1) / 2]
    head = [p[0] for p in a_out if p[1] < ay0 + tol]
    afl, afr, hl, hr = min(foot), max(foot), min(head), max(head)
    # slide the A (and everything after it) left so its left leg sits over the O's right side
    shift = (afl - bbox(o_out)[2]) + stem * (1 + overlap)
    T = lambda xx: xx - shift
    afl, afr, hl, hr, ax0, ax1 = map(T, (afl, afr, hl, hr, ax0, ax1))
    hc = (hl + hr) / 2
    g = (ox1 - ox0) * gap_k
    ext = H * 0.1
    kx = (hl - afl) / H
    leg = lambda pad: (f"{afl - pad - kx * ext:.2f},{ay1 + ext:.2f} {afr + pad - kx * ext:.2f},{ay1 + ext:.2f} "
                       f"{hc + pad + kx * ext:.2f},{ay0 - ext:.2f} {hl - pad + kx * ext:.2f},{ay0 - ext:.2f}")
    k1 = uid()
    knock = (f'<clipPath id="{k1}"><path clip-rule="evenodd" d="M{ox0 - 60:.1f} {oy0 - 60:.1f} H{ox1 + 60:.1f} '
             f'V{oy1 + 60:.1f} H{ox0 - 60:.1f} Z M{leg(g).replace(" ", " L")} Z"/></clipPath>')
    # pen-nib slit from the A tip to the top of its counter
    ct = min(a_in, key=lambda p: p[1]); ctx, cty = T(ct[0]), ct[1]
    ws = stem * 0.28
    slit = (f"{hc - ws / 2:.2f},{ay0 - 3:.2f} {hc + ws / 2:.2f},{ay0 - 3:.2f} "
            f"{ctx + ws / 2:.2f},{cty + 1.5:.2f} {ctx - ws / 2:.2f},{cty + 1.5:.2f}")
    k2 = uid()
    nib = (f'<clipPath id="{k2}"><path clip-rule="evenodd" d="M{ax0 - 60:.1f} {ay0 - 60:.1f} H{ax1 + 60:.1f} '
           f'V{ay1 + 60:.1f} H{ax0 - 60:.1f} Z M{slit.replace(" ", " L")} Z"/></clipPath>')
    if mono:
        paint, defs = mono, ""
    else:
        gid = uid()
        defs = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{ox0:.1f}" y1="{oy1:.1f}" '
                f'x2="{ax1:.1f}" y2="{ay0:.1f}"><stop offset="0" stop-color="#005A03"/>'
                f'<stop offset="0.5" stop-color="{fill}"/><stop offset="1" stop-color="#2FD12A"/></linearGradient>')
        paint = f"url(#{gid})"
    out = "".join(f'<path d="{d}" fill="{fill}"/>' for i, (ch, d, _) in enumerate(glyphs) if i < io)
    out += (defs + knock + nib +
            f'<path d="{dO}" fill="{paint}" clip-path="url(#{k1})"/>'
            f'<g transform="translate({-shift:.2f},0)"><path d="{dA}" fill="{paint}" '
            f'clip-path="url(#{k2})" transform="translate({shift:.2f},0)"/></g>')
    # the nib clip is in shifted coords; draw A shifted by wrapping
    # nib clip built in the A's own (unshifted) coordinates; applied on the A path inside the shifted group
    U = lambda xx: xx + shift
    # pen nib: short slit down from the tip ending in a round breather hole (like a real nib)
    wsl = stem * 0.13
    L = 0.42                                         # slit length as a share of tip -> counter
    ex, ey = hc + (ctx - hc) * L, ay0 + (cty - ay0) * L
    r = wsl * 1.55
    # counter-clockwise outline: slit + circle cut as separate subpaths, both reversed vs the frame
    slit_u = (f"{U(hc - wsl / 2):.2f},{ay0 - 3:.2f} {U(ex - wsl / 2):.2f},{ey:.2f} "
              f"{U(ex + wsl / 2):.2f},{ey:.2f} {U(hc + wsl / 2):.2f},{ay0 - 3:.2f}")
    hole = (f"M{U(ex) + r:.2f} {ey + r * 0.6:.2f} a{r:.2f} {r:.2f} 0 1 0 {-2 * r:.2f} 0 "
            f"a{r:.2f} {r:.2f} 0 1 0 {2 * r:.2f} 0 Z")
    k3 = uid()
    nib_u = (f'<clipPath id="{k3}"><path clip-rule="evenodd" d="M{U(ax0) - 60:.1f} {ay0 - 60:.1f} H{U(ax1) + 60:.1f} '
             f'V{ay1 + 60:.1f} H{U(ax0) - 60:.1f} Z M{slit_u.replace(" ", " L")} Z {hole}"/></clipPath>')
    out = out.replace(f'<g transform="translate({-shift:.2f},0)"><path d="{dA}" fill="{paint}" '
                      f'clip-path="url(#{k2})" transform="translate({shift:.2f},0)"/></g>',
                      f'<g transform="translate({-shift:.2f},0)"><path d="{dA}" fill="{paint}"/></g>')
    out += f'<g transform="translate({-shift:.2f},0)">' + "".join(
        f'<path d="{d}" fill="{fill}"/>' for i, (ch, d, _) in enumerate(glyphs) if i > ia) + '</g>'
    return out, w - shift


# ───────── lockups (3 variations) ─────────
def v_a(mono=None, rev=False):
    """A — Mark + ONYX LOANS (italic caps). Closest to Split O, X carries the orange."""
    mb, mw, mh = hex_o(palette(mono, rev))
    size = mh * 0.60 / BARLOW.cap
    base = mh / 2 + size * BARLOW.cap / 2 + 2
    x = mw + size * 0.20
    c1 = mono or (WHITE if rev else ONYX)
    w1, a = word(BARLOW, "ONYX", size, x, base, c1, 1.5, orange_x=None if mono else ORANGE)
    w2, b = word_oa(BARLOW, "LOANS", size, x + a + size * 0.2, base, mono or GREEN, 1.5, mono=mono)
    return mb + w1 + w2, x + a + size * 0.2 + b + 4, mh


def slab(x0, x1, y0, y1, fill):
    """Forward-slanted block at the same 12-degree slant as the type and the hex."""
    k = (y1 - y0) * SLANT
    return (f'<polygon points="{x0 + k:.2f},{y0:.2f} {x1 + k:.2f},{y0:.2f} {x1:.2f},{y1:.2f} {x0:.2f},{y1:.2f}" '
            f'fill="{fill}"/>')


def v_d(mono=None, rev=False):
    """D — ONYX as free type + LOANS knocked out of a GoLoans-style green slab with speed stripes.
    Slab height = hex height; stripe gaps = hex segment gaps; slant = type slant."""
    mb, mw, mh = hex_o(palette(mono, rev))
    size = mh * 0.56 / BARLOW.cap
    cap = size * BARLOW.cap
    base = mh / 2 + cap / 2 + 2
    x = mw + size * 0.20
    c1 = mono or (WHITE if rev else ONYX)
    w1, a = word(BARLOW, "ONYX", size, x, base, c1, 1.5, orange_x=None if mono else ORANGE)
    # slab spans the hex's flat-side band so the two units read as equals
    y0, y1 = base - cap - cap * 0.30, base + cap * 0.30
    sx0 = x + a + size * 0.16
    pad = size * 0.16
    k = (y1 - y0) * SLANT
    # measure LOANS first
    _, lw = word_oa(BARLOW, "LOANS", size, 0, 0, WHITE, 1.5, mono=WHITE)
    sx1 = sx0 + k * 0.5 + pad + lw + pad + k * 0.5
    slab_fill = mono or GREEN
    text_fill = (WHITE if mono != WHITE else ONYX) if mono else WHITE
    gid = uid()
    if mono:
        body_slab = slab(sx0, sx1, y0, y1, slab_fill)
    else:
        body_slab = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{sx0:.1f}" y1="0" x2="{sx1 + k:.1f}" y2="0">'
                     f'<stop offset="0" stop-color="{GREEN_DK}"/><stop offset="0.35" stop-color="{GREEN}"/>'
                     f'<stop offset="1" stop-color="#00A307"/></linearGradient>' + slab(sx0, sx1, y0, y1, f"url(#{gid})"))
    # centre LOANS optically in the slab: slab centre at cap mid-height vs text centre (italic shifts it right)
    ymid = base - cap / 2
    slab_cx = (sx0 + sx1) / 2 + (y1 - ymid) * SLANT
    tx = slab_cx - lw / 2 - cap * 0.5 * 0.21 * 0.5
    w2, _ = word_oa(BARLOW, "LOANS", size, tx, base, text_fill, 1.5, mono=text_fill)
    # speed stripes: gap = hex segment gap scaled to this lockup, widths step down
    g = 5 * mh / 140
    st1 = sx1 + g * 1.6
    w_a, w_b = size * 0.095, size * 0.065
    stripes = (slab(st1, st1 + w_a, y0, y1, mono or GREEN_LT) +
               slab(st1 + w_a + g * 1.6, st1 + w_a + g * 1.6 + w_b, y0, y1, mono or GREEN_DK))
    end = st1 + w_a + g * 1.6 + w_b + k + 4
    return mb + w1 + body_slab + w2 + stripes, end, mh


def v_b(mono=None, rev=False):
    """B — The mark IS the O: [O]NYX, with LOANS as a tracked tag under NYX."""
    mb, mw, mh = hex_o(palette(mono, rev))
    size = mh * 0.84 / BARLOW9.cap
    base = mh - 6
    x = mw - 4
    c1 = mono or (WHITE if rev else ONYX)
    w1, a = word(BARLOW9, "NYX", size, x, base, c1, 2, orange_x=None if mono else ORANGE)
    tsize = size * 0.34
    w2, b = word(BARLOW, "LOANS", tsize, 0, 0, mono or GREEN, tsize * 0.55)
    # right-align LOANS under NYX, below baseline
    tx = x + a - b
    w2, b = word(BARLOW, "LOANS", tsize, tx - 4, base + tsize * BARLOW.cap + 14, mono or GREEN, tsize * 0.55)
    return mb + w1 + w2, x + a + 6, base + tsize * BARLOW.cap + 18


def v_c(mono=None, rev=False):
    """C — Upright, friendly: straight hex O + lowercase 'onyx loans' (closest to the reference)."""
    mb, mw, mh = hex_o(palette(mono, rev), italic=False, lift=4)
    size = mh * 0.86 / MANROPE.xh * 0.62
    base = mh / 2 + size * MANROPE.xh / 2 + 2
    x = mw + size * 0.18
    c1 = mono or (WHITE if rev else ONYX)
    w1, a = word(MANROPE, "onyx", size, x, base, c1, -1, orange_x=None if mono else ORANGE)
    w2, b = word(MANROPE, "loans", size, x + a + size * 0.22, base, mono or GREEN, -1)
    return mb + w1 + w2, x + a + size * 0.22 + b + 4, mh


VARS = [("a", "A — HEX SPLIT O + ONYX LOANS", v_a),
        ("b", "B — THE MARK IS THE O", v_b),
        ("c", "C — UPRIGHT + FRIENDLY", v_c),
        ("d", "D — ONYX + LOANS SLAB", v_d)]


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


for key, title, fn in VARS:
    export(f"onyx-v4{key}-logo-horizontal", *fn())
    export(f"onyx-v4{key}-logo-reversed", *fn(rev=True), bg=ONYX)
    export(f"onyx-v4{key}-logo-one-colour", *fn(mono=ONYX))

mk = hex_o(palette())
export("onyx-v4-mark", *mk)
mkr = hex_o(palette(rev=True))
icon = svg(200, 200, place(mkr[0], mkr[1], mkr[2], 34, 34, 132, 132), bg=ONYX, rx=44)
open(f"{OUT}/onyx-v4-app-icon.svg", "w").write(icon)
cairosvg.svg2png(bytestring=icon.encode(), write_to=f"{OUT}/onyx-v4-app-icon.png", scale=2)

# ── board ──
W, H = 1600, 1240
b = f'<rect width="{W}" height="{H}" fill="#FAFBFA"/>'
b += label("ONYX LOANS — HEX SPLIT O", 80, 84, 22, INK, 6, "start", 600)
b += label("Onyx half = the borrower (solid base). Green half = the cosigner / lender, lifted up and forward. "
           "Orange = the GO.", 80, 118, 15, "#5B6B7C", 0, "start", 400)
b += label("Hexagon = a cut onyx crystal holding the Cosign pen nib (the signature). The X glows green; in LOANS the A links over the O.", 80, 142, 15, "#5B6B7C", 0, "start", 400)
rows = [(180, 230), (450, 230), (720, 200)]
for (key, title, fn), (y, hh) in zip(VARS, rows):
    body, w, h = fn()
    b += label(title, 80, y + 18, 14, "#8A979F", 3, "start")
    b += place(body, w, h, 80, y + 34, 1000, hh - 50)
    rb, rw, rh = fn(rev=True)
    b += f'<rect x="1120" y="{y + 30}" width="400" height="{hh - 40}" rx="16" fill="{ONYX}"/>'
    b += place(rb, rw, rh, 1150, y + 50, 340, hh - 80)
b += f'<line x1="80" y1="950" x2="1520" y2="950" stroke="#E2E6E3"/>'
tiles = [("PRIMARY MARK", mk, None), ("ONE COLOUR", v_a(mono=ONYX), None),
         ("ON GREEN", v_a(mono=WHITE), GREEN), ("DIGITAL ICON", None, None)]
tw = 1440 / 4
for i, (name, data, bg) in enumerate(tiles):
    x0 = 80 + i * tw
    if bg:
        b += f'<rect x="{x0 + 14}" y="975" width="{tw - 28}" height="180" rx="16" fill="{bg}"/>'
    if data:
        b += place(data[0], data[1], data[2], x0 + 40, 995, tw - 80, 140)
    else:
        b += f'<rect x="{x0 + tw / 2 - 75}" y="985" width="150" height="150" rx="34" fill="{ONYX}"/>'
        b += place(mkr[0], mkr[1], mkr[2], x0 + tw / 2 - 50, 1010, 100, 100)
        b += f'<image href="{OUT}/onyx-v4-app-icon.png" x="{x0 + tw / 2 + 92}" y="1100" width="32" height="32"/>'
        b += f'<image href="{OUT}/onyx-v4-app-icon.png" x="{x0 + tw / 2 + 130}" y="1116" width="16" height="16"/>'
    b += label(name, x0 + tw / 2, 1195, 14)
cairosvg.svg2png(bytestring=svg(W, H, b).encode(), write_to=f"{OUT}/board-v4-hex-split-o.png", unsafe=True)
print("ok")
