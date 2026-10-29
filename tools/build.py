"""Generate the GitHub profile SVG assets (dark + light) for Ward Keadan.

Design language follows the portfolio "Spec Sheet" system (DESIGN.md):
graphite plates, one-job accents (red = act, cyan = data, gold = results),
Big Shoulders Display / Saira / JetBrains Mono. Fonts are embedded as
per-file glyph subsets so every SVG renders identically inside <img>.
"""
import base64, io, json, os, sys
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools import subset as ftsubset

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets")
os.makedirs(OUT, exist_ok=True)

FONT_FILES = {
    "display": "big-shoulders-display-latin-900-normal.woff2",
    "body": "saira-latin-400-normal.woff2",
    "bodyb": "saira-latin-600-normal.woff2",
    "mono": "jetbrains-mono-latin-700-normal.woff2",
    "monom": "jetbrains-mono-latin-500-normal.woff2",
}
FAMILY = {"display": "WKDisplay", "body": "WKBody", "bodyb": "WKBodyB", "mono": "WKMono", "monom": "WKMonoM"}
FALLBACK = {
    "display": "'Arial Narrow',Impact,sans-serif",
    "body": "'Segoe UI',Helvetica,Arial,sans-serif",
    "bodyb": "'Segoe UI',Helvetica,Arial,sans-serif",
    "mono": "ui-monospace,Menlo,Consolas,monospace",
    "monom": "ui-monospace,Menlo,Consolas,monospace",
}


class Metric:
    def __init__(self, path):
        self.font = TTFont(path)
        self.upm = self.font["head"].unitsPerEm
        self.cmap = self.font.getBestCmap()
        self.hmtx = self.font["hmtx"].metrics

    def width(self, text, size, track=0.0):
        w = 0
        for ch in text:
            g = self.cmap.get(ord(ch))
            adv = self.hmtx[g][0] if g else self.upm * 0.5
            w += adv
        return w * size / self.upm + track * size * max(len(text) - 1, 0)


METRICS = {k: Metric(os.path.join(HERE, "fonts", f)) for k, f in FONT_FILES.items()}

THEMES = {
    "dark": dict(
        bg="#0f1114", panel="#171a1f", raised="#22262d", recess="#0b0d10", bevel="#3a404a",
        ink="#eceef1", ink2="#a7afb9", ink3="#8c95a0", rule="#2b3037", rule2="#3a404a",
        red="#c8202e", redt="#ff5a63", cyan="#3fd7ea", gold="#d9a441", goldt="#d9a441",
        grid="rgba(255,255,255,0.025)", onred="#ffffff", icon="#c9cfd6",
    ),
    "light": dict(
        bg="#f2f1ec", panel="#fbfaf7", raised="#e3e5e7", recess="#eceeec", bevel="#ffffff",
        ink="#121417", ink2="#424a53", ink3="#59616b", rule="#d4d6d6", rule2="#a7aeb5",
        red="#b3121f", redt="#b3121f", cyan="#00808f", gold="#c08a1e", goldt="#855c00",
        grid="rgba(18,20,23,0.05)", onred="#ffffff", icon="#2a3038",
    ),
}

ICONS = json.load(open(os.path.join(HERE, "icons.json")))


class SVG:
    def __init__(self, w, h, theme, title, desc=""):
        self.w, self.h, self.t, self.title, self.desc = w, h, THEMES[theme], title, desc
        self.parts, self.used, self.css = [], {}, []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, font, size, fill, anchor="start", track=0.0, cls="", upper=False, opacity=None):
        s = s.upper() if upper else s
        self.used.setdefault(font, set()).update(s)
        ls = f' letter-spacing="{track * size:.2f}"' if track else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        c = f' class="{cls}"' if cls else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FAMILY[font]},{FALLBACK[font]}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}"{ls}{op}{c}>{escape(s)}</text>'
        )
        return METRICS[font].width(s, size, track)

    def fontfaces(self):
        out = []
        for font, chars in self.used.items():
            opts = ftsubset.Options()
            opts.flavor = "woff2"
            opts.layout_features = ["kern", "liga"]
            opts.name_IDs = []
            opts.notdef_outline = True
            f = TTFont(os.path.join(HERE, "fonts", FONT_FILES[font]))
            sub = ftsubset.Subsetter(opts)
            sub.populate(text="".join(sorted(chars)) + " ")
            sub.subset(f)
            buf = io.BytesIO()
            f.flavor = "woff2"
            f.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            out.append(f"@font-face{{font-family:{FAMILY[font]};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
        return "".join(out)

    def render(self):
        style = self.fontfaces() + "".join(self.css)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(self.title)}</title><desc id="d">{escape(self.desc)}</desc>'
            f"<style>{style}</style>" + "".join(self.parts) + "</svg>"
        )


