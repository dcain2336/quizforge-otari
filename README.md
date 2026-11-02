# QuizForge — Otari Edition

**Mozilla Otari "Devs Wilding" Hackathon entry** (Oct 28 – Nov 11, 2026) by David Scott Cain.
A port of QuizForge Live (GenAI Works Open Agent entry): the same study-companion core —
generate a quiz from pasted notes, explain answers, adapt difficulty — with the model layer
moved to Mozilla's Otari open-weight gateway, plus the Otari-native wedge: **multi-model
comparison**. One question goes to two open-weight models through the gateway, and the app
shows where they agree, differ, and why. Model choice becomes a visible decision, not magic.

## The loop (unchanged from Live)

1. **PLAN** — the planner reads topic + graded history and picks focus areas and difficulty.
2. **GENERATE** — the QuizForge engine builds the round's quiz (LLM chain, then an offline
   engine that always works).
3. **GRADE** — answers graded on the spot; score + per-question results.
4. **ADAPT** — every miss gets an evidence-backed explanation; weak topics drive the next round.

## The Otari wedge (new in this edition)

- **Compare tab** — ask one question, optionally ground it with study material. The same
  prompt goes to both configured models. The view renders both answers side by side, an
  agreement badge (✅ AGREE / ⚠️ PARTLY AGREE / ❌ DIFFER), a plain-language verdict, and
  the overlap evidence behind it. The verdict always points back to the study material:
  agreement is not correctness, and disagreement means neither model settles it.
- **Agreement measure** — Jaccard overlap over content words (stopwords removed):
  ≥ 0.6 agree, 0.3–0.6 partial, below 0.3 differ. Pure function, unit-tested.

## Quick start

```bash
cp .env.example .env   # fill in Otari values to go live; all optional — the demo runs keyless
python3 app.py         # serve at http://localhost:8765
```

## API

- `GET /` — single-page UI, three tabs: one-shot quiz (v1), Live study loop, Compare models
- `GET /sample` — demo study text · `GET /health` — liveness
- `GET /api/otari-status` — gateway mode (live/stub) + model names (never the key)
- `POST /api/compare` — `{question, context}` → both model answers + agreement + verdict
- `POST /api/generate`, `POST /api/round`, `POST /api/grade` — the Live core, unchanged
- `GET /api/usage`, `GET /api/status` — metered evidence + integration health panel

## Stub vs live — read this before demoing

- **Stub mode (default):** with no `OTARI_API_KEY` + `OTARI_BASE_URL` set, `/api/compare`
  returns clearly labeled demonstration answers that deliberately disagree, so the comparison
  view can be verified end to end. The UI banners stub mode on every run. Stub answers are
  NOT model output and must never be presented as such.
- **Live mode:** set `OTARI_API_KEY`, `OTARI_BASE_URL`, `OTARI_MODEL_A`, `OTARI_MODEL_B`.
  **Unverified (2026-11-02):** the gateway's exact base URL and model slugs were not
  confirmed live — the onboarding doc at https://www.otari.ai/devs-wilding could not be
  fetched from the build environment. Confirm the endpoint shape against that doc before
  relying on live mode. The client assumes OpenAI-compatible `POST {base}/chat/completions`
  with a Bearer key; set `OTARI_CHAT_PATH` if the doc shows a different path.
- **Security:** the Otari key lives in the environment (or a local `.env` file), never in
  code or this package.

## Architecture

- `otari.py` — the Otari gateway client: env-configured live chat, stub fallback, agreement
  measure, comparison entry point. Standard library only.
- `app.py` — the web server; Otari routes are `/api/otari-status` and `/api/compare`.
- `static/index.html` — the UI; the Compare tab is the third tab.
- Everything else (`agent.py`, `generator.py`, `explain.py`, `markovian.py`, `meterless.py`,
  `nemotron.py`, `zetaris.py`) is the QuizForge Live core, unchanged.
- `tests/test_otari.py` — deterministic offline tests for the gateway module.
  Run the full suite: `python3 -m unittest discover -s tests -v`

## Demo

- `demo/demo-script.md` — narrated ~2-minute walkthrough script.
- `demo/shots/` — genuine screenshots of the running app (stub mode, labeled).
- `demo/quizforge-otari-demo.mp4` — screen recording of the real app running the
  comparison flow (Playwright browser recording, stub mode, labeled on screen).

## License

MIT.
