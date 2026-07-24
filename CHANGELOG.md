# Changelog

All notable changes to ComfyColab Image are recorded here.

This project follows semantic versioning. Development versions are staging
artifacts and are not runtime-installable releases unless the release entry says
otherwise.

## Unreleased

- Increased the isolated Mage worker startup allowance so first-run Hugging
  Face snapshot downloads do not fail at the old three-minute readiness limit.
- Replaced one-dimensional context-window slicing in experimental PiD 16x with
  PiD's native Chroma Radiance NeRF-head tiling and a standard second-pass VAE
  encode, eliminating severe grid/seam corruption from both incompatible
  context slicing and the PixelDiT VAE's tiled encoder.
- Added a 256x256 minimum for experimental 16x after live visual QA showed that
  smaller sources compound generative artifacts across the two PiD passes.

### Added

- Added a repository-root ComfyUI V3 entrypoint so the whole repository can be
  cloned directly into `ComfyUI/custom_nodes/ComfyColab-Image`.
- Added a Manager-compatible installer, explicit node inventory, worker-only
  Mage dependency target, and standalone health checks.
- Added four Mage-Flow generation/editing facades and revision-pinned upstream
  source/model declarations.
- Added example workflows and an isolated persistent inference worker.
- Removed upstream prompt/image screening and Gaussian-Shading watermarking
  from this personal-project integration; generation uses seeded Gaussian noise.

### Changed

- PiD now reports a stock-ComfyUI update instruction when PixelDiT support is
  missing instead of assuming the ComfyColab launcher.
- Mage worker process cleanup supports Windows as well as POSIX process groups.
- Declared the pinned ComfyUI-GGUF checkout's own `requirements.txt` for
  dependency-owned installation by the generic core runtime.
- Standalone installation now refuses an incompatible existing ComfyUI-GGUF
  checkout and verifies every isolated Mage worker package before reporting
  readiness.

### Validation

- Discovered all 12 public nodes on stock ComfyUI 0.28.0 and completed live G4
  Mage generation/editing plus PiD 4x and experimental native-tiled 16x runs.

### Required before the first runtime-installable release

- Publish an immutable daughter commit and add it to the official core registry.
- Generate an exact ComfyColab lock and complete a live Colab smoke run against
  that lock.
- Record accelerator, peak-memory, startup, inference, and representative
  output evidence separately from local test results.

## 0.1.0-dev1 - 2026-07-18

### Added

- Extracted the legacy `ComfyColab-ZImage` node root into an independent Image
  pack while preserving its six public node IDs.
- Added immutable ComfyUI-GGUF and model-catalog pins, checksum-verified model
  downloads, offline hooks, health checks, and pack probes.
- Added local manifest, catalog, downloader, loader-delegation, and node-loading
  tests.

### Known limitations

- Local validation does not prove live GPU inference, memory fit, runtime, or
  output quality in Colab.
