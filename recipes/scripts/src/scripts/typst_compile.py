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

# recipes/scripts/src/scripts/typst_compile.py
import argparse
import subprocess
import sys
from scripts.paths import find_project_root, resolve_piece_path

_INPUT_NAME = "cover.typ"
_OUTPUT_NAME = "cover.png"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse command line arguments for typst-compile.

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
            f"Compile composizioni/<piece-dir>/{_INPUT_NAME} to "
            f"{_OUTPUT_NAME}."
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


def compile_cover(piece_dir: str) -> None:
    """
    Run typst compile for one piece cover entry point.

    Parameters
    ----------
    piece_dir : str
        Directory name under composizioni/.

    Raises
    ------
    ValueError
        If piece_dir is not a bare directory name.
    FileNotFoundError
        If the project root, piece directory, or input Typst file is missing.
    RuntimeError
        If the Typst process exits with a non-zero status.
    """
    project_root = find_project_root()
    piece_path = resolve_piece_path(piece_dir, project_root=project_root)
    input_path = piece_path / _INPUT_NAME
    output_path = piece_path / _OUTPUT_NAME
    if not input_path.is_file():
        raise FileNotFoundError(f"{_INPUT_NAME} not found: {input_path}")

    result = subprocess.run(
        [
            "typst",
            "compile",
            "--root",
            str(project_root),
            str(input_path),
            str(output_path),
        ],
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"typst compile failed with exit code {result.returncode}"
        )


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point for typst-compile.

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
        compile_cover(args.piece_dir)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print("example: typst-compile Op-1_No-1_Believe", file=sys.stderr)
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
