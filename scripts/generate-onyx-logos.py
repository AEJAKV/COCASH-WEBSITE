"""Onyx Loans logo system v2 — interlocking rings + onyx gem + cashback arrow."""
import math, os, sys
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

# Brand palette (from index.html Onyx theme)
BLUE = "#0F58C9"     # trust / the borrower
NAVY = "#103B7A"     # stability / wordmark
ORANGE = "#FF8A1D"   # energy / the cosigner & lender, cashback
ONYX = "#0A1F3F"     # the stone itself
SKY = "#5B9BFF"      # blue lifted for dark backgrounds
WHITE = "#FFFFFF"

FONTS = "/usr/share/fonts/truetype/google-fonts/"


class Font:
    def __init__(self, file):
        f = TTFont(FONTS + file)
        self.gs, self.cmap, self.upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm

    def path(self, text, size, x, y, tracking=0.0):
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        cx = 0.0
        for ch in text:
            g = self.gs[self.cmap[ord(ch)]]
            g.draw(TransformPen(pen, (s, 0, 0, -s, x + cx, y)))
            cx += g.width * s + tracking
        return pen.getCommands(), cx - tracking


BOLD = Font("Poppins-Bold.ttf")
SEMI = Font("Poppins-SemiBold.ttf") if os.path.exists(FONTS + "Poppins-SemiBold.ttf") else BOLD

# ---------- mark geometry (200x200 design box) ----------
R, SW = 46, 16
CB, CO = (78, 100), (122, 100)          # blue / orange ring centres


def pt(c, deg, r=R):
    a = math.radians(deg)
    return c[0] + r * math.cos(a), c[1] + r * math.sin(a)


def arc(c, a0, a1, r=R):
    """SVG arc path from angle a0 to a1 (degrees, screen coords, a1>a0 = clockwise)."""
    x0, y0 = pt(c, a0, r)
    x1, y1 = pt(c, a1, r)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} {sweep} {x1:.2f} {y1:.2f}"


LEAF = ("M0,-12 L3,-6 L8,-8 L6,-1 L11,-3 L9,2 L12,4 L4,7 L5,10 L1,9 L1,14 L-1,14 "
        "L-1,9 L-5,10 L-4,7 L-12,4 L-9,2 L-11,-3 L-6,-1 L-8,-8 L-3,-6 Z")

# crossings: blue passes OVER at the top, orange passes OVER at the bottom (a woven link)
X_TOP_B, X_BOT_O = -61.4, 118.6          # angles on blue / orange rings


def gem(cx, cy, w, h, dark, mid, light):
    """Faceted onyx: crown (top band) + pavilion (point) with light/dark facets."""
    t = h * 0.30                          # crown height
    hw, tw = w / 2, w * 0.26              # half width, half table width
    top, gird, cul = cy - h / 2, cy - h / 2 + t, cy + h / 2
    P = lambda *xy: " ".join(f"{cx + x:.2f},{y:.2f}" for x, y in zip(xy[::2], xy[1::2]))
    return f'''
  <polygon points="{P(-tw, top, tw, top, hw, gird, 0, cul, -hw, gird)}" fill="{dark}"/>
  <polygon points="{P(-tw, top, tw, top, tw * 0.55, gird, -tw * 0.55, gird)}" fill="{light}"/>
  <polygon points="{P(tw, top, hw, gird, tw * 0.55, gird)}" fill="{mid}"/>
  <polygon points="{P(-tw * 0.55, gird, tw * 0.55, gird, 0, cul)}" fill="{mid}"/>
  <polygon points="{P(tw * 0.55, gird, hw, gird, 0, cul)}" fill="{light}" opacity="0.55"/>'''


def mark(uid, ring_b, ring_o, gem_dark, gem_mid, gem_light, ox=0, oy=0, s=1.0):
    # blue ring: open at lower-left (open door — no credit check)
    blue = arc(CB, 150, 470)
    # orange ring: runs anticlockwise and ends in an arrow heading up-right
    end_deg = 20
    orange = arc(CO, 330, end_deg)        # a1 < a0 -> anticlockwise sweep
    ex, ey = pt(CO, end_deg)
    d = (math.sin(math.radians(end_deg)), -math.cos(math.radians(end_deg)))  # tangent
    n = (-d[1], d[0])
    tip = (ex + d[0] * 17, ey + d[1] * 17)
    b1 = (ex + n[0] * 14, ey + n[1] * 14)
    b2 = (ex - n[0] * 14, ey - n[1] * 14)
    arrow = f"M{b1[0]:.2f} {b1[1]:.2f} L{tip[0]:.2f} {tip[1]:.2f} L{b2[0]:.2f} {b2[1]:.2f} Z"
    tx, ty = pt(CO, 330)

    gx, gy, gw, gh = 100, 102, 27, 31
    G = 19                                   # half-gap (deg) where a ring dips under
    # orange dips under blue at the top crossing (-118.6 -> 241.4 on the anticlockwise run)
    o1, o2 = arc(CO, 330, 241.4 + G), arc(CO, 241.4 - G, end_deg)
    # blue dips under orange at the bottom crossing (61.4 -> 421.4)
    b1_, b2_ = arc(CB, 150, 421.4 - G), arc(CB, 421.4 + G, 470)
    return f'''<g transform="translate({ox},{oy}) scale({s})">
  <path d="{o1}" fill="none" stroke="{ring_o}" stroke-width="{SW}"/>
  <path d="{o2}" fill="none" stroke="{ring_o}" stroke-width="{SW}"/>
  <circle cx="{tx:.2f}" cy="{ty:.2f}" r="{SW/2}" fill="{ring_o}"/>
  <path d="{arrow}" fill="{ring_o}" stroke="{ring_o}" stroke-width="3" stroke-linejoin="round"/>
  <path d="{b1_}" fill="none" stroke="{ring_b}" stroke-width="{SW}"/>
  <circle cx="{pt(CB,150)[0]:.2f}" cy="{pt(CB,150)[1]:.2f}" r="{SW/2}" fill="{ring_b}"/>
  <path d="{b2_}" fill="none" stroke="{ring_b}" stroke-width="{SW}"/>
  <circle cx="{pt(CB,470)[0]:.2f}" cy="{pt(CB,470)[1]:.2f}" r="{SW/2}" fill="{ring_b}"/>
  {gem(gx, gy, gw, gh, gem_dark, gem_mid, gem_light)}
</g>'''


