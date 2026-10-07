---
name: project-visualizer
description: Studies a coding project and builds one interactive, animated HTML page that explains the WHOLE project visually in the easiest way (what it is, the big picture, how a request flows, what each part does, how to run it). Use when the user wants to understand, explain, map, or visualize a codebase, or asks "what did the coding agent build?", "how does this project work?", "explain this project", "draw the architecture", "show me how the files connect".
---

# Project Visualizer

Goal: the user opens ONE page and understands the whole project, even if a coding agent wrote it
and they never read the code. Think of a patient teacher with a whiteboard: simple words,
pictures first, one idea at a time, things that move to show what happens in order.

You are the designer and the writer. There is no template. Each project gets its own page,
built from what you learned in the code. Works the same in Claude Code, Antigravity CLI, Codex.

`<skill_dir>` means the folder that contains this SKILL.md.

## Where to save (very important)

1. Run `pwd`. That folder is WORKDIR: the exact folder the agent was started in.
   Example: if Claude Code runs in `/Users/me/Claude_tracker`, WORKDIR is that folder.
2. Save the page as `WORKDIR/project-map.html`, directly inside WORKDIR.
   - No subfolder. No hidden folder. Not in `<skill_dir>`. Not in the project path you studied,
     if that is a different folder. Always WORKDIR.
   - If `project-map.html` already exists there, overwrite it.
3. Temporary files (`project.json`, screenshots) go in `/tmp/project-visualizer/`, never in WORKDIR.
4. After saving, OPEN the page for the user and print its full path:
   macOS `open "WORKDIR/project-map.html"`, Linux `xdg-open "WORKDIR/project-map.html"`,
   Windows `start "" "WORKDIR\project-map.html"`.

## What 10/10 looks like

- A beginner understands the project in 30 seconds from the first screen.
- It explains the WHOLE project: purpose, big picture, one real request step by step, every
  important part, how to run it, and the words they need to know.
- Pictures lead, text supports. No walls of text. One idea per section.
- Things move to show order and direction. Hover highlights. Click opens plain-language details.
- Looks polished and modern (dark theme, color per part, good spacing), never a plain white page.
- Everything is true: each box, arrow and claim comes from code you read, and the page shows the
  file that proves it.

## Steps

1. STUDY the project first (do not write HTML yet).
   Read the README, package/config files, entry points, routes, API clients, main logic, models,
   prompts, and scripts. Optional helper (always pass `-o`):
   `python3 <skill_dir>/scripts/scan_project.py <project> -o /tmp/project-visualizer`
   writes `project.json` (files, imports, routes, HTTP calls, packages) for Python/JS/TS. It is a
   plain static scan: use it to find your way, then confirm by reading the code.
   Trace 1-3 real actions from start to finish (user clicks -> which file -> which file -> result).
   Write down your facts with the file that proves each one: purpose, who uses it, tech stack,
   the parts, how they talk, where data is stored, where AI/LLMs are used, how to run it, env
   variable NAMES, and honest weak spots (TODOs, hard-coded values, missing tests).

2. PLAN the page with `references/page-blueprint.md`. Keep the sections that fit this project,
   skip the rest. Choose a simple everyday analogy for the big picture.

3. WRITE the page with `references/explain-style.md` (how to word things) and
   `references/snippets.md` (working code patterns for animated arrows, guided step player,
   side panel, scroll navigation; adapt them, do not copy a fixed layout). One self-contained
   `.html` file: plain HTML, CSS, JavaScript, SVG. No internet, no CDN, no build step.
   Write it straight to `WORKDIR/project-map.html`. For a long page, create the file first and
   add it in parts.

4. CHECK and IMPROVE (never skip):
   - `python3 <skill_dir>/scripts/check_page.py WORKDIR/project-map.html` and fix every PROBLEM.
   - If a headless browser works, take a screenshot into /tmp and look at it
     (for example `npx playwright screenshot --viewport-size "1440,900" --wait-for-timeout 1500 file://WORKDIR/project-map.html /tmp/project-visualizer/preview.png`).
     If it fails, skip this part.
   - Go through `references/qa-checklist.md`. Read each section as if you were a beginner.
     Fix anything confusing, empty, cramped, or untrue. Then check once more.

5. DELIVER: open the page (see "Where to save"), give the full path, and tell the user in 2-3
   lines what the page shows and which parts are guesses ("inferred").

## Rules

- The only file you add to the user's folder is `project-map.html`.
- Only draw and say what the code supports. Label guesses "inferred" on the page.
- Simple language. Define every technical word the first time (or put it in the glossary).
- Never edit the user's project code.
- Never open or print `.env` files, keys, or tokens. Env variable names are fine, values are not.
- Do not reuse an old page. Each project gets its own layout and its own analogy.
- Big project? Show the big picture first and let the user click into details.
