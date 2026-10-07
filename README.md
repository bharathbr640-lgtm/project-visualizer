# project-visualizer

An agent skill that studies a coding project and builds **one interactive, animated HTML page** that
explains the whole project visually, in simple words.

If a coding agent built your project and you are not sure what it actually made, run this skill.
You get a single `project-map.html` that shows what the project is, how its parts connect, how one
real request travels through the code, and how to run it.

Works with **Claude Code**, **Codex**, and **Antigravity CLI** (all read the same `SKILL.md` format).

## What the page contains

The agent decides what fits your project, but the page usually has:

1. **What is this?** One plain sentence, who it is for, and "in 30 seconds" in 3 points.
2. **The big picture:** boxes for the main parts with animated, labeled arrows that say how they talk
   (for example `POST /api/chat`). Only the important files are shown.
3. **Follow one request:** a Play / Pause / Next step player that lights up each part, with the real
   file and a tiny example of the data at each step.
4. **Inside each part:** what it is, why it exists, and what it talks to.
5. **How the files connect:** a simple dependency view (only when it helps).
6. **Data and AI:** where data is stored and where models are used.
7. **Run it:** real commands, ports, and environment variable names (never values).
8. **Words to know:** a short glossary.
9. **Honest notes:** weak spots, and which 3 files to read first.

The page is a single self-contained file: dark theme, light/dark toggle, search, hover highlights,
click-for-details panel, no internet needed.

There is no fixed template. The agent reads your code and designs the page for that project.
Every box and arrow must come from code it read, and guesses are labeled "inferred".

## Install

Copy the folder into the skills folder of your agent.

Claude Code (all projects):

```bash
mkdir -p ~/.claude/skills
cp -R project-visualizer ~/.claude/skills/
```

Claude Code (one project only): copy it to `<your-project>/.claude/skills/project-visualizer`.

Codex:

```bash
mkdir -p ~/.codex/skills
cp -R project-visualizer ~/.codex/skills/
```

Antigravity CLI: copy the folder into the skills folder that Antigravity reads (check its docs for
the exact path).

The folder must be named `project-visualizer` and `SKILL.md` must sit directly inside it:
`~/.claude/skills/project-visualizer/SKILL.md`. Restart the agent after copying.

## Use

Open your agent in the project you want explained, then run:

```bash
cd /path/to/your/project
claude
```

and type `/project-visualizer`, or just ask:

- "Explain how this project works"
- "Show me how the files connect"
- "Visualize what the coding agent built"

The page is saved as **`project-map.html` directly in the folder the agent is running in**
(no subfolder), and the agent opens it for you. Temporary files go to `/tmp/project-visualizer/`.

## What is inside

```
project-visualizer/
├── SKILL.md                      # the instructions the agent follows
├── scripts/
│   ├── scan_project.py           # optional helper: lists files, imports, routes, HTTP calls
│   └── check_page.py             # checks the generated page (JS errors, offline, interactive)
└── references/
    ├── page-blueprint.md         # the story the page tells, section by section
    ├── explain-style.md          # how to word explanations simply
    ├── snippets.md               # working code patterns (animated arrows, step player, panel)
    └── qa-checklist.md           # the quality bar the agent checks before finishing
```

### Helper scripts

Both use only the Python standard library.

```bash
# Optional: static scan of a Python / JavaScript / TypeScript project
python3 scripts/scan_project.py /path/to/project -o /tmp/project-visualizer

# Check a generated page (needs Node.js for the JavaScript syntax check; works without it too)
python3 scripts/check_page.py project-map.html
```

`scan_project.py` is a plain static scan. It resolves imports and finds routes and HTTP calls, but
the agent still confirms important facts by reading the code.

## Requirements

- An agent that supports `SKILL.md` skills (Claude Code, Codex, Antigravity CLI)
- Python 3.8+ for the optional helper scripts
- Node.js (optional) so `check_page.py` can check JavaScript syntax
- A browser to open the page

## Limitations

- The quality of the page depends on how well the agent reads your project, so results can vary
  between runs. Ask it to improve a section if one is weak.
- `scan_project.py` only understands Python, JavaScript, and TypeScript. Other languages still
  work, because the agent reads the files itself, but without the helper's file and import list.
- Very large projects are shown as a big picture first, with details on click.

## Safety

- The skill never edits your project code. The only file it adds to your folder is `project-map.html`.
- It does not read or print `.env` files, keys, or tokens. Environment variable names may appear,
  values never do.

## Credits

The folder layout (one `SKILL.md` plus a `references/` folder) follows the structure of
[helloianneo/ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations).