def wrap(text, font, size, maxw, track=0.0):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if METRICS[font].width(trial, size, track) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def plate(svg, x, y, w, h, c=16, fill=None, stroke=None):
    t = svg.t
    pts = f"{x+c},{y} {x+w},{y} {x+w},{y+h-c} {x+w-c},{y+h} {x},{y+h} {x},{y+c}"
    svg.add(f'<polygon points="{pts}" fill="{fill or t["panel"]}" stroke="{stroke or t["rule2"]}" stroke-width="1.5"/>')


def ticks(svg, x0, x1, y, step=12, color=None, long_every=5):
    t = svg.t
    d, i, x = [], 0, x0
    while x <= x1:
        L = 9 if i % long_every == 0 else 5
        d.append(f"M{x:.1f} {y}v{-L}")
        x += step
        i += 1
    svg.add(f'<path d="{"".join(d)}" stroke="{color or t["gold"]}" stroke-width="1.5" opacity="0.8"/>')


def clamps(svg, x, w, y):
    t = svg.t
    for cx in (x + 64, x + w - 64 - 46):
        svg.add(f'<rect x="{cx}" y="{y-5}" width="46" height="10" fill="{t["raised"]}" stroke="{t["rule2"]}" stroke-width="1"/>')
        svg.add(f'<circle cx="{cx+10}" cy="{y}" r="2" fill="{t["ink3"]}"/><circle cx="{cx+36}" cy="{y}" r="2" fill="{t["ink3"]}"/>')


def icon(svg, key, x, y, size, color):
    if key in ICONS:
        s = size / 24
        svg.add(f'<path transform="translate({x:.1f} {y:.1f}) scale({s:.4f})" d="{ICONS[key]["path"]}" fill="{color}"/>')
    elif key == "chip":
        s = size
        svg.add(
            f'<g transform="translate({x:.1f} {y:.1f})" fill="none" stroke="{color}" stroke-width="1.6">'
            f'<rect x="{s*0.22}" y="{s*0.22}" width="{s*0.56}" height="{s*0.56}"/>'
            + "".join(f'<path d="M{s*p} {s*0.04}v{s*0.18}M{s*p} {s*0.78}v{s*0.18}M{s*0.04} {s*p}h{s*0.18}M{s*0.78} {s*p}h{s*0.18}"/>' for p in (0.36, 0.64))
            + "</g>"
        )
    elif key == "api":
        svg.text(x + size / 2, y + size * 0.8, "{}", "mono", size * 0.8, color, anchor="middle")
    elif key == "flow":
        s = size
        svg.add(
            f'<g transform="translate({x:.1f} {y:.1f})" fill="none" stroke="{color}" stroke-width="1.6">'
            f'<circle cx="{s*.18}" cy="{s*.5}" r="{s*.12}"/><circle cx="{s*.82}" cy="{s*.2}" r="{s*.12}"/><circle cx="{s*.82}" cy="{s*.8}" r="{s*.12}"/>'
            f'<path d="M{s*.3} {s*.45}L{s*.7} {s*.25}M{s*.3} {s*.55}L{s*.7} {s*.75}"/></g>'
        )
    elif key == "wave":
        s = size
        svg.add(
            f'<path transform="translate({x:.1f} {y:.1f})" d="M0 {s*.5}h{s*.2}l{s*.1} -{s*.35} {s*.15} {s*.7} {s*.15} -{s*.7} {s*.1} {s*.35}h{s*.3}" '
            f'fill="none" stroke="{color}" stroke-width="1.6"/>'
        )



