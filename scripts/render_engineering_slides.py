"""Render designed engineering storyboard frames beside sanitized app captures."""
from __future__ import annotations

import os
import signal
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "media" / "engineering-video-slides.html"
SCREENSHOTS = ROOT / "media" / "provided-app-screenshots" / "engineering"
OUTPUT = ROOT / "media" / "engineering-slides" / "rendered"
ATTRIBUTION_STRIP = ROOT / "media" / "video-attribution-strip.png"
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
COUNT = 14


def chrome_binary() -> str:
    configured = os.environ.get("CHROME_BIN")
    candidates = [configured] if configured else []
    candidates += [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise RuntimeError("Chrome/Chromium not found. Set CHROME_BIN to its executable path.")


def render() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    attribution = (ROOT / "media" / "video-attribution.txt").read_text(encoding="utf-8").strip()
    if attribution not in SOURCE.read_text(encoding="utf-8"):
        raise RuntimeError("The storyboard attribution and NOTICE text have drifted apart")
    browser = chrome_binary()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cafemesh-slides-") as profile:
        for index in range(COUNT):
            screenshot = SCREENSHOTS / f"scene-{index:02}.png"
            if not screenshot.is_file():
                raise FileNotFoundError(f"Sanitized screenshot scene missing: {screenshot}")
            target = OUTPUT / f"scene-{index:02}.png"
            url = SOURCE.as_uri() + f"?scene={index}"
            target.unlink(missing_ok=True)
            process = subprocess.Popen(
                [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                 "--disable-background-networking", "--disable-component-update",
                 "--disable-sync", "--disable-extensions", "--no-first-run",
                 "--no-default-browser-check", "--allow-file-access-from-files",
                 f"--user-data-dir={profile}", "--window-size=1280,720",
                 "--force-device-scale-factor=1", "--virtual-time-budget=900",
                 f"--screenshot={target}", url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
            )
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if target.is_file() and target.stat().st_size > 20_000:
                    break
                if process.poll() is not None:
                    raise RuntimeError(f"Chrome exited before rendering scene {index} (code {process.returncode})")
                time.sleep(0.1)
            else:
                raise TimeoutError(f"Timed out rendering engineering slide {index}")
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)
            if not target.is_file() or target.stat().st_size < 20_000:
                raise RuntimeError(f"Unexpectedly small rendered scene: {target}")
    subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i",
         str(OUTPUT / "scene-00.png"), "-vf", "crop=1280:30:0:690", "-frames:v", "1",
         "-update", "1", str(ATTRIBUTION_STRIP)],
        check=True,
    )
    print(f"Rendered {COUNT} engineering slides with corresponding sanitized app captures.")


if __name__ == "__main__":
    render()
