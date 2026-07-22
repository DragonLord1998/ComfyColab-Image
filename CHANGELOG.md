# Changelog

All notable changes to ComfyColab Image are recorded here.

This project follows semantic versioning. Development versions are staging
artifacts and are not runtime-installable releases unless the release entry says
otherwise.

## Unreleased

### Added

- Added four Mage-Flow generation/editing facades and revision-pinned upstream
  source/model declarations.
- Added example workflows and an isolated persistent inference worker.
- Removed upstream prompt/image screening and Gaussian-Shading watermarking
  from this personal-project integration; generation uses seeded Gaussian noise.

### Changed

- Declared the pinned ComfyUI-GGUF checkout's own `requirements.txt` for
  dependency-owned installation by the generic core runtime.

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
