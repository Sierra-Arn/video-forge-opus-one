# Video Forge for Opus One

*A Pixi workspace for building publication-ready video files of «Sierra Arn — Composizioni, Op. 1» from release FLAC audio.*

## Project Structure at a Glance

```
video-forge-opus-one/
├── composizioni/       # Musical workspaces for `Composizioni, Op. 1`.
│                       # Each `Op-1_No-*/` subdirectory represents one musical
│                       # piece; `cover/` is the shared Typst cover library.
│
├── recipes/            # Local conda packages built via `pixi-build` and
│                       # declared as workspace dependencies. Each subdirectory
│                       # represents one local conda package recipe.
│
├── docs/               # Technical documentation covering workspace dependencies,
│                       # and detailed project structure.
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

## Quick Start

### I. Prerequisites

- [Pixi](https://pixi.sh/latest/) package manager.
- GNU/Linux-based system on `x86_64` architecture.

> **Note:**  
> These prerequisites are not strict requirements but describe the environment used for development. The project can be set up in alternative environments with different package managers, or operating systems if needed.

### II. Setup

1. **Clone the repository**

    ```bash
    git clone git@github.com:Sierra-Arn/video-forge-opus-one.git
    cd video-forge-opus-one
    ```

2. **Install dependencies**

    ```bash
    pixi install
    ```

3. **Fetch release FLAC audio from [audio-forge-opus-one](https://github.com/Sierra-Arn/audio-forge-opus-one/releases/tag/v2026.09.15)**

    ```bash
    pixi run fetch-release-flacs
    ```

### III. Build

With the environment activated and `source.flac` in place for each piece, publication-ready video files can be rebuilt in the following steps:

1. **Compile Typst covers for every piece into `cover.png`**

    ```bash
    pixi run typst-compile-all
    ```

2. **Encode still-image MP4 from `cover.png` and `source.flac` into `video.mp4` for every piece**

    ```bash
    pixi run encode-mp4-all
    ```

3. **Create `release.mp4` from `video.mp4` with release metadata for every piece**

    ```bash
    pixi run release-all
    ```

> **Want to see what happens under the hood?**  
> The Pixi tasks that drive this pipeline are defined here:
> - [Workspace tasks](./pixi.toml)
>
> Those tasks invoke the video pipeline CLIs. Every file is fully documented with detailed docstrings:
> - [Pipeline CLIs](./recipes/scripts/src/scripts/)

## License

Every file in this project is licensed under the [Apache License, Version 2.0](LICENSE-APACHE-2.0).

The FLAC audio sources (`.flac`) are obtained from [audio-forge-opus-one](https://github.com/Sierra-Arn/audio-forge-opus-one) and are licensed under the [Creative Commons Attribution 4.0 International License](LICENSE-CC-BY-4.0).

All files generated from the `.flac` files, all files produced by compiling Typst code, and all files further derived from those outputs — including video produced in this workspace — are also licensed under the [Creative Commons Attribution 4.0 International License](LICENSE-CC-BY-4.0).
