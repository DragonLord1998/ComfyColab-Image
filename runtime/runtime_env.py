#!/usr/bin/env python3
"""Return resolver-owned paths for the Image pack's isolated workers."""

from __future__ import annotations

import json
import sys


def main() -> int:
    raw_context = sys.stdin.read()
    context = json.loads(raw_context) if raw_context.strip() else {}
    paths = context.get("resolved_paths", {})
    pack_root = context.get("pack_root", "/content/.comfycolab/packs/image")
    print(
        json.dumps(
            {
                "schema": 1,
                "hook": "runtime_env",
                "status": "ok",
                "environment": {
                    "COMFYCOLAB_MAGEFLOW_WORKER": (
                        f"{pack_root}/worker/mage_flow/worker_main.py"
                    ),
                    "COMFYCOLAB_MAGEFLOW_SOURCE": paths.get(
                        "mage-flow-source",
                        "/content/.comfycolab/dependencies/sources/Mage",
                    ),
                    "COMFYCOLAB_MAGEFLOW_MODEL": paths.get(
                        "mage-flow-model",
                        "/content/.comfycolab/dependencies/models/image/mage-flow",
                    ),
                    "COMFYCOLAB_MAGEFLOW_TURBO_MODEL": paths.get(
                        "mage-flow-turbo-model",
                        "/content/.comfycolab/dependencies/models/image/mage-flow-turbo",
                    ),
                    "COMFYCOLAB_MAGEFLOW_EDIT_MODEL": paths.get(
                        "mage-flow-edit-model",
                        "/content/.comfycolab/dependencies/models/image/mage-flow-edit",
                    ),
                    "COMFYCOLAB_MAGEFLOW_EDIT_TURBO_MODEL": paths.get(
                        "mage-flow-edit-turbo-model",
                        "/content/.comfycolab/dependencies/models/image/mage-flow-edit-turbo",
                    ),
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
