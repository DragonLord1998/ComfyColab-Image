from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path

from test_mageflow_node_pack import FakeIO


ROOT = Path(__file__).resolve().parents[1]


def load_root_package():
    name = "normalized_manager_install_name"
    for module_name in list(sys.modules):
        if module_name == name or module_name.startswith(name + "."):
            del sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    package = importlib.util.module_from_spec(spec)
    sys.modules[name] = package
    assert spec.loader is not None
    spec.loader.exec_module(package)
    return package


class StandaloneLoadingTests(unittest.TestCase):
    def setUp(self):
        self.saved_modules = {
            name: sys.modules.get(name)
            for name in ("comfy_api", "comfy_api.latest")
        }
        FakeIO.Audio = type(FakeIO.Image)("AUDIO")
        FakeIO.Video = type(FakeIO.Image)("VIDEO")
        latest = types.ModuleType("comfy_api.latest")
        latest.io = FakeIO
        latest.ComfyExtension = type("ComfyExtension", (), {})
        api = types.ModuleType("comfy_api")
        api.latest = latest
        sys.modules.update(
            {"comfy_api": api, "comfy_api.latest": latest}
        )

    def tearDown(self):
        for name, module in self.saved_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def test_root_is_one_v3_extension_with_every_public_node(self):
        before = set(sys.modules)
        package = load_root_package()
        imported = set(sys.modules) - before
        self.assertFalse(
            {"torch", "numpy", "PIL", "diffusers", "transformers"} & imported
        )
        self.assertFalse(hasattr(package, "NODE_CLASS_MAPPINGS"))

        extension = asyncio.run(package.comfy_entrypoint())
        node_classes = asyncio.run(extension.get_node_list())
        schemas = [node.define_schema() for node in node_classes]
        public_ids = {
            schema.node_id
            for schema in schemas
            if not getattr(schema, "is_dev_only", False)
        }
        declared = set(
            json.loads((ROOT / "node_list.json").read_text(encoding="utf-8"))
        )
        self.assertEqual(public_ids, declared)

    def test_legacy_bundle_loaders_are_adapted_to_standard_v3_outputs(self):
        package = load_root_package()
        extension = asyncio.run(package.comfy_entrypoint())
        node_classes = asyncio.run(extension.get_node_list())
        schemas = {
            node.define_schema().node_id: node.define_schema()
            for node in node_classes
        }
        schema = schemas["ComfyColabZImageTurboBundleLoader"]
        self.assertEqual(
            [port["io_type"] for port in schema.outputs],
            ["MODEL", "CLIP", "VAE"],
        )
        self.assertEqual(
            [port["name"] for port in schema.inputs],
            ["quantization", "force_redownload"],
        )

    def test_manager_and_manual_install_files_are_present(self):
        self.assertTrue((ROOT / "install.py").is_file())
        self.assertTrue((ROOT / "requirements.txt").is_file())
        self.assertTrue((ROOT / "requirements-mage-worker.txt").is_file())
        self.assertTrue((ROOT / "node_list.json").is_file())
        source = (ROOT / "install.py").read_text(encoding="utf-8")
        self.assertIn("MAGE_ARCHIVE_SHA256", source)
        self.assertIn("GGUF_REF", source)
        self.assertIn("MAGE_PACKAGE_MODULES", source)
        self.assertIn("_commit(gguf) == GGUF_REF", source)


if __name__ == "__main__":
    unittest.main()
