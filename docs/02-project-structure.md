# II. Detailed Project Structure

> *This document describes the logical organization of the project codebase as a Pixi workspace for the video release pipeline.*

## Repository Layout

```
video-forge-opus-one/
├── composizioni/       # Musical workspaces for `Composizioni, Op. 1`.
│   │
│   ├── cover/                              # Shared Typst video cover library.
│   │
│   ├── Op-1_No-1_Believe/                  # No. 1: Believe (Piano).
│   ├── Op-1_No-2_Silence/                  # No. 2: Silence (Piano).
│   ├── Op-1_No-3_Abyss/                    # No. 3: Abyss (Piano, Harp, and Soprano).
│   ├── Op-1_No-4_Through_Pain/             # No. 4: Through Pain (Piano).
│   ├── Op-1_No-5_To-the-Beloved/           # No. 5: To the Beloved (Piano, Soprano, and Contralto).
│   ├── Op-1_No-6_Dreaming/                 # No. 6: Dreaming (Harp).
│   └── Op-1_No-7_Solitude-and-Loneliness/  # No. 7: Solitude and Loneliness (Piano).
│
├── recipes/            # Local conda packages built via `pixi-build` and
│   │                   # declared as workspace dependencies.
│   │
│   └── scripts/        # Video pipeline CLIs (pixi-build-python recipe).
│
├── metadata.toml       # Shared release metadata (used by workspace CLIs).
│
├── pixi.toml           # Workspace manifest: channels, dependencies, and tasks.
│
├── pixi.lock           # Fully resolved and reproducible dependency lockfile.
│
├── LICENSE-CC-BY-4.0   # Full text of the Creative Commons Attribution 4.0
│                       # International License.
│
├── LICENSE-APACHE-2.0  # Full text of the Apache License, Version 2.0.
│
└── NOTICE              # Preferred attribution when reusing Apache-2.0 licensed
                        # portions of this project, plus preserved
                        # NOTICE text from upstream works reused here.
```

Source files are documented with detailed docstrings and/or inline comments to explain the code.

## Workspace Overview

### 1. `composizioni/cover/`

Shared Typst library that produces the 16:9 video cover for every piece.

```
cover/
├── lib.typ             # Entry function: loads `metadata.toml`, sets page and document
│                       # properties, and composes the cover page.
│
└── 01-cover.typ        # Cover page layout (collection, number, title, instruments,
                        # author, publication date).
```

### 2. `composizioni/Op-1_No-*/`

One directory per piece under `composizioni/Op-1_No-*`. Every piece directory follows the same file layout, so only one example is shown below.

```
Op-1_No-1_Believe/
├── cover.typ           # Per-piece Typst entry; imports `../cover/lib.typ` and
│                       # supplies number, title, and instruments.
│
├── source.flac         # Release FLAC from audio-forge-opus-one (fetched).
│
├── cover.png           # Typst cover output.
│
├── video.mp4           # Still-image MP4 (H.264 + ALAC) from encode-mp4.
│
└── release.mp4         # video.mp4 with release MP4 tags.
```

> **Note:**  
> `*.flac`, `*.mp4`, and `cover.png` are gitignored. After a fresh clone only `cover.typ` is present until `fetch-release-flacs` and the video pipeline are run.

### 3. `recipes/scripts/`

Conda package recipe for the video pipeline CLIs. Exposes four CLI entry points consumed by the Pixi tasks in `pixi.toml`. Pulls `ffmpeg`, `mutagen`, and `typst` as run dependencies.

```
scripts/
├── pyproject.toml                      # Hatchling project definition and console script
│                                       # entry points.
│
├── pixi.toml                           # pixi-build-python recipe: host and run dependencies.
│
└── src/scripts/
    ├── paths.py                        # Project root resolution (PIXI_PROJECT_ROOT or
    │                                   # ancestor walk), piece path resolution, and
    │                                   # `metadata.toml` loading.
    │
    ├── fetch_release_flacs.py          # fetch-release-flacs CLI: downloads each local
    │                                   # piece's release FLAC from audio-forge-opus-one
    │                                   # as `source.flac`.
    │
    ├── typst_compile.py                # typst-compile CLI: compiles
    │                                   # `composizioni/<piece-dir>/cover.typ` to
    │                                   # `cover.png`.
    │
    ├── encode_mp4.py                   # encode-mp4 CLI: encodes `cover.png` and
    │                                   # `source.flac` into `video.mp4`
    │                                   # (H.264 + ALAC).
    │
    └── write_mp4_metadata.py           # write-mp4-metadata CLI: copies `video.mp4` to
                                        # `release.mp4` with tags from `metadata.toml`
                                        # and embedded `cover.png`.
```

Piece-oriented CLIs accept a bare directory name (for example `Op-1_No-1_Believe`) and resolve paths relative to the workspace root. They expect the fixed file names from the piece layout above — `cover.typ`, `source.flac`, `cover.png`, `video.mp4`, and `release.mp4` — and will fail if those names are missing or renamed. They share `paths.py` for consistent project-root discovery and `metadata.toml` access.
