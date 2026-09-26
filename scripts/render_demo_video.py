"""Render walkthroughs from supplied screenshots with paragraph-synced narration."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")
ATTRIBUTION = ROOT / "media" / "video-attribution.txt"
ATTRIBUTION_STRIP = ROOT / "media" / "video-attribution-strip.png"
BUILDS = {
    "product": {
        "audio": ROOT / "frontend/public/audio/cafemesh-product-walkthrough.mp3",
        "timing": ROOT / "media/cafemesh-product-walkthrough-timing.json",
        "output": ROOT / "frontend/public/videos/cafemesh-product-walkthrough.mp4",
        "scenes": ROOT / "media/video-scenes/product",
        "provided_scenes": ROOT / "media/provided-app-screenshots/product",
        "count": 12,
    },
    "engineering": {
        "audio": ROOT / "frontend/public/audio/cafemesh-engineering-walkthrough.mp3",
        "timing": ROOT / "media/cafemesh-engineering-walkthrough-timing.json",
        "output": ROOT / "frontend/public/videos/cafemesh-engineering-walkthrough.mp4",
        "scenes": ROOT / "media/video-scenes/engineering",
        "provided_scenes": ROOT / "media/provided-app-screenshots/engineering",
        "rendered_scenes": ROOT / "media/engineering-slides/rendered",
        "layout": "engineering_hybrid",
        "count": 14,
    },
}


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of",
         "default=noprint_wrappers=1:nokey=1", str(path)], check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def render_slides(build: dict, segments: list[dict]) -> None:
    scenes = build["scenes"]
    scenes.mkdir(parents=True, exist_ok=True)
    if len(segments) != build["count"]:
        raise ValueError(f"Expected {build['count']} narration paragraphs, found {len(segments)}")
    lines: list[str] = []
    for index, row in enumerate(segments):
        image = scenes / f"scene-{index:02}.png"
        image.unlink(missing_ok=True)
        supplied_image = (build.get("rendered_scenes") or build["provided_scenes"]) / f"scene-{index:02}.png"
        if not supplied_image.is_file():
            raise FileNotFoundError(f"Expected user-supplied screenshot scene: {supplied_image}")
        shutil.copy2(supplied_image, image)
        lines.extend((f"file 'scene-{index:02}.png'", f"duration {float(row['duration']):.3f}"))
        continue
    lines.append(f"file 'scene-{build['count'] - 1:02}.png'")
    (scenes / "concat.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def render(kind: str) -> Path:
    build = BUILDS[kind]
    for path in (build["audio"], build["timing"]):
        if not path.is_file():
            raise FileNotFoundError(path)
    manifest = json.loads(build["timing"].read_text(encoding="utf-8"))
    duration = probe_duration(build["audio"])
    segments = manifest["segments"]
    if not 90 < duration < 600:
        raise ValueError(f"Unexpected {kind} narration duration: {duration:.1f}s")
    # Match slide cue boundaries to the final encoded narration duration.
    source_total = sum(float(item["duration"]) for item in segments)
    if source_total <= 0:
        raise ValueError("Timing manifest contains no positive narration durations")
    scale = duration / source_total
    aligned = [{"duration": float(item["duration"]) * scale} for item in segments]
    if build.get("layout") == "engineering_hybrid":
        subprocess.run([sys.executable, str(ROOT / "scripts" / "render_engineering_slides.py")], check=True)
    elif not ATTRIBUTION_STRIP.is_file():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "render_engineering_slides.py")], check=True)
    render_slides(build, aligned)
    build["output"].parent.mkdir(parents=True, exist_ok=True)
    if not ATTRIBUTION.is_file():
        raise FileNotFoundError(f"Required visible media attribution is missing: {ATTRIBUTION}")
    subprocess.run([
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i",
        str(build["scenes"] / "concat.txt"), "-i", str(build["audio"]), "-loop", "1", "-framerate", "30",
        "-i", str(ATTRIBUTION_STRIP), "-filter_complex", "[0:v][2:v]overlay=0:690:eof_action=repeat:shortest=1[vout]",
        "-map", "[vout]", "-map", "1:a:0", "-t", f"{duration:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
        str(build["output"]),
    ], check=True)
    video_duration = probe_duration(build["output"])
    if abs(video_duration - duration) > .25:
        raise RuntimeError(f"Audio/video duration mismatch: audio {duration:.3f}s, video {video_duration:.3f}s")
    print(f"{kind}: {build['output'].relative_to(ROOT)} | {duration:.2f}s | {len(segments)} narration-aligned scenes | A/V delta {abs(video_duration-duration):.3f}s")
    return build["output"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=BUILDS, help="Which narrated walkthrough to render")
    args = parser.parse_args()
    render(args.kind)
