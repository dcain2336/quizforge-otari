# otari.py - the Mozilla Otari open-weight gateway client for QuizForge Otari Edition.  # Module header: what this file is.
# QuizForge Otari Edition keeps the Live study loop and swaps the model layer to Otari,  # Design choice 1: the port keeps the core, changes only the model route.
# Mozilla's open-weight gateway. The Otari-native wedge is multi-model comparison: the same  # Design choice 2: comparison is the wedge, not a re-skin.
# question goes to two open-weight models through the gateway, and the app shows where they  # Design choice 2 continued: agree, differ, and why.
# agree, differ, and why, so the learner sees model choice as a visible decision, not magic.  # Design choice 2 continued: the judging edge.
# HONEST STATE (2026-11-02): no Otari API key is on record and the gateway's exact base URL  # Honesty: what is verified and what is not.
# and model slugs were NOT verified live — the onboarding doc at otari.ai/devs-wilding could  # Honesty continued: the doc fetch failed, so nothing here is claimed verified.
# not be fetched from this environment. So the base URL and model slugs are fully  # Honesty continued: everything gateway-shaped is env-configurable.
# environment-configurable, and with no key configured the module runs in STUB mode: it returns  # Honesty continued: stub mode is the default, and it says so.
# clearly labeled demonstration answers so the comparison view can be verified end to end.  # Honesty continued: stub answers exist to verify the view.
# Stub mode NEVER pretends to be live: every stub response carries mode "stub" and the UI  # Honesty continued: the stub label travels with the data.
# banners it. Set OTARI_API_KEY + OTARI_BASE_URL + model slugs to go live, and confirm the  # How to go live: the three values plus the doc check.
# endpoint shape against the onboarding doc first — the client assumes an OpenAI-compatible  # Assumption flagged: OpenAI-compatible chat completions.
# POST {base}/chat/completions with a Bearer key, which is the shape Otari documents for its  # Assumption continued: the documented gateway shape.
# gateway; if the doc shows a different path, set OTARI_CHAT_PATH to match.  # Escape hatch: one env var fixes a different path.
# SECURITY RULE: the Otari key lives in the environment (or a local .env file), NEVER in code  # Security rule: where the key lives.
# or this repo. This module reads it at call time and never prints it.  # Security rule continued: the key is never echoed.
# Zero third-party dependencies: it uses only Python's standard library, like the rest of QuizForge.  # Design choice 3: no installs needed.
# Import the JSON module so requests can be encoded and replies decoded.  # Library: json.
import json  # Make the json module available.
# Import the OS module so keys, URLs, and model slugs can be read from the environment.  # Library: os.
import os  # Make the os module available.
# Import the regular-expression module so answers can be normalized for comparison.  # Library: re.
import re  # Make the re module available.
# Import urllib.request so gateway calls work with zero third-party packages.  # Library: urllib.request.
import urllib.request  # Make the urllib.request module available.
# Import urllib.error so HTTP failures can be caught and reported cleanly.  # Library: urllib.error.
import urllib.error  # Make the urllib.error module available.
# Define the default chat path, overridden by OTARI_CHAT_PATH if the doc shows another.  # Constant: chat path default.
DEFAULT_CHAT_PATH = "/chat/completions"  # The OpenAI-compatible chat path, per the gateway assumption above.
# Define how long (in seconds) a gateway call may take before we give up.  # Constant: HTTP timeout.
HTTP_TIMEOUT_SECONDS = 60  # Gateway answers on shared tiers can queue; 60s matches the study-loop pace.
# Define a browser-like user agent, because some API edges reject the default Python one.  # Constant: user agent string.
USER_AGENT = "curl/8.0"  # A plain user agent that API edges accept reliably.
# Define the words ignored when measuring answer overlap, so filler cannot fake agreement.  # Constant: stopword set.
STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are", "was", "were", "it", "its", "that", "this", "as", "by", "at", "be", "from", "which", "you", "your"}  # Common filler words, excluded from the overlap math.
# Start the exception type raised when a live gateway call cannot produce an answer.  # Class: OtariError.
class OtariError(Exception):  # Define OtariError, a plain exception with a message.
    pass  # No extra behavior: it is just a labeled error.
