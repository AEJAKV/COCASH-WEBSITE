import sys, runpy, cairosvg
S, F, OUTD = sys.argv[1], sys.argv[2], sys.argv[3]
sys.argv = ["x", S + "/v4tmp", F]
g = runpy.run_path(S + "/onyx_v4.py")
L = g["label"]; P = g["place"]; V = g["v_new"]; ONYX = g["ONYX"]; GREEN = g["GREEN"]; WHITE = g["WHITE"]
ex = g["export"]; ex.__globals__["OUT"] = OUTD
for k in ("track", "tag"):
    ex(f"onyx-new-{k}-logo-horizontal", *V(k))
    ex(f"onyx-new-{k}-logo-reversed", *V(k, rev=True), bg=ONYX)
    ex(f"onyx-new-{k}-logo-one-colour", *V(k, mono=ONYX))
W, H = 1600, 1020
b = f'<rect width="{W}" height="{H}" fill="#FAFBFA"/>' + L("ONYX LOANS — NEW CONCEPTS", 80, 80, 22, g["INK"], 6, "start", 600)
rows = [("track", "1 — INSTALLMENT TRACK", "Each segment is a repayment. Onyx first (the borrower's start), then green as it climbs: paying it off builds credit."),
        ("tag", "2 — CRYSTAL TAG", "LOANS sits in the onyx crystal, stretched: same 60° cuts as the symbol. The right point is the forward arrow.")]
for i, (k, t, d) in enumerate(rows):
    y = 120 + i * 440
    b += L(t, 80, y + 20, 16, g["INK"], 4, "start", 600) + L(d, 80, y + 46, 15, "#5B6B7C", 0, "start", 400)
    b += P(*V(k), 80, y + 70, 860, 300)
    b += f'<rect x="990" y="{y + 70}" width="530" height="170" rx="16" fill="{ONYX}"/>' + P(*V(k, rev=True), 1020, y + 90, 470, 130)
    b += P(*V(k, mono=ONYX), 1020, y + 260, 470, 110)
cairosvg.svg2png(bytestring=g["svg"](W, H, b).encode(), write_to=OUTD + "/board-new-concepts.png", unsafe=True)
print("ok")
