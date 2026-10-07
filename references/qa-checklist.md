# QA checklist (the 10/10 bar)

Go through this after `check_page.py` passes and after you have looked at a screenshot or the
opened page. Fix what fails, then check again.

## Is it true?
- [ ] Every box, arrow, step, and claim comes from code you actually read.
- [ ] The details panel shows the file (and function or line) that proves each connection.
      Guesses are labeled "inferred".
- [ ] Examples (routes, field names, sample values) are real, not invented.
- [ ] No secrets, keys, tokens, or `.env` values anywhere. Env variable names only.

## Does it explain the WHOLE project?
- [ ] Hero: what it does, who it is for, "in 30 seconds" in 3 points.
- [ ] Big picture with an analogy and labeled, animated arrows.
- [ ] One real request followed step by step with a player.
- [ ] Every important part has a card: what, why, talks to, key files.
- [ ] How to run it (real commands, ports, env variable names).
- [ ] Glossary for the technical words used.
- [ ] Honest notes: weak spots and "read these 3 files first".
- [ ] Sections that do not apply (no database, no AI) are left out, not faked.

## Is it easy?
- [ ] A beginner gets the first screen in 10 seconds.
- [ ] No paragraph is longer than 4 lines. Pictures carry the story.
- [ ] Only important files are shown. Tests, styles, configs, and boilerplate are hidden.
- [ ] Arrow labels say HOW (`POST /api/chat`), not "uses".
- [ ] Every technical word is explained the first time.

## Is it beautiful and alive?
- [ ] Not a plain white page: dark theme, color per part, consistent spacing, clear hierarchy.
- [ ] Something moves to show order or direction. Hover highlights. Click opens details.
- [ ] Sticky menu, search, and light/dark toggle work.
- [ ] Fits a laptop screen and a phone. Text is at least 14px. Nothing overlaps or is cut off.
- [ ] Respects reduced motion (`prefers-reduced-motion`).

## Does it work?
- [ ] `check_page.py` says OK. No JavaScript errors.
- [ ] One self-contained file. Opens by double-click, works offline.
- [ ] Every button, tab, and link on the page does something.

## Finish
- [ ] Opened the page and gave the user the full path.
- [ ] Told the user in 2-3 lines what it shows and which parts are guesses.
- [ ] Did not change any of the user's project code.
