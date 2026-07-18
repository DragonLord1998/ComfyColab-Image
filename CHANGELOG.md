# Changelog

All notable changes to ComfyColab Image are recorded here.

This project follows semantic versioning. Development versions are staging
artifacts and are not runtime-installable releases unless the release entry says
otherwise.

## Unreleased

### Required before the first runtime-installable release

- Resolve the pinned ComfyUI-GGUF checkout's Python requirements into the
  manifest's main `environments` declaration.
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

- The pack manifest does not yet declare normalized main-environment Python
  requirements from the pinned ComfyUI-GGUF checkout. ComfyColab must not infer
  or install an undeclared upstream `requirements.txt`; this development version
  is therefore not a runtime-installable release.
- Local validation does not prove live GPU inference, memory fit, runtime, or
  output quality in Colab.
