# ComfyColab Image

ComfyColab Image is the optional image-generation and image-editing pack for
[ComfyColab](https://github.com/DragonLord1998/ComfyColab). It is intentionally
separate from the ComfyUI-on-Colab engine so image models, licenses, catalogs,
and optimizations can evolve on their own release cadence.

> Development staging status: the source, manifest, hooks, and offline contract
> suite are complete. The v1 manifest explicitly directs the generic core
> runtime to install `requirements.txt` from the pinned ComfyUI-GGUF checkout.
> A runtime-installable release still requires an immutable daughter commit in
> the official core registry, an exact generated lock, and a clean live Colab
> install, startup, and inference run against that lock.

The first modular release preserves the legacy internal node-root name
`custom_nodes/ComfyColab-ZImage` and all existing public node IDs:

- `ComfyColabZImageTurboBundleLoader`
- `ComfyColabQwenImageEdit2511BundleLoader`
- `ComfyColabKrea2BundleLoader`
- `ComfyColabFlux2Klein4BBundleLoader`
- `ComfyColabFlux2Klein9BBundleLoader`
- `ComfyColabFlux2DevBundleLoader`

Each node returns standard ComfyUI `MODEL`, `CLIP`, and `VAE` outputs.
Z-Image, Qwen Image Edit, and FLUX.2 use the manifest-declared, immutable
ComfyUI-GGUF dependency. Krea 2 uses ComfyUI's native FP8 loader.

The pack also adds exactly four direct Mage-Flow image nodes:

- `ComfyColabMageFlow`
- `ComfyColabMageFlowTurbo`
- `ComfyColabMageFlowEdit`
- `ComfyColabMageFlowEditTurbo`

They run revision-pinned Microsoft Mage-Flow models in an isolated persistent
worker and return a standard ComfyUI `IMAGE`. This personal-project integration
does not run prompt/image screening and does not expose a screening toggle. It
also removes Gaussian-Shading watermark generation; `seed` controls ordinary
deterministic Gaussian noise. No Base Mage-Flow nodes are registered. See
[`docs/mageflow.md`](docs/mageflow.md) for inputs and example workflows.

The pack also provides one NVIDIA PiD facade:

- `ComfyColabPiDUpscale`

It accepts any ComfyUI image, lets the user choose a matched FLUX.1, FLUX.2,
or Qwen Image VAE family, and returns a native 4x PiD upscale. Experimental
16x mode cascades two 4x passes and uses tiled VAE encoding plus overlapped
context-window sampling on the second pass. See
[`docs/pid-upscaler.md`](docs/pid-upscaler.md); the NVIDIA noncommercial model
license must be explicitly accepted in the node before assets are downloaded.

## Installation after publication

After an immutable daughter commit is added to the official core registry and
the resulting lock passes live validation, the supported installation path
will be:

```bash
comfycolab start --pack image
```

The resolver verifies `comfycolab-pack.json`, resolves the exact dependency
revisions, and links both Image node roots into ComfyUI. The pack does not need
to be installed as a Python dependency. During development, core
integration uses an explicit authenticated `--pack-ref` file rather than the
currently unpublished `image` alias.

## Models

All model assets are declared in checksum-pinned JSON catalogs under
`custom_nodes/ComfyColab-ZImage/catalog/`. Downloads are resumable and an asset
is published into the active ComfyUI model folder only after SHA-256
verification. See [the catalog guide](docs/model-catalog.md) and
[third-party notices](THIRD_PARTY_NOTICES.md) before use.

## Validation

```bash
PYTHON=python3 bash scripts/check.sh
python3 scripts/verify_catalogs.py
```

The first command is offline and verifies the manifest, hooks, node inventory,
catalog contracts, downloader behavior, and loader delegation. The second
command is an explicit network check of pinned Hugging Face sizes and hashes.
Neither command proves live GPU inference or output quality; that requires a
separate Colab smoke run.

Four Mage-Flow workflows and one PiD upscaler workflow are included under
`workflows/`. Local tests cover their graph contracts, but live GPU inference
remains a separate release gate.
