# SUBMIT — Mozilla Otari "Devs Wilding" Hackathon

**Deadline: Nov 11, 2026** (Eventbrite lists the window through Nov 12, 07:00 ET;
treat Nov 11 as the build deadline). **Status: LIVE-VERIFIED + REPO PUBLIC 2026-11-02, not submitted — DoraHacks submission is the only remaining step.**

## Build state (2026-11-02)

- Port complete in `quizforge-otari/`: QuizForge Live core unchanged + new `otari.py`
  gateway client + `POST /api/compare` + `GET /api/otari-status` + Compare tab in the UI.
- Verified: 38/38 unit tests pass (re-run in the live push pass); live server compare
  returns mode live with real answers from both models (agree verdict on supplied
  material); demo video + screenshots captured from the real running app in both
  stub mode (labeled) and live mode.
- Public repo: https://github.com/dcain2336/quizforge-otari — commit 069d829 (full app +
  stub demo, 30 tree paths). Pushed tree verified: NO `.env` anywhere in it. The `.env`
  file does not exist locally either, so no key material could have been pushed.
- Gateway mode: LIVE VERIFIED 2026-11-02. The live key sits only in local
  `quizforge-otari/.env` (mode 600, never pushed, never in chat/memory). Verified
  endpoint: https://otari.ai/api/v1 + POST /chat/completions with an `Otari-Key:`
  header (OTARI_AUTH=otari-key); the docs form (api.otari.ai/v1 + Bearer) 404s with
  "serves its API under /api/v1". Models: deepseek/deepseek-v4.1-flash-1017 +
  meta/llama-3.1-8b-instruct. muse-spark-open was DROPPED: as a reasoning model it
  burns its token budget on reasoning and returns empty content. Live spend so far is
  fractions of a cent against the $2 free credit; no payment method on the account.
- Client changes for live mode (all in `otari.py`, tests still 38/38): Otari-Key auth
  via OTARI_AUTH env (Bearer kept for the docs shape), max_tokens 400 on gateway calls,
  retry on dropped connections and on 429s, and an empty OTARI_CHAT_PATH counts as the
  default path (an empty value previously built a pathless URL, which the gateway 403d).
  `demo/capture_otari_live.py` now passes OTARI_AUTH + proxy vars through and prints
  the app's error body on failure.
- Demo: stub video `quizforge-otari/demo/quizforge-otari-demo.mp4` (+ `demo-script.md`,
  `shots/`) AND live video `quizforge-otari/demo/quizforge-otari-demo-live.webm` with
  `transcript-compare-live.json` + live stills (`01-compare-tab-live-banner.png`,
  `02-compare-results-live.png`). Both are genuine Playwright screen recordings of the
  running app, each labeled with its mode on screen. The live capture refuses to record
  unless `/api/otari-status` reads live.

## Registration (parent steps — email sent, account created, do NOT redo)

1. Onboarding doc: https://www.otari.ai/devs-wilding
2. Registration email to marcus+wilding@mozilla.org — SENT 2026-11-02 from the personal
   Gmail (parent step, done).
3. Otari signup at https://otari.ai (free) — DONE 2026-11-02 (arc.agent.ops@gmail.com,
   $2.00 free credit, no payment method). DoraHacks application is part of submission below.

## Submission (remaining steps, in order)

1. ~~Live key + live compare + live demo re-capture + tests + repo push~~ — DONE
   2026-11-02 (see Build state above).
2. Submit repo + demo on DoraHacks at https://dorahacks.io/hackathon/mozilla-devs-wilding/detail
   before Nov 11 — the ONLY remaining step (parent step).
5. No EOD content anywhere in the entry.

## Sources verified 2026-11-02

- dev.to announcement (Oct 28, 2026): prizes $1,000/$200 + engineer hours.
- Eventbrite: "Mozilla Otari Hackathon - Devs Wilding Online!", free ticket.
