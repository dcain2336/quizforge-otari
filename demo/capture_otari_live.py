# capture_otari_live.py - live-mode variant of capture_otari.py. Demo tooling, not part of the shipped app.
# Run ONLY with the Otari gateway values in the environment (OTARI_API_KEY, OTARI_BASE_URL,
# OTARI_MODEL_A, OTARI_MODEL_B, optional OTARI_CHAT_PATH). The key is passed to the server
# process only; it is never printed, never written to any captured file, and never committed.
# Outputs are suffixed -live so they sit alongside (never overwrite) the stub demo.
# The server here runs with the real gateway env, so the recording shows the LIVE banner and
# genuine model answers. If the gateway is unreachable or unconfigured, the app fails loudly
# instead of silently falling back to stub answers on screen.
import json  # Make the json module available.
import os  # Make the os module available.
import subprocess  # Manage the server child process.
import sys  # Reuse the same Python interpreter for the server.
import time  # Poll for server startup.
import urllib.request  # Drive the API flow and confirm the comparison payload.
from playwright.sync_api import sync_playwright  # The browser driver for video + screenshots.

HERE = os.path.dirname(os.path.abspath(__file__))  # This demo/ folder.
PROJECT = os.path.dirname(HERE)  # app.py and the modules live one level up.
SHOTS = os.path.join(HERE, "shots")  # Stills go in demo/shots/.
VIDEO_DIR = os.path.join(HERE, "video-tmp-live")  # Playwright writes the raw recording here first.
APP_URL = "http://127.0.0.1:8793"  # The demo server's local URL (different port from the stub capture).
# Pass the gateway env through to the server, and nothing else secret-like. Missing values
# mean the app reports stub mode, which this script refuses to record (see the mode check below).
SERVER_ENV = {
    "PATH": os.environ.get("PATH", ""),
    "PORT": "8793",
    "LANG": "C.UTF-8",
    "OTARI_API_KEY": os.environ.get("OTARI_API_KEY", ""),
    "OTARI_BASE_URL": os.environ.get("OTARI_BASE_URL", ""),
    "OTARI_MODEL_A": os.environ.get("OTARI_MODEL_A", ""),
    "OTARI_MODEL_B": os.environ.get("OTARI_MODEL_B", ""),
    "OTARI_CHAT_PATH": os.environ.get("OTARI_CHAT_PATH", ""),
}  # Gateway values only; the key travels to the child process, never to stdout or files.
QUESTION = "What is the first step of first aid for a bleeding wound?"  # The demo question, same as the stub capture.

os.makedirs(SHOTS, exist_ok=True)  # Prepare the stills folder.
os.makedirs(VIDEO_DIR, exist_ok=True)  # Prepare the raw video folder.

server = subprocess.Popen(  # Start the real app server as a child process.
    [sys.executable, os.path.join(PROJECT, "app.py")],  # The app entry point.
    env=SERVER_ENV, cwd=PROJECT,  # Gateway env, project working directory.
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Keep the demo output clean.
try:  # Guard the whole capture so the server always stops afterwards.
    for _ in range(50):  # Poll for startup, up to ~5 seconds.
        try:  # Try the health endpoint.
            with urllib.request.urlopen(APP_URL + "/health", timeout=1) as resp:  # Health check.
                if resp.status == 200:  # Server is up.
                    break  # Stop polling.
        except Exception:  # Not up yet (or still starting).
            time.sleep(0.1)  # Wait a beat, then retry.
    else:  # The poll loop never saw a healthy server.
        raise RuntimeError("Demo server did not start.")  # Fail loudly, not silently.
    with urllib.request.urlopen(APP_URL + "/api/otari-status", timeout=5) as resp:  # Confirm live mode before recording.
        status = json.loads(resp.read().decode("utf-8"))  # The mode snapshot (never contains the key).
    if status.get("mode") != "live":  # Stub mode here would mean the env did not reach the server.
        raise RuntimeError("Refusing to record: gateway status is '%s', not live." % status.get("mode"))  # Fail loudly, not silently.
    req = urllib.request.Request(  # Build the comparison POST for the transcript.
        APP_URL + "/api/compare",  # The comparison endpoint.
        data=json.dumps({"question": QUESTION, "context": "Apply direct pressure."}).encode("utf-8"),  # The demo payload.
        headers={"Content-Type": "application/json"}, method="POST")  # JSON POST.
    with urllib.request.urlopen(req, timeout=90) as resp:  # Run the real live comparison (gateway calls can queue).
        payload = json.loads(resp.read().decode("utf-8"))  # The verbatim server reply.
    with open(os.path.join(HERE, "transcript-compare-live.json"), "w") as handle:  # Save the live transcript.
        json.dump(payload, handle, indent=2)  # Pretty-printed, unmodified content.
    with sync_playwright() as pw:  # Open the browser driver.
        browser = pw.chromium.launch()  # Headless Chromium.
        context = browser.new_context(  # A fresh browser context with video recording on.
            viewport={"width": 1280, "height": 800},  # Demo-sized viewport.
            record_video_dir=VIDEO_DIR, record_video_size={"width": 1280, "height": 800})  # Record the session.
        page = context.new_page()  # Open the demo page.
        page.goto(APP_URL + "/", wait_until="networkidle")  # Load the app.
        page.click("#tabCompareBtn")  # Switch to the Compare tab.
        page.wait_for_selector("#compareMode")  # Wait for the gateway banner.
        time.sleep(4)  # Hold the banner on screen so the recording reads clearly.
        page.screenshot(path=os.path.join(SHOTS, "01-compare-tab-live-banner.png"))  # Still 1: the live banner.
        page.click("#compareRunBtn")  # Run the comparison with the prefilled question.
        page.wait_for_selector("#compareResultsCard:not(.hidden)", timeout=90000)  # Wait for live results (gateway can queue).
        time.sleep(12)  # Hold the results on screen so the recording reads clearly.
        page.screenshot(path=os.path.join(SHOTS, "02-compare-results-live.png"), full_page=True)  # Still 2: both panels + verdict.
        context.close()  # Close the context, which finalizes the video file.
        browser.close()  # Close the browser.
    videos = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".webm")]  # Playwright records webm.
    if not videos:  # No recording appeared.
        raise RuntimeError("No demo video was recorded.")  # Fail loudly.
    src = os.path.join(VIDEO_DIR, videos[0])  # The recorded file.
    dst = os.path.join(HERE, "quizforge-otari-demo-live.webm")  # The shipped live demo video.
    os.replace(src, dst)  # Move it to its final name.
    print("Live demo captured: %s" % dst)  # Confirm the artifact.
    print("Stills: %s" % SHOTS)  # Confirm the stills.
    print("Comparison mode: %s, agreement: %s" % (payload["mode"], payload["agreement"]))  # Confirm the honest labels.
finally:  # Always stop the server, even on failure.
    server.terminate()  # Ask the server to stop.
    try:  # Wait briefly for a clean exit.
        server.wait(timeout=5)  # Up to 5 seconds.
    except subprocess.TimeoutExpired:  # It did not stop in time.
        server.kill()  # Force it.