# Start the getter that reads the gateway base URL fresh from the environment.  # Function: _base_url.
def _base_url():  # Define _base_url, which returns the gateway base URL each time it is called.
    # Read OTARI_BASE_URL live at call time, so a .env loaded after import still works.  # Why live: env may load after import.
    # Empty until configured: no unverified default URL is baked in.  # Why empty: the doc fetch failed, so no URL is claimed.
    return os.environ.get("OTARI_BASE_URL", "").rstrip("/")  # The gateway root, without a trailing slash.
# Start the getter that reads the Otari API key fresh from the environment.  # Function: _api_key.
def _api_key():  # Define _api_key, which returns the API key or an empty string.
    # Read OTARI_API_KEY live at call time, for the same late-load reason as the URL.  # Why live: same late-load reason.
    return os.environ.get("OTARI_API_KEY", "")  # Empty means stub mode; the key is never logged or returned.
# Start the getter that reads the chat path fresh from the environment.  # Function: _chat_path.
def _chat_path():  # Define _chat_path, which returns the chat path each time it is called.
    # Read OTARI_CHAT_PATH live, defaulting to the OpenAI-compatible path.  # Why live: the doc may show a different path.
    return os.environ.get("OTARI_CHAT_PATH", DEFAULT_CHAT_PATH)  # One override fixes a doc mismatch.
# Start the predicate that reports whether live gateway calls are possible.  # Function: is_configured.
def is_configured():  # Define is_configured, which returns True only when key and URL both exist.
    # Both values are required: a key with no URL (or the reverse) cannot make a call.  # Rule: both or neither.
    return bool(_api_key() and _base_url())  # True only when a live call has somewhere to go and a key to use.
# Start the getter that names the two comparison models, live slugs or honest stub labels.  # Function: get_models.
def get_models():  # Define get_models, which returns the (model_a, model_b) pair.
    # Read the env slugs live; fall back to labels that say "stub" out loud.  # Why stub labels: a demo model must never pose as a real one.
    model_a = os.environ.get("OTARI_MODEL_A", "") or "model-a (stub)"  # First comparison model, or its stub label.
    model_b = os.environ.get("OTARI_MODEL_B", "") or "model-b (stub)"  # Second comparison model, or its stub label.
    return (model_a, model_b)  # Hand the pair back to the caller.
# Start the status reporter the UI banner and /api/otari-status both read.  # Function: status.
def status():  # Define status, which returns the gateway configuration snapshot.
    # Report mode and model names only: the key is never included in any output.  # Security: the snapshot carries no secret.
    model_a, model_b = get_models()  # Resolve the two model names for display.
    return {"configured": is_configured(), "mode": "live" if is_configured() else "stub", "model_a": model_a, "model_b": model_b, "base_url_set": bool(_base_url())}  # Mode, models, and whether a URL exists — nothing secret.