# Width-aware layouts. Desktop assets are 720 wide; mobile variants are 400
# wide with larger relative type, swapped in by <picture media="(max-width…)">.

def chamfer_grid(s, W, H, c):
    t = s.t
    s.add(f'<defs><pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{t["grid"]}" stroke-width="1"/></pattern></defs>')
    s.add(f'<polygon points="{c+1},2 {W-2},2 {W-2},{H-c-1} {W-c-1},{H-2} 2,{H-2} 2,{c+1}" fill="url(#g)"/>')


HERO_CSS = (
    ".rail{stroke-dasharray:800;stroke-dashoffset:800;animation:draw 1.4s cubic-bezier(.2,.7,.2,1) .15s forwards}"
    ".wire{stroke-dasharray:800;stroke-dashoffset:800;animation:draw 1.2s ease-out .9s forwards}"
    ".lamp{animation:pulse 2.6s ease-in-out infinite}"
    ".rise{opacity:0;animation:rise .7s ease-out .25s forwards}"
    "@keyframes draw{to{stroke-dashoffset:0}}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}"
    "@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
    "@media (prefers-reduced-motion:reduce){.rail,.wire{animation:none;stroke-dashoffset:0}.lamp{animation:none}.rise{animation:none;opacity:1}}"
)

HERO_COLS = [
    ("EDUCATION", ["B.Sc. Computer Science", "Holon Institute of Technology"]),
    ("CURRENT", ["Team Lead · Talent Bridge", "Hasoub AI Engineer Career Accelerator"]),
    ("DOMAINS", ["Web · Backend · APIs", "Embedded · Digital hardware"]),
]
HERO_TITLE = "Ward Keadan — Software Engineer"
HERO_DESC = ("Software Engineer. Full-stack and backend development, AI-assisted engineering. "
             "B.Sc. Computer Science, Holon Institute of Technology. Team Lead, Talent Bridge, "
             "Hasoub AI Engineer Career Accelerator. Domains: web, backend, APIs, embedded, digital hardware.")


