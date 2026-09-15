# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# recipes/scripts/src/scripts/encode_mp4.py
import argparse
import subprocess
import sys
from pathlib import Path
from scripts.paths import find_project_root, resolve_piece_path

_COVER_NAME = "cover.png"
_SOURCE_NAME = "source.flac"
_OUTPUT_NAME = "video.mp4"
_FRAME_RATE = 1


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command line arguments for encode-mp4.

    Parameters
    ----------
    argv : list of str or None, optional
        Argument vector to parse. If None, sys.argv is used. Default is None.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing piece_dir.
    """
    parser = argparse.ArgumentParser(
        description=(
            f"Encode composizioni/<piece-dir>/{_COVER_NAME} and "
            f"{_SOURCE_NAME} into {_OUTPUT_NAME}. Video is a still image "
            "(H.264); audio is remuxed as Apple Lossless (ALAC)."
        ),
    )
    parser.add_argument(
        "piece_dir",
        help=(
            "Directory name under composizioni/, "
            "e.g. Op-1_No-1_Believe."
        ),
    )
    return parser.parse_args(argv)


def _audio_duration_seconds(audio_path: Path) -> float:
    """
    Read the duration of an audio file with ffprobe.

    Parameters
    ----------
    audio_path : Path
        Absolute path to the input audio.

    Returns
    -------
    float
        Duration in seconds.

    Raises
    ------
    RuntimeError
        If ffprobe fails or the duration is missing / not numeric.
    """
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(
            f"ffprobe duration failed for {audio_path}{suffix}"
        )

    raw = completed.stdout.strip()
    try:
        duration = float(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"ffprobe returned a non-numeric duration for {audio_path}: {raw}"
        ) from exc
    if not duration > 0.0:
        raise RuntimeError(
            f"ffprobe returned a non-positive duration for {audio_path}: {raw}"
        )
    return duration


def _run_ffmpeg(
    cover_path: Path,
    audio_path: Path,
    output_path: Path,
) -> None:
    """
    Build a still-image MP4 with lossless ALAC audio via ffmpeg.

    Output length is capped to the FLAC duration from ffprobe (a looped still
    image must not be left to determine container length via -shortest).

    Parameters
    ----------
    cover_path : Path
        Absolute path to the static cover image.
    audio_path : Path
        Absolute path to the input FLAC.
    output_path : Path
        Absolute path for the written MP4.

    Raises
    ------
    RuntimeError
        If ffprobe or ffmpeg fails.
    """
    duration = _audio_duration_seconds(audio_path)
    completed = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-nostats",
            "-loglevel",
            "error",
            "-loop",
            "1",
            "-framerate",
            str(_FRAME_RATE),
            "-i",
            str(cover_path),
            "-i",
            str(audio_path),
            "-t",
            f"{duration:.6f}",
            "-c:v",
            "libx264",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-vf",
            "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:a",
            "alac",
            "-movflags",
            "+faststart",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(
            f"ffmpeg encode failed for {audio_path}{suffix}"
        )


def encode_mp4(piece_dir: str) -> Path:
    """
    Encode one piece's cover image and source FLAC into a still-image MP4.

    Parameters
    ----------
    piece_dir : str
        Directory name under composizioni/.

    Returns
    -------
    Path
        Absolute path of the written video MP4.

    Raises
    ------
    ValueError
        If piece_dir is not a bare directory name.
    FileNotFoundError
        If the project root, piece directory, cover.png, or source FLAC is
        missing.
    RuntimeError
        If ffprobe or ffmpeg fails.
    """
    project_root = find_project_root()
    piece_path = resolve_piece_path(piece_dir, project_root=project_root)
    cover_path = piece_path / _COVER_NAME
    source_path = piece_path / _SOURCE_NAME
    output_path = piece_path / _OUTPUT_NAME

    if not cover_path.is_file():
        raise FileNotFoundError(f"{_COVER_NAME} not found: {cover_path}")
    if not source_path.is_file():
        raise FileNotFoundError(f"{_SOURCE_NAME} not found: {source_path}")

    _run_ffmpeg(cover_path, source_path, output_path)
    return output_path


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for encode-mp4.

    Parameters
    ----------
    argv : list of str or None, optional
        Argument vector to parse. If None, sys.argv is used. Default is None.

    Returns
    -------
    int
        Process exit code. Zero on success, one on failure.
    """
    args = _parse_args(argv)
    try:
        encode_mp4(args.piece_dir)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print("example: encode-mp4 Op-1_No-1_Believe", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
