"""Generate a narrated MP3 with Google Cloud Gemini-TTS."""
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

from google.cloud import texttospeech


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "frontend" / "public" / "audio"
MAX_TEXT_BYTES = 3_600
DEFAULT_PROMPT = (
    "Narrate warmly and clearly for a polished Indian product demo. Use a natural, "
    "confident Indian English accent, moderate pace, crisp pronunciation, and brief "
    "pauses between paragraphs. Do not sound overly promotional."
)


def split_text(text: str, max_bytes: int = MAX_TEXT_BYTES) -> list[str]:
    """Split at paragraph/sentence boundaries while staying within the API byte limit."""
    paragraphs = [part.strip() for part in text.strip().split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        sentences = [s.strip() for s in paragraph.replace("! ", "!\n").replace("? ", "?\n").replace(". ", ".\n").splitlines() if s.strip()]
        for sentence in sentences:
            if len(sentence.encode("utf-8")) > max_bytes:
                raise ValueError("A single narration sentence exceeds the configured text byte limit")
            candidate = f"{current} {sentence}".strip()
            if current and len(candidate.encode("utf-8")) > max_bytes:
                chunks.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append(current)
            current = ""
    return chunks


def audio_duration(path: Path) -> float:
    result = subprocess.run(
        [os.environ.get("FFPROBE", "ffprobe"), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        check=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def synthesize(text: str, output_name: str = "cafemesh-product-walkthrough.mp3", timing_name: str | None = None) -> Path:
    if not text.strip():
        raise ValueError("Narration text must not be empty")
    if Path(output_name).name != output_name or not output_name.endswith(".mp3"):
        raise ValueError("Output must be an MP3 filename inside the audio asset folder")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project:
        raise ValueError("GOOGLE_CLOUD_PROJECT must be set for authenticated Cloud TTS")

    locale = os.environ.get("GOOGLE_TTS_LANGUAGE", "en-IN")
    voice = os.environ.get("GOOGLE_TTS_VOICE", "Despina")
    model = os.environ.get("GOOGLE_TTS_MODEL", "gemini-2.5-flash-tts")
    timeout = float(os.environ.get("GOOGLE_TTS_TIMEOUT_SECONDS", "90"))
    if not timeout > 0:
        raise ValueError("GOOGLE_TTS_TIMEOUT_SECONDS must be positive")
    client = texttospeech.TextToSpeechClient()
    paragraphs = [part.strip() for part in text.strip().split("\n\n") if part.strip()]
    segments = split_text(text)
    if len(segments) != len(paragraphs):
        raise ValueError("Timing requires one generated speech segment per narration paragraph")
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT_ROOT / output_name
    with tempfile.TemporaryDirectory(prefix="cafemesh-tts-") as temp_dir:
        temp = Path(temp_dir)
        segment_files: list[Path] = []
        timings: list[dict[str, float | int]] = []
        cursor = 0.0
        for index, segment in enumerate(segments):
            response = client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=segment, prompt=DEFAULT_PROMPT),
                voice=texttospeech.VoiceSelectionParams(
                    language_code=locale,
                    name=voice,
                    model_name=model,
                ),
                audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3),
                timeout=timeout,
            )
            if not response.audio_content:
                raise RuntimeError(f"Google TTS returned no audio for narration segment {index + 1}")
            segment_path = temp / f"segment-{index:02}.mp3"
            segment_path.write_bytes(response.audio_content)
            segment_files.append(segment_path)
            segment_duration = audio_duration(segment_path)
            timings.append({"scene": index, "start": cursor, "end": cursor + segment_duration, "duration": segment_duration})
            cursor += segment_duration

        concat_list = temp / "concat.txt"
        concat_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in segment_files) + "\n", encoding="utf-8")
        subprocess.run(
            [os.environ.get("FFMPEG", "ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
             "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c:a", "libmp3lame", "-q:a", "3", str(destination)],
            check=True,
        )
    if timing_name:
        if Path(timing_name).name != timing_name or not timing_name.endswith(".json"):
            raise ValueError("Timing manifest must be a JSON filename inside media/")
        total = audio_duration(destination)
        # Normalize source-segment timings to the final concatenated track duration.
        scale = total / cursor
        normalized = [{"scene": row["scene"], "start": row["start"] * scale,
                       "end": row["end"] * scale, "duration": row["duration"] * scale} for row in timings]
        manifest = {"audio": f"frontend/public/audio/{output_name}", "duration": total,
                    "locale": locale, "voice": voice, "model": model, "segments": normalized}
        (PROJECT_ROOT / "media" / timing_name).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(segments)} timed narration segments; locale={locale}, voice={voice}, model={model}")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 text file with narration")
    parser.add_argument("--output", default="cafemesh-product-walkthrough.mp3", help="MP3 filename under frontend/public/audio")
    parser.add_argument("--timing-output", help="Optional timing-manifest JSON filename under media/")
    args = parser.parse_args()
    print(synthesize(args.input.read_text(encoding="utf-8"), args.output, args.timing_output))
