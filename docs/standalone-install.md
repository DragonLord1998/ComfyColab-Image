# Standalone ComfyUI installation

Clone this repository as one directory directly under `ComfyUI/custom_nodes`
and run its installer with the same Python executable that launches ComfyUI.
The checkout directory name is not significant; the root entrypoint resolves
its internal node packages by file path.

## Installation contract

`install.py` performs installation-time provisioning only:

- Microsoft Mage source is downloaded at
  `1c4727a6daea1200488d9c68544ebea2e784c765` and checked against the archive
  SHA-256 recorded in the installer.
- Mage's incompatible packages are installed under
  `.standalone/mage/python-packages`. They are added only to the Mage worker
  process and never replace packages in ComfyUI's Python environment.
- The pinned ComfyUI-GGUF checkout is installed beside this repository only
  when no installation already exists. An existing exact-pinned checkout is
  reused; a different or non-git installation produces an actionable error
  instead of reporting a misleading successful install.
- Model weights are not downloaded until the corresponding node executes.

Run a read-only health check with:

```bash
python install.py --check
python runtime/doctor.py
```

## ComfyUI compatibility

The standalone custom node targets current ComfyUI with the V3 extension API.
NVIDIA PiD additionally requires the native PixelDiT/PiD nodes included in
current ComfyUI. If the PiD node reports missing upstream node IDs, update
ComfyUI and restart. The standalone installer deliberately does not patch
another user's ComfyUI checkout.

The managed ComfyColab runtime can continue using its content-addressed PiD
compatibility patch for its older pinned ComfyUI revision.

## Platform support

- Linux with NVIDIA CUDA is the fully validated inference target.
- Windows supports custom-node discovery and Mage worker process lifecycle.
  Full model inference still requires a compatible CUDA/PyTorch installation.
- macOS and CPU systems can load the nodes, but the bundled Mage and PiD models
  are not claimed to be practical inference targets there.

## Troubleshooting

If Mage reports that standalone dependencies are missing, rerun `install.py`
with the ComfyUI Python executable and restart ComfyUI.

If a Z-Image or FLUX loader reports that `UnetLoaderGGUF` is missing, install or
update ComfyUI-GGUF to the audited revision and restart. The installer never
overwrites an existing GGUF checkout and refuses incompatible revisions.

If PiD reports missing PixelDiT node IDs, update ComfyUI. Do not copy the
managed ComfyColab core patch into an unrelated checkout.
