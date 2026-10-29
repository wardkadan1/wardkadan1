import sys
OUT = sys.argv[1] if len(sys.argv) > 1 else __import__("os").path.join(__import__("os").path.dirname(__file__), "..", "README.md")
LINKEDIN = "https://www.linkedin.com/in/ward-keadan"
PORTFOLIO = "https://wardkeadan.vercel.app"
EMAIL = "mailto:wardkadan1@gmail.com"
GH = "https://github.com/wardkadan1"

def pic(name, alt, width=720, mobile=True):
    a = "assets/"
    src = []
    if mobile:
        src.append(f'<source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="{a}{name}-mobile-dark.svg">')
        src.append(f'<source media="(max-width: 600px)" srcset="{a}{name}-mobile-light.svg">')
    src.append(f'<source media="(prefers-color-scheme: dark)" srcset="{a}{name}-dark.svg">')
    return ("<picture>" + "".join(src) +
            f'<img alt="{alt}" src="{a}{name}-light.svg" width="{width}"></picture>')

def btn(name, alt, href):
    return (f'<a href="{href}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/btn-{name}-dark.svg">'
            f'<img alt="{alt}" src="assets/btn-{name}-light.svg" width="180" height="44"></picture></a>')

def divider(slug, alt):
    return f'<p>{pic("divider-" + slug, alt, 720)}</p>'

cards = [
    ("code-review-roulette", "Code Review Roulette — fair, random code-review pairing. Next.js, TypeScript, 8 tests including 10,000 randomized rounds. Live.",
     f"{GH}/Code-Review-Roulette",
     [("Repository", f"{GH}/Code-Review-Roulette"), ("Live demo", "https://code-review-roulette-five.vercel.app")]),
    ("harmony-headlines", "Harmony Headlines — React news reader that scores headline tone with Gemini; Express API, Clerk auth.",
     f"{GH}/Harmony-Headlines",
     [("Frontend", f"{GH}/Harmony-Headlines"), ("Backend API", f"{GH}/Harmony-Headlines-Backend")]),
    ("cost-manager", "Cost Manager API — Express 5 and MongoDB REST API with monthly reports and request logging. Team of 2.",
     f"{GH}/Cost-Manager-RESTful-Web",
     [("Repository", f"{GH}/Cost-Manager-RESTful-Web")]),
    ("cpu-16-8-16", "CPU 16-8-16 — microcoded 16-bit CPU in VHDL with an 8-bit program memory; HLS and RTL outputs match. Grade 100.",
     f"{GH}/CPU-16-8-16",
     [("Repository", f"{GH}/CPU-16-8-16")]),
    ("parking-gate", "Parking Gate System — Arduino UNO, register-level AVR C, INT0 emergency interrupt, Timer1 servo, I2C LCD. Grade 95.",
     f"{GH}/iot-project",
     [("Repository", f"{GH}/iot-project")]),
]

L = []
L.append(f'<a href="{PORTFOLIO}">{pic("hero", "Ward Keadan — Software Engineer. Full-stack and backend development, AI-assisted engineering. B.Sc. Computer Science (HIT). Team Lead, Hasoub AI Engineer Career Accelerator.")}</a>')
L.append("")
L.append(f'<p>{btn("portfolio", "Portfolio", PORTFOLIO)}&nbsp;{btn("linkedin", "LinkedIn", LINKEDIN)}&nbsp;{btn("email", "Email", EMAIL)}</p>')
L.append("")
L.append("I build web applications end to end — REST APIs, data models and React / Next.js interfaces — and I'm just as comfortable below the software stack: I've designed a microcoded CPU in VHDL and written register-level firmware for AVR. I hold a B.Sc. in Computer Science from the Holon Institute of Technology (2025).")
L.append("")
L.append("I use AI-assisted workflows (Claude Code, Cursor) for implementation, code review and debugging, and I treat their output the way I treat a teammate's pull request: read it, test it, question it.")
L.append("")
L.append(divider("experience", "01 — Leadership and experience"))
L.append("")
L.append("### Team Lead · Talent Bridge")
L.append("**Hasoub AI Engineer Career Accelerator** · 2026 – present · team of five")
L.append("")
L.append("A recruitment and career-support platform for Hasoub, with separate portals for candidates, recruiters and senior engineers. React + TypeScript frontend, FastAPI backend, PostgreSQL, Docker. I joined as the team's Scrum Master and now lead it as Team Lead.")
L.append("")
L.append("- **Technical coordination** — breaking work down, aligning frontend and backend, keeping the team unblocked")
L.append("- **Pull request reviews** — reviewing changes for correctness, consistency and maintainability")
L.append("- **Workflow** — improving how the team uses GitHub and Jira, from issues to merged PRs")
L.append("- **Quality** — pushing automated testing and code quality (pytest, Vitest, GitHub Actions)")
L.append("- **AI-assisted collaboration** — bringing Claude Code into day-to-day engineering, with review on every change")
L.append("")
L.append("**Also** — building the *Elafandy B2B Platform* solo for a real wholesale business (Next.js, PostgreSQL, Prisma; in progress), and earlier co-founded *BuilderBond*, a construction-labor marketplace, as co-founder and frontend developer — presented at HIT FUTURE Demo Day.")
L.append("")
L.append(divider("stack", "02 — Technical stack"))
L.append("")
L.append(pic("stack", "Technical stack. Languages: JavaScript, TypeScript, Python, Java, C, VHDL. Frontend: React, Next.js, Vite, Tailwind CSS, HTML, CSS. Backend: Node.js, Express, FastAPI, REST APIs. Data: PostgreSQL, MongoDB, Firebase. Hardware: Arduino and AVR, ModelSim, HLS-to-RTL flow. Tooling: Git, GitHub, Linux, Docker, Postman. AI-assisted: Claude Code, Cursor, AI engineering workflows."))
L.append("")
L.append(divider("projects", "03 — Selected projects"))
L.append("")
for slug, alt, href, links in cards:
    L.append(f'<a href="{href}">{pic("card-" + slug, alt)}</a>')
    L.append("")
    L.append("<sub>" + " &nbsp;·&nbsp; ".join(f'<a href="{u}">{t} ↗</a>' for t, u in links) + "</sub>")
    L.append("")
    L.append("<br>")
    L.append("")
L.append(f'More: [SmartInventory]({GH}/SmartInventory) — Android (Java) with Firebase Auth and Firestore · [Who Is The Smartest?]({GH}/Who-Is-The-Smartest) — trivia game built by a team of four')
L.append("")
L.append(divider("contact", "04 — Get in touch"))
L.append("")
L.append("Open to **software engineering roles** — full-stack and backend first, and also AI-related software engineering, embedded systems and verification.")
L.append("")
L.append(f'<p>{btn("portfolio", "Portfolio", PORTFOLIO)}&nbsp;{btn("linkedin", "LinkedIn", LINKEDIN)}&nbsp;{btn("email", "Email", EMAIL)}</p>')
L.append("")
open(OUT, "w").write("\n".join(L) + "\n")
print("README written", len("\n".join(L)))
