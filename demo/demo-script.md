# QuizForge Otari Edition — demo script (full walkthrough narration)

The shipped clip (`demo/quizforge-otari-demo.mp4`, ~17s) is a short silent screen
recording of the real comparison flow — tab, stub banner, run, DIFFER verdict. The
script below is the full ~2-minute narration for a live walkthrough, or for a
re-recorded narrated cut. Every claim below is what the app actually shows. The
recording runs in STUB mode (no Otari key) and says so on screen — say that out
loud; do not present stub answers as live model output.

## 0:00 — The pitch (15s)

"QuizForge turns study notes into a live study loop — quiz, grade, adapt. The Otari
Edition adds the one thing only a gateway can do: ask TWO open-weight models the same
question and show where they agree, differ, and why."

## 0:15 — The setup (30s)

"Here's the app. Three tabs: the one-shot quiz, the Live study loop, and the new one —
Compare models. The banner is honest about the mode: with no key configured, this demo
runs labeled stub answers so the comparison view itself can be verified. With a key and
the gateway configured, these panels are real Otari models."

Show: the Compare tab, the stub banner, the prefilled first-aid question.

## 0:45 — The comparison (45s)

"One question, same prompt to both models. Watch what happens when they don't agree."

Click "Run both models." Show: both panels, the ❌ DIFFER badge, the verdict — "The
models disagree — neither one settles it. Go back to the study material" — and the
evidence line: only 23% of content words overlap.

"The point isn't which model won. The point is the learner sees model choice as a
decision, and the study material stays the authority. Agreement is not correctness."

## 1:30 — The loop behind it (30s)

"And the rest of QuizForge is still here: paste notes, get a quiz, get graded, and the
next round adapts to what you missed — the plan, grade, and adapt loop from the
GenAI Works entry, unchanged. Otari changes the model layer, not the pedagogy."

## 2:00 — Close (one line)

"QuizForge Otari Edition: the same study loop, with model comparison built in —
because two models disagreeing is a better teacher than one model sounding sure."

## Live-mode note (for judges, not narration)

To run this demo against live Otari models: sign up at https://otari.ai, set
OTARI_API_KEY, OTARI_BASE_URL, OTARI_MODEL_A, OTARI_MODEL_B from the onboarding doc
at https://www.otari.ai/devs-wilding, confirm the endpoint shape (the client assumes
OpenAI-compatible POST {base}/chat/completions), and re-run `demo/capture_otari.py`
with those vars set. The banner will read LIVE and name both real models.
