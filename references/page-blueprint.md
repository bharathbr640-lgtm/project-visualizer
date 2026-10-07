# Page blueprint: the story the page tells

The page is a guided story, top to bottom, with a sticky menu to jump between sections.
Keep the sections that fit this project and skip the rest. Order matters: from "what is this?"
to "how do I use it?".

## 1. Hero: "What is this?"
- Project name, one plain sentence of what it does, and who it is for.
- "In 30 seconds": exactly 3 short points (what goes in, what happens, what comes out).
- Tech chips (React, FastAPI, SQLite, Ollama...) with a tiny hint of what each one does.

## 2. The big picture
- One diagram: the main parts as boxes, arrows with labels that say HOW they talk
  (`POST /api/chat`, `SQL query`, `calls Ollama`). 2-7 boxes. Each box shows only its 2-5 key files.
  Everything else hidden behind "+N other files".
- One everyday analogy line above it (a restaurant, a post office, a factory line). Map each
  box to the analogy in one short phrase.
- Dots move along the arrows. Hover a box to light up its connections. Click for details.

## 3. Follow one request (the most important section)
- Pick the main thing a user does. Show it as a step player: Play, Pause, Previous, Next.
- Each step: the part that lights up, a one-line plain caption ("The frontend sends the question"),
  the real file and function name, and a tiny example of the data at that moment
  (`{ "question": "Will it rain in Hassan?" }`), taken from the code or a test, not invented.
- If the project has a second important flow (upload, training, scheduled job), add it as a tab.

## 4. Inside each part
- One card per box from section 2: what it does, why it exists, what it talks to, key files with
  one line each, and the 1-2 functions that matter most. Click a file to open details.

## 5. How the files connect (only if it helps)
- Simplified dependency view: clusters by folder, not hundreds of dots. Hover a file to see what
  it uses and what uses it. Skip for tiny projects.

## 6. Data and AI (only if present)
- Where data lives (files, database tables, vector store) and its shape in one small example.
- Where AI is used: which model, what prompt goes in, what comes out, who calls it.

## 7. Run it
- The real commands from README/package files/scripts, the ports it uses, and the env variable
  NAMES it needs (never values). A copy button on each command.

## 8. Words to know
- Glossary of 5-12 terms that appear on the page (API, endpoint, embedding, route...), one
  simple sentence each, with an example from this project when possible.

## 9. Honest notes
- 3-6 short points: what looks solid, what looks weak or unfinished (TODOs, hard-coded values,
  no tests, missing error handling), and what to read first: "If you read only 3 files, read
  these". Label guesses "inferred".

## Always
- Sticky top menu with the section names, highlighting the current one.
- Search box and light/dark toggle.
- A small footer line: "Built from the code in <folder> on <date>".
