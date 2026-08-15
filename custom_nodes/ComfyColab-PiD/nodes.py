from __future__ import annotations

import importlib
from typing import Any

from .catalog import MAGE_VAE_EXPERIMENTAL, backbone_names
from .graph import MAGE_REQUIRED_NODES, REQUIRED_NODES, SCALE_FACTORS, build_pid_graph
from .models import ensure_pid_assets


MAX_SEED = (2**63) - 1
MAX_MERGED_DIMENSION = 32768
SCALE_OPTIONS = ["2x", "4x", "8x", "16x"]
QWEN_IMAGE_PROMPT_NODE_ID = "ComfyColabQwen38ImagePromptEnhancer"


def _io():
    return importlib.import_module("comfy_api.latest").io


def _require_upstream_nodes(vae_family: str, enhance_prompt_with_qwen: bool) -> None:
    try:
        registry = importlib.import_module("nodes").NODE_CLASS_MAPPINGS
    except (ModuleNotFoundError, AttributeError):
        return
    required = REQUIRED_NODES
    if vae_family == MAGE_VAE_EXPERIMENTAL:
        required = required | MAGE_REQUIRED_NODES
    if enhance_prompt_with_qwen:
        required = required | {QWEN_IMAGE_PROMPT_NODE_ID}
    missing = sorted(required - set(registry))
    if missing:
        raise RuntimeError(
            "ComfyColab PiD requires a pinned ComfyUI build with PixelDiT/PiD "
            f"support. Missing node IDs: {', '.join(missing)}. Restart with "
            "`comfycolab start --refresh`."
        )


def _enhance_prompt(
    image: Any,
    prompt: str,
    *,
    seed: int,
    force_redownload: bool,
) -> str:
    registry = importlib.import_module("nodes").NODE_CLASS_MAPPINGS
    enhancer_class = registry.get(QWEN_IMAGE_PROMPT_NODE_ID)
    if enhancer_class is None:
        raise RuntimeError(
            "PiD Qwen prompt enhancement requires the current ComfyColab Video "
            f"pack node {QWEN_IMAGE_PROMPT_NODE_ID}. Restart with "
            "`comfycolab start --refresh`."
        )
    result = enhancer_class.execute(
        image=image,
        prompt=prompt,
        seed=seed % (2**31),
        max_tokens=4096,
        temperature=1.0,
        force_redownload=force_redownload,
    )
    enhanced = result[0] if isinstance(result, (tuple, list)) and result else None
    if not isinstance(enhanced, str) or not enhanced.strip():
        raise RuntimeError("Qwen Image Prompt Enhancer returned an empty prompt.")
    return enhanced.strip()


def _image_dimensions(image: Any) -> tuple[int, int]:
    shape = getattr(image, "shape", None)
    if shape is None and image is not None:
        shape = getattr(getattr(image, "movedim", None), "shape", None)
    if shape is None or len(shape) < 3:
        raise ValueError("PiD upscale requires an IMAGE tensor with shape [B, H, W, C].")
    return int(shape[2]), int(shape[1])


def _validate_output_dimensions(width: int, height: int, scale: str) -> None:
    factor = SCALE_FACTORS[scale]
    output_width = width * factor
    output_height = height * factor
    if output_width > MAX_MERGED_DIMENSION or output_height > MAX_MERGED_DIMENSION:
        raise ValueError(
            f"PiD {scale} would produce {output_width}x{output_height}, but the "
            "pinned ComfyUI ImageMergeTileList node supports at most "
            f"{MAX_MERGED_DIMENSION}px per side. Reduce the input size or scale."
        )


