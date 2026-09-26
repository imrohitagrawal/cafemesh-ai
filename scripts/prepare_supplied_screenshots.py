"""Prepare user-supplied CaféMesh screen captures as narration-mapped video stills.

The screenshots are read from the owner's Desktop/Downloads and are never
copied into the repository in their unredacted form. FFmpeg crops them for
the relevant narration scene and masks visible account details in-frame.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "provided-app-screenshots"

SOURCES = {
    "permission": Path("/Users/rohitagrawal/Desktop/Screenshot 2026-09-26 at 6.47.08\u202fPM.png"),
    "account_chooser": Path("/Users/rohitagrawal/Desktop/Screenshot 2026-09-26 at 6.44.51\u202fPM.png"),
    "sign_in_form": Path("/Users/rohitagrawal/Desktop/Screenshot 2026-09-26 at 6.42.26\u202fPM.png"),
    "vision": Path("/Users/rohitagrawal/Downloads/screencapture-cafemesh-stackclimb-2026-09-26-18_49_27.png"),
    "owner": Path("/Users/rohitagrawal/Downloads/screencapture-cafemesh-stackclimb-2026-09-26-18_49_13.png"),
    "operations": Path("/Users/rohitagrawal/Downloads/screencapture-cafemesh-stackclimb-2026-09-26-18_48_56.png"),
    "customer_results": Path("/Users/rohitagrawal/Downloads/screencapture-cafemesh-stackclimb-2026-09-26-18_45_47.png"),
    "customer_discovery": Path("/Users/rohitagrawal/Downloads/screencapture-cafemesh-stackclimb-2026-09-26-18_45_20.png"),
}


@dataclass(frozen=True)
class Frame:
    source: str
    crop: tuple[int, int, int, int] | None = None  # x, y, width, height
    masks: tuple[str, ...] = ()  # FFmpeg drawbox arguments after 1280x720 fit


def crop_fill(crop: tuple[int, int, int, int]) -> str:
    x, y, width, height = crop
    return f"crop={width}:{height}:{x}:{y},scale=1280:720:flags=lanczos,setsar=1"


def full_fit() -> str:
    return (
        "scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,"
        "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=0xf4f1ea,setsar=1"
    )


def write_frame(frame: Frame, target: Path) -> None:
    src = SOURCES[frame.source]
    if not src.is_file():
        raise FileNotFoundError(f"Required user-provided screenshot is missing: {src}")
    vf = crop_fill(frame.crop) if frame.crop else full_fit()
    for mask in frame.masks:
        vf += f",drawbox={mask}"
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
         "-vf", vf, "-frames:v", "1", "-update", "1", str(target)],
        check=True,
    )


def frame(source: str, crop: tuple[int, int, int, int] | None = None, *masks: str) -> Frame:
    return Frame(source, crop, tuple(masks))


# Crops use the main application area where a long full-page capture would be
# too small to read. Every user-supplied screenshot appears in the two-video set.
HEADER_MASK = "x=0:y=0:w=1280:h=42:color=0xf4f1ea:t=fill"
ALERT_MASK = "x=0:y=214:w=1280:h=48:color=0xf4f1ea:t=fill"
ACCOUNT_MASK = "x=520:y=326:w=255:h=64:color=white:t=fill"
PERMISSION_MASKS = (
    "x=1025:y=58:w=220:h=30:color=white:t=fill",
    "x=392:y=232:w=888:h=43:color=0xf4f1ea:t=fill",
)

P = [
    frame("vision", (480, 0, 2400, 1350), HEADER_MASK, ALERT_MASK),
    frame("customer_discovery", (480, 400, 2400, 1350), "x=0:y=0:w=1280:h=76:color=0xf4f1ea:t=fill"),
    frame("permission", None, *PERMISSION_MASKS),
    frame("customer_results", (480, 1550, 2400, 1350)),
    frame("customer_results", (480, 2900, 2400, 1350)),
    frame("operations", (480, 3400, 2400, 1350)),
    frame("operations", (480, 0, 2400, 1350), HEADER_MASK, ALERT_MASK),
    frame("owner", (400, 0, 2480, 1395), HEADER_MASK, "x=0:y=205:w=1280:h=48:color=0xf4f1ea:t=fill"),
    frame("operations", (480, 1250, 2400, 1350)),
    frame("account_chooser", None, ACCOUNT_MASK),
    frame("vision", (480, 1450, 2400, 1350)),
    frame("customer_discovery", (480, 400, 2400, 1350), "x=0:y=0:w=1280:h=76:color=0xf4f1ea:t=fill"),
]

E = [
    frame("customer_results", (480, 1550, 2400, 1350)),
    frame("vision", (480, 0, 2400, 1350), HEADER_MASK, ALERT_MASK),
    frame("operations", (480, 1250, 2400, 1350)),
    frame("customer_results", (480, 1550, 2400, 1350)),
    frame("customer_results", (480, 2900, 2400, 1350)),
    frame("operations", (480, 1250, 2400, 1350)),
    frame("operations", (480, 3400, 2400, 1350)),
    frame("permission", None, *PERMISSION_MASKS),
    frame("operations", (480, 0, 2400, 1350), HEADER_MASK, ALERT_MASK),
    frame("owner", (400, 0, 2480, 1395), HEADER_MASK, "x=0:y=205:w=1280:h=48:color=0xf4f1ea:t=fill"),
    frame("sign_in_form"),
    frame("operations", (480, 2350, 2400, 1350)),
    frame("operations", (480, 1250, 2400, 1350)),
    frame("vision", (480, 1450, 2400, 1350)),
]


def main() -> None:
    specs = {"product": P, "engineering": E}
    for kind, frames in specs.items():
        expected = 12 if kind == "product" else 14
        if len(frames) != expected:
            raise ValueError(f"{kind}: expected {expected} screenshot scenes, got {len(frames)}")
        folder = OUT / kind
        folder.mkdir(parents=True, exist_ok=True)
        for index, item in enumerate(frames):
            write_frame(item, folder / f"scene-{index:02}.png")
        print(f"{kind}: prepared {len(frames)} redacted user-supplied app screenshot scenes")


if __name__ == "__main__":
    main()