# tight bounds of the mark inside the 200 box
MX0, MY0, MW, MH = 22, 44, 162, 112


def svg(w, h, body, bg=None, rx=0):
    b = f'<rect width="{w}" height="{h}" rx="{rx}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">{b}{body}</svg>')


def wordmark(x, base, size, c_onyx, c_loans, leaf_c):
    d1, w1 = BOLD.path("Onyx", size, x, base, tracking=-1)
    space = size * 0.24
    d2, w2 = SEMI.path("Loans", size, x + w1 + space, base, tracking=-0.5)
    end = x + w1 + space + w2
    return f'<path d="{d1}" fill="{c_onyx}"/><path d="{d2}" fill="{c_loans}"/>', end - x


def palette(dark_bg):
    if dark_bg:
        return dict(ring_b=SKY, ring_o=ORANGE, gem_dark="#1A3F7A", gem_mid=SKY, gem_light=WHITE)
    return dict(ring_b=BLUE, ring_o=ORANGE, gem_dark=ONYX, gem_mid=NAVY, gem_light=BLUE)


def horizontal(uid, dark=False, mono=None):
    p = palette(dark)
    if mono:
        p = dict(ring_b=mono, ring_o=mono, gem_dark=mono, gem_mid=mono, gem_light=mono)
    m = mark(uid, ox=-MX0 + 10, oy=-MY0 + 10, **p)
    c1 = mono or (WHITE if dark else NAVY)
    c2 = mono or ORANGE
    wm, ww = wordmark(MW + 34, 10 + MH * 0.70, 76, c1, c2, mono or (SKY if dark else BLUE))
    return svg(MW + 34 + ww + 14, MH + 20, m + wm, bg="#0B2347" if dark else None)


def stacked(uid, dark=False):
    p = palette(dark)
    size = 64
    _, ww = wordmark(0, 0, size, "", "", "")
    W = max(ww, MW) + 40
    m = mark(uid, ox=(W - MW) / 2 - MX0, oy=-MY0 + 14, **p)
    wm, _ = wordmark((W - ww) / 2, MH + 14 + 78, size, WHITE if dark else NAVY, ORANGE, "")
    return svg(W, MH + 14 + 104, m + wm, bg="#0B2347" if dark else None)


def tagline(uid, dark=False):
    """Primary lockup + leaf-led tagline under the wordmark."""
    p = palette(dark)
    m = mark(uid, ox=-MX0 + 10, oy=-MY0 + 10, **p)
    x0 = MW + 34
    wm, ww = wordmark(x0, 10 + MH * 0.56, 76, WHITE if dark else NAVY, ORANGE, "")
    tsize = 19.5
    ld, lw = SEMI.path("COSIGNER & LENDER MATCHING", tsize, 0, 0, tracking=3.2)
    sc = (ww - 30) / lw                       # tagline spans under the wordmark
    leaf_c = SKY if dark else BLUE
    td, _ = SEMI.path("COSIGNER & LENDER MATCHING", tsize * sc, x0 + 30, 10 + MH * 0.92, tracking=3.2 * sc)
    leaf = f'<path d="{LEAF}" transform="translate({x0 + 11},{10 + MH * 0.92 - tsize * sc * 0.36:.2f}) scale({tsize * sc / 26:.3f})" fill="{ORANGE}"/>'
    body = m + wm + f'<path d="{td}" fill="{leaf_c}"/>' + leaf
    return svg(x0 + ww + 14, MH + 20, body, bg="#0B2347" if dark else None)


def icon(uid, dark=False):
    p = palette(dark)
    s = 168 / MW
    body = mark(uid, ox=16 - MX0 * s, oy=100 - (MY0 + MH / 2) * s, s=s, **p)
    return svg(200, 200, body, bg="#0B2347" if dark else None, rx=44 if dark else 0)


variants = {
    "onyx-loans-logo-horizontal": horizontal("a"),
    "onyx-loans-logo-horizontal-reversed": horizontal("b", dark=True),
    "onyx-loans-logo-stacked": stacked("c"),
    "onyx-loans-logo-tagline": tagline("d"),
    "onyx-loans-logo-mono-navy": horizontal("e", mono=NAVY),
    "onyx-loans-icon": icon("f"),
    "onyx-loans-icon-app": icon("g", dark=True),
}
for name, s in variants.items():
    open(f"{OUT}/{name}.svg", "w").write(s)
    cairosvg.svg2png(bytestring=s.encode(), write_to=f"{OUT}/{name}.png", scale=2)
print("done:", ", ".join(variants))