# Start the live chat caller: one prompt, one model, one text reply.  # Function: chat.
def chat(prompt, model):  # Define chat, which calls the gateway and returns the model's text.
    # Refuse to call live without configuration, instead of failing obscurely downstream.  # Guard: configuration comes first.
    if not is_configured():  # No key or no URL means no live call is possible.
        raise OtariError("Otari is not configured: set OTARI_API_KEY and OTARI_BASE_URL (see .env.example).")  # Say exactly which values are missing.
    # Build the OpenAI-compatible request body: model plus a single user message.  # Step: request body.
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}  # The gateway's chat shape, per the documented assumption.
    # Encode the body as UTF-8 JSON bytes for the POST.  # Step: encode the body.
    body = json.dumps(payload).encode("utf-8")  # Convert the dictionary into bytes.
    # Build the POST request against the configured base URL plus the chat path.  # Step: request object.
    request = urllib.request.Request(_base_url() + _chat_path(), data=body, method="POST")  # The full gateway URL for this call.
    # Declare the body as JSON so the gateway parses it.  # Step: content-type header.
    request.add_header("Content-Type", "application/json")  # Tell the gateway the body is JSON.
    # Attach the key as a Bearer token, the gateway's auth shape.  # Step: auth header.
    request.add_header("Authorization", "Bearer " + _api_key())  # The key travels only in this header.
    # Use the browser-like user agent so the edge does not reject the call.  # Step: user-agent header.
    request.add_header("User-Agent", USER_AGENT)  # A plain user agent that API edges accept.
    try:  # Begin the guarded call, so gateway failures become a readable OtariError.
        # Open the URL with the timeout, and read the reply inside the context manager.  # Step: perform the call.
        with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:  # Send the POST and hold the reply.
            raw = response.read().decode("utf-8")  # Read the reply body as text.
    except urllib.error.HTTPError as err:  # The gateway answered with an HTTP error status.
        raise OtariError("Otari gateway HTTP %s (check OTARI_API_KEY, OTARI_BASE_URL, and model slug)." % err.code)  # Report the status, not the key.
    except urllib.error.URLError as err:  # The gateway could not be reached at all.
        raise OtariError("Otari gateway unreachable: %s (check OTARI_BASE_URL)." % err.reason)  # Report the reachability failure.
    # Parse the reply body as JSON, failing readably if it is not JSON.  # Step: parse the reply.
    try:  # Begin the guarded parse, so a non-JSON reply becomes a readable error.
        data = json.loads(raw)  # Convert the reply text into a dictionary.
    except ValueError:  # The reply was not valid JSON.
        raise OtariError("Otari gateway returned a non-JSON reply.")  # Say the reply was unusable.
    # Pull the assistant text out of the OpenAI-compatible choices shape.  # Step: extract the answer.
    try:  # Begin the guarded extraction, so a shape mismatch becomes a readable error.
        text = data["choices"][0]["message"]["content"]  # The first choice's message content.
    except (KeyError, IndexError, TypeError):  # The reply lacked the expected shape.
        raise OtariError("Otari gateway reply had an unexpected shape (expected OpenAI-compatible choices).")  # Name the expected shape.
    return text.strip()  # Hand back the answer text, with outer whitespace trimmed.
# Start the normalizer that turns an answer into comparable content words.  # Function: _content_words.
def _content_words(text):  # Define _content_words, which returns the set of meaningful words in a text.
    # Lowercase, split on non-letters, drop stopwords and single letters.  # Rule: case and filler must not affect agreement.
    words = re.findall(r"[a-z]+", text.lower())  # All lowercase letter-runs in the answer.
    return {word for word in words if word not in STOPWORDS and len(word) > 1}  # The meaningful vocabulary, as a set.
# Start the agreement measurer: two answers in, one verdict plus a note out.  # Function: measure_agreement.
def measure_agreement(answer_a, answer_b):  # Define measure_agreement, which compares two answers.
    # Measure overlap over content words with the Jaccard index (shared / combined).  # Method: shared vocabulary over combined vocabulary.
    words_a = _content_words(answer_a)  # The first answer's meaningful vocabulary.
    words_b = _content_words(answer_b)  # The second answer's meaningful vocabulary.
    # Handle the empty edge first: two empty answers carry no signal either way.  # Edge: empties cannot agree.
    if not words_a or not words_b:  # Either answer has no meaningful words.
        return ("differ", "One of the answers carried no checkable content, so agreement cannot be claimed.")  # Honest verdict for empty input.
    # Compute the shared vocabulary and the combined vocabulary.  # Step: overlap sets.
    shared = words_a & words_b  # Words both answers use.
    combined = words_a | words_b  # Words either answer uses.
    # Divide shared by combined to get the overlap score between 0 and 1.  # Step: Jaccard score.
    score = len(shared) / len(combined)  # 1.0 means identical vocabulary; 0.0 means none shared.
    # Map the score to a verdict with plain-language thresholds.  # Rule: high overlap agrees, low overlap differs, middle is partial.
    if score >= 0.6:  # Most of the vocabulary is shared.
        return ("agree", "Both models cover substantially the same ground (overlap %.0f%% of content words)." % (score * 100))  # Agreement verdict with its evidence.
    if score >= 0.3:  # Some ground is shared, but real differences remain.
        return ("partial", "The models partly overlap (%.0f%% of content words) but diverge on real points — check the study material on the difference." % (score * 100))  # Partial verdict with its evidence.
    return ("differ", "The models go in different directions (only %.0f%% of content words overlap) — treat neither as settled until the study material is checked." % (score * 100))  # Difference verdict with its evidence.
