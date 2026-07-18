# Third-party notices

ComfyColab Image downloads and connects third-party projects at runtime. It
does not store model weights in this repository. Upstream license files and
model-card terms control; review them before redistribution, commercial use,
or hosted-service deployment.

## ComfyUI-GGUF

- Source: <https://github.com/city96/ComfyUI-GGUF>
- Pinned revision: `6ea2651e7df66d7585f6ffee804b20e92fb38b8a`
- Declared source license: Apache-2.0

## Z-Image Turbo

- Community GGUF repository: <https://huggingface.co/jayn7/Z-Image-Turbo-GGUF>
- Text encoder: <https://huggingface.co/unsloth/Qwen3-4B-GGUF>
- VAE: <https://huggingface.co/Comfy-Org/z_image_turbo>

The GGUF files are community conversions. Their source-model and text-encoder
terms remain applicable.

## Qwen Image Edit 2511

- Community GGUF repository: <https://huggingface.co/unsloth/Qwen-Image-Edit-2511-GGUF>
- ComfyUI encoder and VAE assets: <https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI>

Qwen model terms and the terms declared by the conversion repositories remain
applicable.

## Krea 2

- Model, encoder, and VAE assets: <https://huggingface.co/Comfy-Org/Krea-2>

Krea 2 has upstream community-license terms. The catalog includes both the
Turbo inference model and the raw training/base artifact; selecting the latter
does not make it the recommended inference configuration.

## FLUX.2 Klein and FLUX.2 Dev

- Klein 4B GGUF: <https://huggingface.co/unsloth/FLUX.2-klein-4B-GGUF>
- Klein 9B GGUF: <https://huggingface.co/unsloth/FLUX.2-klein-9B-GGUF>
- Dev GGUF: <https://huggingface.co/city96/FLUX.2-dev-gguf>
- ComfyUI companion assets: <https://huggingface.co/Comfy-Org/flux2-dev>

The current catalogs declare Klein 4B as Apache-2.0 and Klein 9B plus Dev as
subject to the FLUX Non-Commercial License. Community conversions remain
derivative artifacts and do not replace the source-model terms.

Every artifact URL, revision, size, and SHA-256 used by the pack is recorded in
the corresponding JSON catalog.