def hero(theme, W):
    t = THEMES[theme]
    mob = W < 500
    m = 22 if mob else 36
    if mob:
        H = 470
    else:
        H = 340
    s = SVG(W, H, theme, HERO_TITLE, HERO_DESC)
    s.css.append(HERO_CSS)
    c = 18 if mob else 22
    plate(s, 1, 1, W - 2, H - 2, c=c)
    chamfer_grid(s, W, H, c)
    s.add(f'<line x1="{c}" y1="3" x2="{W-2}" y2="3" stroke="{t["rule"]}" stroke-width="4"/>')
    s.add(f'<line class="rail" x1="{c}" y1="3" x2="{W-2}" y2="3" stroke="{t["red"]}" stroke-width="4"/>')
    top = "WK-01" if mob else "ENGINEERING PROFILE · WK-01"
    s.text(m, 38, top, "mono", 12 if mob else 13, t["ink3"], track=0.12)
    lamp_txt = "OPEN TO SOFTWARE ROLES"
    lw = METRICS["mono"].width(lamp_txt, 12 if mob else 13, 0.12)
    s.add(f'<circle class="lamp" cx="{W-m-lw-12:.1f}" cy="33.5" r="5" fill="{t["cyan"]}"/>')
    s.text(W - m, 38, lamp_txt, "mono", 12 if mob else 13, t["cyan"], anchor="end", track=0.12)
    s.add(f'<line x1="{m}" y1="54" x2="{W-m}" y2="54" stroke="{t["rule"]}" stroke-width="1"/>')
    s.add('<g class="rise">')
    if mob:
        s.text(m - 2, 122, "WARD KEADAN", "display", 60, t["ink"], track=0.01)
        s.text(m, 154, "SOFTWARE ENGINEER", "mono", 15, t["redt"], track=0.14)
        for i, l in enumerate(["Full-stack & backend development", "AI-assisted engineering"]):
            s.text(m, 184 + i * 24, l, "body", 18, t["ink2"])
        wy = 226
    else:
        s.text(m - 2, 142, "WARD KEADAN", "display", 92, t["ink"], track=0.01)
        s.text(m + 1, 180, "SOFTWARE ENGINEER", "mono", 18, t["redt"], track=0.14)
        s.text(m, 212, "Full-stack & backend development · AI-assisted engineering", "body", 20, t["ink2"])
        wy = 232
    s.add("</g>")
    if mob:
        s.add(f'<path class="wire" d="M{m+3} {wy} V{H-40}" stroke="{t["cyan"]}" stroke-width="1.5" fill="none"/>')
        y = wy + 22
        for lab, lines in HERO_COLS:
            s.add(f'<rect x="{m}" y="{y-9}" width="7" height="7" fill="{t["gold"]}"/>')
            s.text(m + 18, y, lab, "mono", 12, t["ink3"], track=0.12)
            s.text(m + 18, y + 24, lines[0], "bodyb", 17, t["ink"])
            s.text(m + 18, y + 46, lines[1], "body", 15, t["ink2"])
            y += 70
    else:
        s.add(f'<path class="wire" d="M{m} {wy} H{W-m}" stroke="{t["cyan"]}" stroke-width="1.5" fill="none"/>')
        widths = [max(METRICS["bodyb"].width(l[0], 16), METRICS["body"].width(l[1], 14), METRICS["mono"].width(lab, 12, 0.12)) for lab, l in HERO_COLS]
        gap = (W - 2 * m - sum(widths)) / 2
        x = m
        for i, (lab, lines) in enumerate(HERO_COLS):
            s.add(f'<rect x="{x:.1f}" y="{wy-3}" width="7" height="7" fill="{t["gold"]}"/>')
            s.text(x, 260, lab, "mono", 12, t["ink3"], track=0.12)
            s.text(x, 284, lines[0], "bodyb", 16, t["ink"])
            s.text(x, 305, lines[1], "body", 14, t["ink2"])
            x += widths[i] + gap
    ticks(s, m, W - 110, H - 8, step=12)
    s.text(W - m, H - 12, "REV 2026", "mono", 10, t["ink3"], anchor="end", track=0.1)
    return s.render()


def divider(theme, num, label, W):
    t = THEMES[theme]
    mob = W < 500
    fs = 14 if mob else 15
    s = SVG(W, 44, theme, label.title(), "")
    s.text(2, 28, num, "mono", fs, t["goldt"], track=0.1)
    lw = s.text(34, 28, label, "mono", fs, t["ink"], track=0.16)
    x0 = 34 + lw + 16
    end = W - (40 if mob else 70)
    s.add(f'<line x1="{x0:.1f}" y1="23" x2="{end}" y2="23" stroke="{t["rule2"]}" stroke-width="1"/>')
    s.add(f'<rect x="{x0:.1f}" y="21" width="24" height="4" fill="{t["red"]}"/>')
    ticks(s, end + 8, W - 2, 28, step=6, long_every=5)
    return s.render()


STACK = [
    ("LANGUAGES", [("javascript", "JavaScript"), ("typescript", "TypeScript"), ("python", "Python"),
                   ("openjdk", "Java"), ("c", "C"), ("chip", "VHDL")]),
    ("FRONTEND", [("react", "React"), ("nextdotjs", "Next.js"), ("vite", "Vite"),
                  ("tailwindcss", "Tailwind CSS"), ("html5", "HTML"), ("css", "CSS")]),
    ("BACKEND", [("nodedotjs", "Node.js"), ("express", "Express"), ("fastapi", "FastAPI"), ("api", "REST APIs")]),
    ("DATA", [("postgresql", "PostgreSQL"), ("mongodb", "MongoDB"), ("firebase", "Firebase")]),
    ("HARDWARE", [("arduino", "Arduino · AVR"), ("wave", "ModelSim"), ("chip", "HLS → RTL flow")]),
    ("TOOLING", [("git", "Git"), ("github", "GitHub"), ("linux", "Linux"), ("docker", "Docker"), ("postman", "Postman")]),
    ("AI-ASSISTED", [("claude", "Claude Code"), ("cursor", "Cursor"), ("flow", "AI engineering workflows")]),
]


