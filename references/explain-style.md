# How to explain (writing style)

The reader is smart but new to this code. Write like a friendly teacher.

## For every part (box, file, step) answer three things
1. What it is, in 5-10 words. ("The screen where the user types questions.")
2. Why it exists. ("Without it the user has no way to talk to the app.")
3. What it talks to. ("Sends the question to the backend.")

## Rules
- Short sentences. One idea each. Max about 20 words.
- Everyday words first, technical word second: "The backend (the server code) ..."
- Use "it sends", "it asks", "it stores". Avoid "leverages", "orchestrates", "facilitates",
  "robust", "seamless".
- Start with an analogy, then give the real names. Keep the analogy consistent on the page.
- Use real examples from the code: real route names, real field names, real sample values from
  tests or seed data. Never invent numbers, file names, or behavior.
- Name files with the short name and show the full path on hover or in the details panel.
- Arrow labels are verbs or calls, not "uses": `POST /api/chat`, `reads PDF`, `embeds text`.
- If unsure what something does, read it. If still unsure, say "inferred" or leave it out.

## Good vs weak
- Weak: "api.js handles API communication."
- Good: "api.js packs the user's question into JSON and sends it to the backend with fetch()."
- Weak: "Vector database for retrieval."
- Good: "A shelf where every document chunk is stored as numbers, so the app can find the chunks
  closest in meaning to the question."

## Length
- Hero sentence: 1. Section intro: 1-2 sentences. Card text: 2-3 sentences. Step caption: 1 sentence.
- If a paragraph is longer than 4 lines, turn it into a picture or a short list.
