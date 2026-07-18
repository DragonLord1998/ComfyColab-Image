# ComfyColab Image

ComfyColab Image is the optional image-generation and image-editing pack for
[ComfyColab](https://github.com/DragonLord1998/ComfyColab). It is intentionally
separate from the ComfyUI-on-Colab engine so image models, licenses, catalogs,
and optimizations can evolve on their own release cadence.

> Development staging status: the source, manifest, hooks, and offline contract
> suite are complete, but the v1 manifest does not yet contain normalized
> main-environment Python requirements from the pinned ComfyUI-GGUF checkout.
> Core correctly refuses to auto-discover an undeclared `requirements.txt`.
> Add those resolved requirements to `environments` before publishing a
> runtime-installable release.

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

## Installation after publication

After the normalized requirements blocker above is resolved and an immutable
daughter commit is added to the official core registry, the supported
installation path will be:

```bash
comfycolab start --pack image
```

The resolver verifies `comfycolab-pack.json`, resolves the exact dependency
revision, and links `custom_nodes/ComfyColab-ZImage` into ComfyUI. The pack does
not need to be installed as a Python dependency. During development, core
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

No image example workflow existed at the extraction baseline. The loader
contracts remain covered by parameterized tests until representative workflows
are added without changing the preserved node APIs.