def stack(theme, W):
    t = THEMES[theme]
    mob = W < 500
    pad = 20 if mob else 28
    chip_h, isz, fs = (34, 16, 15) if mob else (38, 18, 16)
    label_w = 0 if mob else 140
    maxx = W - pad
    rows, y = [], 34
    for lab, items in STACK:
        cy0 = y + (26 if mob else 0)
        x, ry, placed = pad + label_w, cy0, []
        for key, name in items:
            cw = 12 + isz + 8 + METRICS["body"].width(name, fs) + 12
            if x + cw > maxx:
                x, ry = pad + label_w, ry + chip_h + 7
            placed.append((x, ry, cw, key, name))
            x += cw + 7
        rows.append((lab, y, placed))
        y = ry + chip_h + 26
    H = int(y)
    s = SVG(W, H, theme, "Technical stack",
            "; ".join(f"{lab.title()}: " + ", ".join(n for _, n in items) for lab, items in STACK))
    plate(s, 1, 1, W - 2, H - 2, c=18)
    clamps(s, 0, W, 1)
    for i, (lab, ry, placed) in enumerate(rows):
        if i:
            s.add(f'<line x1="{pad}" y1="{ry-13}" x2="{W-pad}" y2="{ry-13}" stroke="{t["rule"]}" stroke-width="1" stroke-dasharray="2 4"/>')
        color = t["goldt"] if lab == "HARDWARE" else (t["redt"] if lab == "AI-ASSISTED" else t["cyan"])
        s.add(f'<rect x="{pad}" y="{ry+(6 if mob else 15)}" width="6" height="6" fill="{color}"/>')
        s.text(pad + 14, ry + (15 if mob else 24), lab, "mono", 12, t["ink3"], track=0.12)
        for (x, cy, cw, key, name) in placed:
            s.add(f'<rect x="{x:.1f}" y="{cy}" width="{cw:.1f}" height="{chip_h}" fill="{t["raised"]}" stroke="{t["rule2"]}" stroke-width="1"/>')
            icon(s, key, x + 12, cy + (chip_h - isz) / 2, isz, t["icon"])
            s.text(x + 12 + isz + 8, cy + chip_h / 2 + fs * 0.36, name, "body", fs, t["ink"])
    return s.render()