# Start the stub answer builder: deterministic demo answers that visibly disagree.  # Function: _stub_answer.
def _stub_answer(question, which):  # Define _stub_answer, which returns a labeled demo answer for a question.
    # Stub answers are templated around the question so ANY question demonstrates the view.  # Why templated: the demo must work on any input.
    # Model A answers short and direct; model B answers longer with an extra claim.  # Why they differ: the view needs a real disagreement to show.
    if which == "a":  # First stub model: the concise answerer.
        return ("Short answer: the key point behind \"%s\" is the one your study material states most directly — "  # Stub A opens with its direct claim.
                "learn that first, then build outward. Bottom line: master the core statement before the details.") % question  # Stub A closes with its bottom line.
    # Second stub model: the expansive answerer, with a debatable extra claim.  # Stub B's role: breadth plus one claim to check.
    return ("A fuller view on \"%s\": the core statement matters, but so do the exceptions and edge cases around it — "  # Stub B opens with its broader claim.
            "a good answer names both the rule and where it bends. Bottom line: know the rule, the exceptions, and when each applies.") % question  # Stub B closes with a different bottom line.
# Start the comparison entry point: same question, two models, one verdict.  # Function: compare.
def compare(question, context=""):  # Define compare, which runs one question through both models and judges agreement.
    # Reject an empty question instead of comparing nothing.  # Guard: a comparison needs a question.
    if not question or not question.strip():  # The question is missing or blank.
        raise ValueError("compare needs a non-empty question.")  # Say what is missing.
    # Resolve the two model names once, so live and stub paths label identically.  # Step: model names.
    model_a, model_b = get_models()  # The pair of models for this comparison.
    # Build the shared prompt: the same words go to both models, so any difference is theirs.  # Rule: identical input, so output differences are model differences.
    prompt = ("Answer this study question concisely, using only the study material below. "  # Prompt part 1: the task and the grounding rule.
              "End with a line starting 'Bottom line:' that states your final answer in one sentence.\n\n"  # Prompt part 2: the bottom-line format, which the verdict can lean on.
              "Study material:\n%s\n\nQuestion: %s" % (context.strip() or "(no study material supplied)", question.strip()))  # Prompt part 3: material plus question.
    # Route to stub mode when the gateway is not configured; the stub label travels with the result.  # Branch: stub when unconfigured.
    if not is_configured():  # No key or no URL means no live call is possible.
        answer_a = _stub_answer(question.strip(), "a")  # Stub A's deterministic demo answer.
        answer_b = _stub_answer(question.strip(), "b")  # Stub B's deterministic demo answer.
        mode = "stub"  # The result is labeled stub, never live.
    else:  # The gateway is configured, so both models get the same live prompt.
        answer_a = chat(prompt, model_a)  # Model A's live answer.
        answer_b = chat(prompt, model_b)  # Model B's live answer.
        mode = "live"  # The result is genuinely from the gateway.
    # Measure agreement between the two answers, whatever their source.  # Step: verdict.
    agreement, note = measure_agreement(answer_a, answer_b)  # The verdict plus its plain-language evidence.
    # Build the verdict the learner acts on: agreement is not correctness, so differ means check.  # Rule: the verdict always points back to the material.
    if agreement == "agree":  # Both models landed in the same place.
        verdict = "Both models agree — that raises confidence, but the study material is still the authority. Re-read it once before moving on."  # Agreement verdict for the learner.
    elif agreement == "partial":  # The models partly overlap.
        verdict = "The models partly agree — trust the shared ground, and settle the difference from the study material, not from either model alone."  # Partial verdict for the learner.
    else:  # The models genuinely differ.
        verdict = "The models disagree — neither one settles it. Go back to the study material and decide which answer it actually supports."  # Difference verdict for the learner.
    # Return the full comparison package: mode, both panels, verdict, and note.  # Step: package.
    return {"mode": mode, "question": question.strip(), "model_a": {"model": model_a, "answer": answer_a}, "model_b": {"model": model_b, "answer": answer_b}, "agreement": agreement, "agreement_note": note, "verdict": verdict}  # Everything the view renders, in one dictionary.
