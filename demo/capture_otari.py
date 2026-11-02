# capture_otari.py - run the real QuizForge Otari Edition app offline and capture a genuine
# demo video plus stills of the comparison flow. Demo tooling, not part of the shipped app.
# Honesty contract: the server runs with a scrubbed environment (no API keys), so every
# response below is the app's real stub path, labeled STUB on screen. No mocked data anywhere:
# the video records the actual browser session, and the transcript is the server's verbatim reply.
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
VIDEO_DIR = os.path.join(HERE, "video-tmp")  # Playwright writes the raw recording here first.
APP_URL = "http://127.0.0.1:8792"  # The demo server's local URL.
SERVER_ENV = {"PATH": os.environ.get("PATH", ""), "PORT": "8792", "LANG": "C.UTF-8"}  # No API keys: stub mode is forced and labeled by the app itself.
QUESTION = "What is the first step of first aid for a bleeding wound?"  # The demo question.

os.makedirs(SHOTS, exist_ok=True)  # Prepare the stills folder.
os.makedirs(VIDEO_DIR, exist_ok=True)  # Prepare the raw video folder.

server = subprocess.Popen(  # Start the real app server as a child process.
    [sys.executable, os.path.join(PROJECT, "app.py")],  # The app entry point.
    env=SERVER_ENV, cwd=PROJECT,  # Scrubbed env, project working directory.
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
    req = urllib.request.Request(  # Build the comparison POST for the transcript.
        APP_URL + "/api/compare",  # The comparison endpoint.
        data=json.dumps({"question": QUESTION, "context": "Apply direct pressure."}).encode("utf-8"),  # The demo payload.
        headers={"Content-Type": "application/json"}, method="POST")  # JSON POST.
    with urllib.request.urlopen(req, timeout=10) as resp:  # Run the real comparison.
        payload = json.loads(resp.read().decode("utf-8"))  # The verbatim server reply.
    with open(os.path.join(HERE, "transcript-compare.json"), "w") as handle:  # Save the transcript.
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
        page.screenshot(path=os.path.join(SHOTS, "01-compare-tab-stub-banner.png"))  # Still 1: the stub banner.
        page.click("#compareRunBtn")  # Run the comparison with the prefilled question.
        page.wait_for_selector("#compareResultsCard:not(.hidden)", timeout=15000)  # Wait for results.
        time.sleep(12)  # Hold the results on screen so the recording reads clearly.
        page.screenshot(path=os.path.join(SHOTS, "02-compare-results-differ.png"), full_page=True)  # Still 2: both panels + verdict.
        context.close()  # Close the context, which finalizes the video file.
        browser.close()  # Close the browser.
    videos = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".webm")]  # Playwright records webm.
    if not videos:  # No recording appeared.
        raise RuntimeError("No demo video was recorded.")  # Fail loudly.
    src = os.path.join(VIDEO_DIR, videos[0])  # The recorded file.
    dst = os.path.join(HERE, "quizforge-otari-demo.webm")  # The shipped demo video.
    os.replace(src, dst)  # Move it to its final name.
    print("Demo captured: %s" % dst)  # Confirm the artifact.
    print("Stills: %s" % SHOTS)  # Confirm the stills.
    print("Comparison mode: %s, agreement: %s" % (payload["mode"], payload["agreement"]))  # Confirm the honest labels.
finally:  # Always stop the server, even on failure.
    server.terminate()  # Ask the server to stop.
    try:  # Wait briefly for a clean exit.
        server.wait(timeout=5)  # Up to 5 seconds.
    except subprocess.TimeoutExpired:  # It did not stop in time.
        server.kill()  # Force it.