PROJECTS = [
    dict(slug="code-review-roulette", n="01", domain="WEB · FULL-STACK", dkey="cyan",
         title="Code Review Roulette", stamp="LIVE · 10,000-ROUND TESTS",
         problem="Choosing reviewers by hand is slow and uneven. Two wheels pair the whole team so everyone reviews exactly one teammate, and nobody reviews their own code.",
         built=[("ROLE", "Solo project, built with an AI-assisted workflow (Claude Code)"),
                ("PROOF", "Pairing planned before the first spin · saved rounds validated · 8 tests incl. 10,000 randomized rounds")],
         chips=["Next.js 16", "React 19", "TypeScript", "Tailwind", "node:test", "Vercel"]),
    dict(slug="harmony-headlines", n="02", domain="WEB · FULL-STACK · AI API", dkey="cyan",
         title="Harmony Headlines", stamp="REACT + EXPRESS",
         problem="Regional news headlines can be emotionally charged. Every headline gets a 0–10 tone score from Gemini, and admins can rewrite a story calmer or sharper.",
         built=[("SYSTEM", "React client and a separate Express API, in two repositories"),
                ("PROOF", "MediaStack + Gemini integration · Clerk auth with an admin role · per-article tone rewrite")],
         chips=["React", "Vite", "Express", "Gemini API", "Clerk", "REST"]),
    dict(slug="cost-manager", n="03", domain="BACKEND · REST API", dkey="cyan",
         title="Cost Manager API", stamp="EXPRESS 5 · MONGODB",
         problem="Users log costs by category and need monthly summaries. A RESTful service handles users, costs, monthly reports and per-request audit logging.",
         built=[("ROLE", "Team of 2 — co-developed with Shafir Hafif"),
                ("PROOF", "MVC layout · Mongoose models · past-month reports cached once computed · pino request logging")],
         chips=["Node.js", "Express 5", "MongoDB", "Mongoose", "pino", "MVC"]),
    dict(slug="cpu-16-8-16", n="04", domain="DIGITAL HARDWARE · VHDL", dkey="gold",
         title="CPU 16-8-16", stamp="GRADE 100",
         problem="A microcoded 16-bit CPU reworked for an 8-bit program memory, so every 16-bit word moves as a low byte and then a high byte.",
         built=[("DESIGN", "30-state FSM control unit generated from algorithmic state machines; PC, MAC, IR, BR and ALU datapath"),
                ("PROOF", "Same test program gives matching output in HLS and RTL simulation (ModelSim)")],
         chips=["VHDL", "ModelSim", "Synthagate", "ASMCreator", "FSM", "RTL"]),
    dict(slug="parking-gate", n="05", domain="EMBEDDED · REAL-TIME", dkey="gold",
         title="Parking Gate System", stamp="GRADE 95",
         problem="An automatic parking gate on an Arduino UNO: two ultrasonic sensors, a servo gate, a status LCD and an interrupt-driven emergency mode.",
         built=[("ROLE", "Solo · register-level AVR firmware (DDRx / PORTx)"),
                ("PROOF", "INT0 ISR only sets a flag, debounced in the main loop · Timer1 servo · LCD over I2C")],
         chips=["C", "AVR", "Interrupts", "Timer1", "I2C", "Arduino UNO"]),
]


def card(theme, p, W):
    t = THEMES[theme]
    mob = W < 500
    pad = 22 if mob else 30
    inner = W - 2 * pad
    accent = t["cyan"] if p["dkey"] == "cyan" else t["goldt"]
    tfs, pfs, bfs = (34, 16, 15) if mob else (46, 17, 15)
    lab_w = 0 if mob else 92
    prob = wrap(p["problem"], "body", pfs, inner)
    built = [(lab, wrap(txt, "body", bfs, inner - lab_w)) for lab, txt in p["built"]]
    title_lines = wrap(p["title"].upper(), "display", tfs, inner, 0.01)
    # vertical layout
    y_dom = 44
    y_stamp = y_dom + 30 if mob else y_dom
    y_title = (y_stamp + 52) if mob else (y_dom + 50)
    y_prob = y_title + (len(title_lines) - 1) * (tfs + 2) + (30 if mob else 34)
    y_rule = y_prob + (len(prob) - 1) * (pfs + 8) + 22
    yy = y_rule + 26
    blocks = []
    for lab, ls in built:
        if mob:
            blocks.append((lab, yy, yy + 22, ls))
            yy += 22 + len(ls) * (bfs + 6) + 10
        else:
            blocks.append((lab, yy, yy, ls))
            yy += len(ls) * (bfs + 6) + 8
    chip_fs = 12
    chip_rows, x, cy = [], pad, yy + 6
    for c in p["chips"]:
        cw = METRICS["monom"].width(c, chip_fs, 0.06) + 20
        if x + cw > W - pad:
            x, cy = pad, cy + 33
        chip_rows.append((x, cy, cw, c))
        x += cw + 7
    H = int(cy + 26 + 38)
    s = SVG(W, H, theme, f'{p["title"]} — {p["domain"].title()}',
            f'{p["problem"]} ' + " ".join(f"{lab.title()}: {txt}." for lab, txt in p["built"]) + " Stack: " + ", ".join(p["chips"]) + ".")
    plate(s, 1, 1, W - 2, H - 2, c=18)
    clamps(s, 0, W, 1)
    s.add(f'<rect x="{pad}" y="{y_dom-11}" width="6" height="6" fill="{accent}"/>')
    s.text(pad + 14, y_dom - 4, f'{p["n"]} · {p["domain"]}', "mono", 12, accent, track=0.12)
    sw = METRICS["mono"].width(p["stamp"], 12, 0.12) + 24
    sx = pad if mob else W - pad - sw
    s.add(f'<rect x="{sx:.1f}" y="{y_stamp-21}" width="{sw:.1f}" height="26" fill="none" stroke="{t["gold"]}" stroke-width="1.5"/>')
    s.text(sx + sw / 2, y_stamp - 3.5, p["stamp"], "mono", 12, t["goldt"], anchor="middle", track=0.12)
    for i, l in enumerate(title_lines):
        s.text(pad - 2, y_title + i * (tfs + 2), l, "display", tfs, t["ink"], track=0.01)
    for i, line in enumerate(prob):
        s.text(pad, y_prob + i * (pfs + 8), line, "body", pfs, t["ink2"])
    s.add(f'<line x1="{pad}" y1="{y_rule}" x2="{W-pad}" y2="{y_rule}" stroke="{t["rule"]}" stroke-width="1"/>')
    for lab, ly, ty, ls in blocks:
        s.text(pad, ly, lab, "mono", 11, t["ink3"], track=0.12)
        for j, l in enumerate(ls):
            s.text(pad + lab_w, ty + j * (bfs + 6), l, "body", bfs, t["ink"])
    for (x, cy, cw, c) in chip_rows:
        s.add(f'<rect x="{x:.1f}" y="{cy}" width="{cw:.1f}" height="26" fill="{t["raised"]}" stroke="{t["rule2"]}" stroke-width="1"/>')
        s.text(x + 10, cy + 17.5, c, "monom", chip_fs, t["ink"], track=0.06)
    ticks(s, pad, W - pad - 52, H - 8, step=12)
    s.text(W - pad, H - 11, "VIEW ↗", "mono", 11, t["redt"], anchor="end", track=0.12)
    return s.render()


