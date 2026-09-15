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

# recipes/scripts/src/scripts/write_mp4_metadata.py
import argparse
import shutil
import sys
from pathlib import Path
from typing import Any
from mutagen.mp4 import MP4, MP4Cover
from scripts.paths import find_project_root, load_metadata, resolve_piece_path

_SOURCE_NAME = "video.mp4"
_RELEASE_NAME = "release.mp4"
_COVER_NAME = "cover.png"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command line arguments for write-mp4-metadata.

    Parameters
    ----------
    argv : list of str or None, optional
        Argument vector to parse. If None, sys.argv is used. Default is None.

    Returns
    -------
    argparse.Namespace
        Parsed arguments containing piece_dir and title.
    """
    parser = argparse.ArgumentParser(
        description=(
            f"Tag composizioni/<piece-dir>/{_SOURCE_NAME} and write "
            f"{_RELEASE_NAME} via mutagen. Release fields other than title "
            "are read from metadata.toml. Cover art is embedded from "
            f"{_COVER_NAME}."
        ),
    )
    parser.add_argument(
        "piece_dir",
        help=(
            "Directory name under composizioni/, "
            "e.g. Op-1_No-1_Believe."
        ),
    )
    parser.add_argument(
        "title",
        help='Track title, e.g. "No. 1: Believe".',
    )
    return parser.parse_args(argv)


def _require_str(meta: dict[str, Any], keys: tuple[str, ...]) -> str:
    """
    Read a nested string field from parsed metadata.toml.

    Parameters
    ----------
    meta : dict of str to Any
        Parsed TOML document.
    keys : tuple of str
        Nested key path, for example ("author", "display_name").

    Returns
    -------
    str
        Field value.

    Raises
    ------
    ValueError
        If any key along the path is missing or the leaf is not a string.
    """
    current: Any = meta
    path = ".".join(keys)
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"metadata.toml missing required field: {path}")
        current = current[key]

    if not isinstance(current, str):
        raise ValueError(f"metadata.toml field must be a string: {path}")
    return current


def _require_int(meta: dict[str, Any], keys: tuple[str, ...]) -> int:
    """
    Read a nested integer field from parsed metadata.toml.

    Parameters
    ----------
    meta : dict of str to Any
        Parsed TOML document.
    keys : tuple of str
        Nested key path, for example ("date", "year").

    Returns
    -------
    int
        Field value.

    Raises
    ------
    ValueError
        If any key along the path is missing or the leaf is not an integer.
    """
    current: Any = meta
    path = ".".join(keys)
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"metadata.toml missing required field: {path}")
        current = current[key]

    if not isinstance(current, int):
        raise ValueError(f"metadata.toml field must be an integer: {path}")
    return current


def _format_date(meta: dict[str, Any]) -> str:
    """
    Build an ISO date string from metadata.toml [date] for the MP4 date tag.

    Parameters
    ----------
    meta : dict of str to Any
        Parsed TOML document.

    Returns
    -------
    str
        Date in YYYY-MM-DD form.

    Raises
    ------
    ValueError
        If year, month, or day is missing or out of range.
    """
    year = _require_int(meta, ("date", "year"))
    month = _require_int(meta, ("date", "month"))
    day = _require_int(meta, ("date", "day"))

    if not 1 <= month <= 12:
        raise ValueError(f"metadata.toml date.month out of range: {month}")
    if not 1 <= day <= 31:
        raise ValueError(f"metadata.toml date.day out of range: {day}")

    return f"{year:04d}-{month:02d}-{day:02d}"


def write_release_mp4(piece_dir: str, title: str) -> Path:
    """
    Copy the encoded MP4 into the release MP4 with iTunes-style tags.

    Existing tags are cleared. Title comes from the CLI argument; artist,
    album, date, and copyright are taken from metadata.toml. Cover art is
    embedded from cover.png in the piece directory.

    Parameters
    ----------
    piece_dir : str
        Directory name under composizioni/.
    title : str
        Value for the title tag.

    Returns
    -------
    Path
        Absolute path of the written release MP4.

    Raises
    ------
    ValueError
        If piece_dir is not a bare directory name, or required metadata keys
        are missing.
    FileNotFoundError
        If the project root, piece directory, source MP4, cover.png, or
        metadata.toml is missing.
    RuntimeError
        If mutagen cannot open or save the MP4 file.
    """
    project_root = find_project_root()
    piece_path = resolve_piece_path(piece_dir, project_root=project_root)
    source_path = piece_path / _SOURCE_NAME
    release_path = piece_path / _RELEASE_NAME
    cover_path = piece_path / _COVER_NAME

    if not source_path.is_file():
        raise FileNotFoundError(f"{_SOURCE_NAME} not found: {source_path}")
    if not cover_path.is_file():
        raise FileNotFoundError(f"{_COVER_NAME} not found: {cover_path}")

    meta = load_metadata(project_root)
    artist = _require_str(meta, ("author", "display_name"))
    album = _require_str(meta, ("work", "collection"))
    date = _format_date(meta)
    copyright_notice = _require_str(meta, ("license", "notice"))
    cover_bytes = cover_path.read_bytes()

    if release_path.exists():
        release_path.unlink()
    shutil.copy2(source_path, release_path)

    media = MP4(release_path)
    media.clear()
    media["\xa9nam"] = [title]
    media["\xa9ART"] = [artist]
    media["\xa9alb"] = [album]
    media["\xa9day"] = [date]
    media["\xa9cpr"] = [copyright_notice]
    media["covr"] = [MP4Cover(cover_bytes, imageformat=MP4Cover.FORMAT_PNG)]
    try:
        media.save()
    except Exception as exc:
        raise RuntimeError(f"failed to save MP4 tags: {release_path}") from exc

    return release_path


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for write-mp4-metadata.

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
        write_release_mp4(args.piece_dir, args.title)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            'example: write-mp4-metadata Op-1_No-1_Believe "No. 1: Believe"',
            file=sys.stderr,
        )
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
