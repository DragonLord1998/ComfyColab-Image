# Contributing to ComfyColab Image

ComfyColab Image owns image-generation and image-editing nodes, model catalogs,
workflows, licenses, and image-specific optimizations. Changes to the generic
ComfyUI-on-Colab installer or pack resolver belong in the ComfyColab core
repository.

## Development contract

- Preserve public node IDs unless a documented breaking release intentionally
  changes them.
- Keep every Git dependency on an immutable 40-character commit.
- Keep downloadable model assets on immutable revisions with expected byte
  sizes and SHA-256 checksums.
- Declare dependencies and Python or system requirements in
  `comfycolab-pack.json`. Runtime code must not discover or install undeclared
  upstream requirements.
- Keep bootstrap hooks offline (`network: "none"`) and within their declared
  write roots.
- Update `THIRD_PARTY_NOTICES.md` whenever code, model, or data licensing
  changes.
- Keep the version in `comfycolab-pack.json` equal to `[project].version` in
  `pyproject.toml`.

## Local validation

Run the offline suite from this repository's root:

```bash
PYTHON=python3 bash scripts/check.sh
```

This validates Python syntax, the manifest and hook contracts, public node
inventory, catalogs, downloader behavior, and loader delegation. It does not
load CUDA models and does not establish that the pack is installable by the
ComfyColab runtime.

The catalog metadata verifier is a separate, networked check:

```bash
python3 scripts/verify_catalogs.py
```

Record its result separately from the offline suite because remote metadata can
change or become unavailable.

## Live validation

A release candidate needs a bounded Colab run using the exact generated lock,
not a mutable branch or an ad hoc install. Record at least:

- core, ComfyUI, pack, and dependency commits plus the lock SHA-256;
- accelerator and Python/CUDA environment;
- clean install and ComfyUI startup results;
- every declared Image node present in `/object_info`;
- one representative inference for each materially different loader path;
- peak memory, wall-clock time, output dimensions, and artifact checks;
- any skipped path and the reason it remains unproven.

Local green tests and a live Colab run are different evidence tiers. Do not
describe local checks as live-runtime proof.

## Current release blocker

`0.1.0-dev1` now declares the pinned ComfyUI-GGUF checkout's
`requirements.txt` on its Git dependency, so the generic core runtime owns that
installation. Before publishing a runtime-installable version, publish and
register an immutable daughter commit, generate a new lock, and run the live
validation above. Do not add a second imperative `pip install -r` path to a hook
or node.

## Pull-request checklist

- Manifest and `pyproject.toml` versions agree.
- New dependencies, assets, and licenses are immutable and documented.
- `PYTHON=python3 bash scripts/check.sh` passes.
- Network verification is reported separately when run.
- Live Colab evidence is attached for runtime-affecting changes, or the missing
  live gate is stated explicitly.
- `CHANGELOG.md` records user-visible behavior and remaining limitations.