def button(theme, label, primary=False, w=180):
    t = THEMES[theme]
    h = 44
    s = SVG(w, h, theme, label.replace("↗", "").strip().title(), "")
    c = 10
    pts = f"{c},0 {w},0 {w},{h-c} {w-c},{h} 0,{h} 0,{c}"
    if primary:
        s.add(f'<polygon points="{pts}" fill="{t["red"]}"/>')
        s.text(w / 2, 27.5, label, "mono", 13, t["onred"], anchor="middle", track=0.14)
    else:
        s.add(f'<polygon points="{pts}" fill="{t["raised"]}" stroke="{t["rule2"]}" stroke-width="1.5"/>')
        s.text(w / 2, 27.5, label, "mono", 13, t["ink"], anchor="middle", track=0.14)
    return s.render()


def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)


for f in os.listdir(OUT):
    if f.endswith(".svg"):
        os.remove(os.path.join(OUT, f))
for th in ("dark", "light"):
    for W, suf in ((720, ""), (400, "-mobile")):
        write(f"hero{suf}-{th}.svg", hero(th, W))
        write(f"stack{suf}-{th}.svg", stack(th, W))
        for p in PROJECTS:
            write(f"card-{p['slug']}{suf}-{th}.svg", card(th, p, W))
    for num, slug, label in [("01", "experience", "LEADERSHIP & EXPERIENCE"), ("02", "stack", "TECHNICAL STACK"),
                             ("03", "projects", "SELECTED PROJECTS"), ("04", "contact", "GET IN TOUCH")]:
        write(f"divider-{slug}-{th}.svg", divider(th, num, label, 720))
        write(f"divider-{slug}-mobile-{th}.svg", divider(th, num, label, 400))
    write(f"btn-portfolio-{th}.svg", button(th, "PORTFOLIO ↗", primary=True))
    write(f"btn-linkedin-{th}.svg", button(th, "LINKEDIN ↗"))
    write(f"btn-email-{th}.svg", button(th, "EMAIL"))

total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print(len(os.listdir(OUT)), "files", round(total / 1024), "KB")
