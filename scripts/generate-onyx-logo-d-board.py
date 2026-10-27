import sys, runpy, cairosvg
S, F = sys.argv[1], sys.argv[2]
sys.argv = ["x", S + "/v4", F]
g = runpy.run_path(S + "/onyx_v4.py")
W, H = 1600, 1100
L = g["label"]; P = g["place"]; ONYX = g["ONYX"]; GREEN = g["GREEN"]; WHITE = g["WHITE"]
b = f'<rect width="{W}" height="{H}" fill="#FAFBFA"/>'
b += L("ONYX LOANS — LOGO D", 80, 84, 22, g["INK"], 6, "start", 600)
b += L("ONYX stays free type with the green-glow X; LOANS sits in a GoLoans-style green slab, same 12° slant as the type and the hex.", 80, 118, 15, "#5B6B7C", 0, "start", 400)
b += L("Slab height matches the hex, stripe gaps match the hex gaps. The X's green stroke hands off into the slab: momentum, approval, funds fast.", 80, 142, 15, "#5B6B7C", 0, "start", 400)
d = g["v_d"]()
b += P(*d, 120, 190, 1360, 300)
b += '<line x1="80" y1="540" x2="1520" y2="540" stroke="#E2E6E3"/>'
b += f'<rect x="80" y="575" width="700" height="220" rx="18" fill="{ONYX}"/>' + P(*g["v_d"](rev=True), 120, 605, 620, 160)
b += P(*g["v_d"](mono=ONYX), 840, 605, 640, 160)
b += L("REVERSED", 430, 830, 14) + L("ONE COLOUR", 1160, 830, 14)
mk = g["hex_o"](g["palette"]()); mkr = g["hex_o"](g["palette"](rev=True))
b += P(*mk, 300, 870, 160, 160) + L("SYMBOL", 380, 1065, 14)
b += f'<rect x="700" y="870" width="160" height="160" rx="36" fill="{ONYX}"/>' + P(*mkr, 725, 895, 110, 110) + L("APP ICON", 780, 1065, 14)
b += f'<rect x="1040" y="890" width="460" height="120" rx="16" fill="{GREEN}"/>' + P(*g["v_d"](mono=WHITE), 1070, 910, 400, 80) + L("ON GREEN", 1270, 1065, 14)
cairosvg.svg2png(bytestring=g["svg"](W, H, b).encode(), write_to=S + "/v4/board-v4d-loans-slab.png", unsafe=True)
print("ok")
