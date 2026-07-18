#!/usr/bin/env python3
"""Read-only health inspection for ComfyColab Image."""

from __future__ import annotations

import json
from pathlib import Path


EXPECTED_NODE_IDS = (
    "ComfyColabZImageTurboBundleLoader",
    "ComfyColabQwenImageEdit2511BundleLoader",
    "ComfyColabKrea2BundleLoader",
    "ComfyColabFlux2Klein4BBundleLoader",
    "ComfyColabFlux2Klein9BBundleLoader",
    "ComfyColabFlux2DevBundleLoader",
)
EXPECTED_CATALOGS = (
    "z_image_turbo.json",
    "qwen_image_edit_2511.json",
    "krea_2.json",
    "flux_2_klein_4b.json",
    "flux_2_klein_9b.json",
    "flux_2_dev.json",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    node_root = root / "custom_nodes" / "ComfyColab-ZImage"
    source = (node_root / "__init__.py").read_text(encoding="utf-8")
    checks = {
        "node_root": node_root.is_dir(),
        "node_ids": all(node_id in source for node_id in EXPECTED_NODE_IDS),
        "catalogs": all(
            (node_root / "catalog" / name).is_file() for name in EXPECTED_CATALOGS
        ),
    }
    status = "ok" if all(checks.values()) else "error"
    print(
        json.dumps(
            {"schema": 1, "hook": "doctor", "status": status, "checks": checks},
            sort_keys=True,
        )
    )
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
