# ComfyColab PiD

`ComfyColab PiD — Image Upscaler` is one public ComfyUI facade over the native
PiD/PixelDiT nodes in ComfyColab's pinned ComfyUI build.

- 2x/4x: one tiled native 4x PiD pass, reduced to 2x when selected.
- 8x/16x: two tiled native 4x PiD passes, reduced to 8x when selected.
- Every scale returns the raw overlapped PiD tile merge. The former Z-Image
  Turbo touch-up pass is disabled and absent from the expanded graph.
- VAE families: FLUX.1, FLUX.2, Qwen Image, and experimental Mage-VAE.

FLUX.1, FLUX.2, and Qwen Image use matched VAE/PiD pairs. Mage-VAE is an
experimental bridge: its unscaled 128-channel, 16x-downsampled latent is sent to
the FLUX.2 PiD checkpoint because NVIDIA has not published a Mage-VAE-specific
PiD checkpoint. Mage-VAE encoding runs in the isolated Mage worker and supports
every tiled PiD path. The node also uses the PixelDiT Gemma text encoder and
ComfyUI's `pixel_space` VAE for output decoding. FLUX.2 is the default PiD VAE
family. The pinned tile merger permits a final canvas up to 32768 px per side.
Model downloads remain blocked
until the NVIDIA noncommercial license checkbox is explicitly enabled.

`enhance_prompt_with_qwen` is enabled by default. It invokes the Video pack's
`ComfyColabQwen38ImagePromptEnhancer` before any PiD model allocation. That node
uses thinking-enabled Qwen3.8-27B Q4_K_M and its pinned vision projector to
inspect the first image and write a detailed, source-preserving PiD prompt. The
Qwen llama.cpp process terminates before PiD starts. The exact prompt used by
PiD is returned as the second `STRING` output; disable the option to use the
manual prompt unchanged.

See [`docs/pid-upscaler.md`](../../docs/pid-upscaler.md) for model sources,
limits, and licensing.