class ComfyColabPiDUpscale:
    @classmethod
    def define_schema(cls):
        io = _io()
        return io.Schema(
            node_id="ComfyColabPiDUpscale",
            display_name="ComfyColab PiD — Image Upscaler",
            category="ComfyColab/Image",
            description=(
                "Tiled 2x/4x/8x/16x image upscale through NVIDIA PiD / PixelDiT. "
                "Optional Qwen3.8 vision with thinking inspects the image and writes "
                "the PiD prompt before PiD models are allocated."
            ),
            enable_expand=True,
            inputs=[
                io.Image.Input("image"),
                io.Combo.Input(
                    "vae_family",
                    options=backbone_names(),
                    default="FLUX.2",
                    tooltip=(
                        "Selects the PiD checkpoint and VAE family. Mage-VAE is an "
                        "experimental bridge through the FLUX.2 PiD checkpoint."
                    ),
                ),
                io.String.Input(
                    "prompt",
                    multiline=True,
                    default="high fidelity detailed image upscale",
                ),
                io.Boolean.Input(
                    "enhance_prompt_with_qwen",
                    default=True,
                    tooltip=(
                        "Use thinking-enabled Qwen3.8-27B Q4 vision to inspect the "
                        "image and replace the manual text with a detailed, faithful "
                        "PiD prompt. Requires the ComfyColab Video pack."
                    ),
                ),
                io.Combo.Input("scale", options=SCALE_OPTIONS, default="4x"),
                io.Int.Input("seed", default=0, min=0, max=MAX_SEED),
                io.Float.Input(
                    "degrade_sigma",
                    default=0.0,
                    min=0.0,
                    max=1.0,
                    step=0.05,
                    advanced=True,
                ),
                io.Int.Input(
                    "tile_size",
                    default=1536,
                    min=512,
                    max=4096,
                    step=64,
                    advanced=True,
                ),
                io.Int.Input(
                    "tile_overlap",
                    default=384,
                    min=64,
                    max=1024,
                    step=32,
                    advanced=True,
                ),
                io.Boolean.Input(
                    "accept_nvidia_noncommercial_license",
                    default=False,
                    tooltip=(
                        "Required before downloads. Comfy-Org PixelDiT is "
                        "published under the NVIDIA Source Code License V1."
                    ),
                ),
                io.Boolean.Input(
                    "force_redownload",
                    default=False,
                    advanced=True,
                    tooltip="Discard resumable cached files and download selected assets again.",
                ),
            ],
            outputs=[
                io.Image.Output("image"),
                io.String.Output("enhanced_prompt"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image,
        vae_family="FLUX.2",
        prompt="high fidelity detailed image upscale",
        enhance_prompt_with_qwen=True,
        scale="4x",
        seed=0,
        degrade_sigma=0.0,
        tile_size=1536,
        tile_overlap=384,
        accept_nvidia_noncommercial_license=False,
        force_redownload=False,
    ):
        if not accept_nvidia_noncommercial_license:
            raise PermissionError(
                "PiD downloads are blocked until "
                "accept_nvidia_noncommercial_license is true. "
                "Comfy-Org PixelDiT/PiD is published under NVIDIA Source Code License V1."
            )
        if vae_family not in backbone_names():
            raise ValueError(f"Unknown PiD VAE family: {vae_family}.")
        if scale not in SCALE_OPTIONS:
            raise ValueError("PiD scale must be one of 2x, 4x, 8x, or 16x.")
        seed = int(seed)
        degrade_sigma = float(degrade_sigma)
        tile_size = int(tile_size)
        tile_overlap = int(tile_overlap)
        if seed < 0 or seed > MAX_SEED:
            raise ValueError(f"seed must be between 0 and {MAX_SEED}.")
        if not 0.0 <= degrade_sigma <= 1.0:
            raise ValueError("degrade_sigma must be between 0 and 1.")
        if tile_overlap >= tile_size:
            raise ValueError("tile_overlap must be smaller than tile_size.")
        width, height = _image_dimensions(image)
        _validate_output_dimensions(width, height, scale)
        _require_upstream_nodes(vae_family, bool(enhance_prompt_with_qwen))
        working_prompt = str(prompt).strip()
        if enhance_prompt_with_qwen:
            working_prompt = _enhance_prompt(
                image,
                working_prompt,
                seed=seed,
                force_redownload=bool(force_redownload),
            )
        if not working_prompt:
            raise ValueError(
                "PiD requires a non-empty prompt when Qwen prompt enhancement is disabled."
            )
        model_names = ensure_pid_assets(
            vae_family,
            force_redownload=bool(force_redownload),
        )
        return build_pid_graph(
            image=image,
            prompt=working_prompt,
            scale=scale,
            width=width,
            height=height,
            seed=seed,
            degrade_sigma=degrade_sigma,
            tile_size=tile_size,
            tile_overlap=tile_overlap,
            vae_family=vae_family,
            model_names=model_names,
        )


PUBLIC_NODE_CLASS_MAPPINGS = {
    "ComfyColabPiDUpscale": ComfyColabPiDUpscale,
}

NODE_CLASS_MAPPINGS = dict(PUBLIC_NODE_CLASS_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyColabPiDUpscale": "ComfyColab PiD — Image Upscaler",
}
