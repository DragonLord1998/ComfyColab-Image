# ComfyColab Image

ComfyColab Image is a standalone ComfyUI custom-node pack for image generation,
editing, Mage-Flow, and NVIDIA PiD upscaling. It can be cloned directly into a
normal ComfyUI installation; the managed
[ComfyColab](https://github.com/DragonLord1998/ComfyColab) runtime remains an
additional supported installation path.

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
worker and return `IMAGE`, `MODEL`, `CLIP`, and `VAE`. Connect the component
outputs to `CLIP Text Encode`, a sampler of your choice, and `VAE Decode`; use
the included 128-channel, 16x Mage empty latent node for text-to-image. Edit
models retain their connected source image as sampler reference conditioning,
and the exported VAE preserves batches and supports tiled encode/decode.
This personal-project integration
does not run prompt/image screening and does not expose a screening toggle. It
also removes Gaussian-Shading watermark generation; `seed` controls ordinary
deterministic Gaussian noise. No Base Mage-Flow nodes are registered. See
[`docs/mageflow.md`](docs/mageflow.md) for inputs and example workflows.

The pack also provides one NVIDIA PiD facade:

- `ComfyColabPiDUpscale`

It accepts any ComfyUI image and exposes tiled `2x`, `4x`, `8x`, and `16x`
upscaling. FLUX.2 is the default PiD VAE; matched FLUX.1 and Qwen Image options
and an experimental Mage-VAE bridge are also available. PiD runs on bounded,
overlapping source tiles and returns the raw merged PiD result; the former
Z-Image Turbo touch-up pass is disabled. An optional, default-enabled Qwen3.8
vision step inspects the source with thinking and writes the detailed prompt
before PiD loads. The exact prompt used is exposed as a second output. This
integration requires the current ComfyColab Video pack alongside Image. The
former 4096/8192-pixel facade caps are removed; the pinned ComfyUI
tile merger supports a final canvas up to 32768 px per side. See
[`docs/pid-upscaler.md`](docs/pid-upscaler.md); the NVIDIA noncommercial model
license must be explicitly accepted in the node before assets are downloaded.

## Standalone installation

### ComfyUI Manager

Install `ComfyColab-Image` from its Git URL. Manager clones the repository,
runs the lightweight shared requirements step, and then runs `install.py`.
Restart ComfyUI after installation.

### Manual

From the ComfyUI directory:

```bash
cd custom_nodes
git clone https://github.com/DragonLord1998/ComfyColab-Image.git
cd ComfyColab-Image
python install.py
```

Use the same Python executable that starts ComfyUI. Portable Windows users
should run the embedded Python executable instead of a system Python. Restart
ComfyUI after the installer completes.

The installer:

- keeps Mage's `transformers`, `diffusers`, `accelerate`, and `loguru` versions
  in a private worker-only target;
- downloads the exact Microsoft Mage source archive and verifies its SHA-256;
- installs the pinned ComfyUI-GGUF dependency as a sibling custom node when it
  is not already present;
- never downloads model weights during installation.

Mage and PiD model weights remain lazy, checksum/revision-pinned downloads.
PiD requires current ComfyUI PixelDiT support. Older stock ComfyUI installations
must be updated; the standalone installer does not modify ComfyUI source files.
See [`docs/standalone-install.md`](docs/standalone-install.md) for diagnostics
and platform boundaries.

## Managed ComfyColab installation

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
`workflows/`. Local tests cover their graph contracts; standalone GPU inference
is validated separately on a clean stock-ComfyUI runtime.
