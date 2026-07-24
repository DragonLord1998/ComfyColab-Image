"""
@author: DragonLord1998
@title: ComfyColab Image
@nickname: ComfyColab Image
@description: Standalone image generation, editing, Mage-Flow, and NVIDIA PiD nodes.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def _load_internal_package(alias: str, directory: str):
    """Load a nested node root without depending on the checkout folder name."""

    module_name = f"{__name__}.{alias}"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    package_dir = ROOT / "custom_nodes" / directory
    spec = importlib.util.spec_from_file_location(
        module_name,
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load internal node package: {package_dir}")
    package = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = package
    try:
        spec.loader.exec_module(package)
    except BaseException:
        sys.modules.pop(module_name, None)
        raise
    return package


def _input_port(io: Any, name: str, descriptor: tuple, *, optional: bool):
    value_type = descriptor[0]
    config = dict(descriptor[1]) if len(descriptor) > 1 else {}
    if isinstance(value_type, (list, tuple)):
        return io.Combo.Input(
            name,
            options=list(value_type),
            optional=optional,
            **config,
        )
    factories = {
        "BOOLEAN": io.Boolean,
        "FLOAT": io.Float,
        "IMAGE": io.Image,
        "INT": io.Int,
        "STRING": io.String,
    }
    factory = factories.get(str(value_type), io.Custom(str(value_type)))
    return factory.Input(name, optional=optional, **config)


def _output_port(io: Any, value_type: str, name: str):
    factories = {
        "AUDIO": io.Audio,
        "CLIP": io.Clip,
        "CONDITIONING": io.Conditioning,
        "IMAGE": io.Image,
        "LATENT": io.Latent,
        "MASK": io.Mask,
        "MODEL": io.Model,
        "VAE": io.Vae,
        "VIDEO": io.Video,
    }
    factory = factories.get(str(value_type), io.Custom(str(value_type)))
    return factory.Output(name)


def _v3_adapter(io: Any, node_id: str, display_name: str, core: type):
    """Adapt the legacy loader nodes so the root can be one V3 extension."""

    @classmethod
    def define_schema(cls):
        declared = core.INPUT_TYPES()
        inputs = []
        for section, optional in (("required", False), ("optional", True)):
            for name, descriptor in declared.get(section, {}).items():
                inputs.append(
                    _input_port(io, name, descriptor, optional=optional)
                )
        output_names = getattr(
            core,
            "RETURN_NAMES",
            tuple(f"output_{index}" for index in range(len(core.RETURN_TYPES))),
        )
        outputs = [
            _output_port(io, value_type, output_names[index])
            for index, value_type in enumerate(core.RETURN_TYPES)
        ]
        return io.Schema(
            node_id=node_id,
            display_name=display_name,
            category=getattr(core, "CATEGORY", "ComfyColab/Image"),
            description=getattr(core, "DESCRIPTION", None),
            inputs=inputs,
            outputs=outputs,
        )

    @classmethod
    def execute(cls, **kwargs):
        function = getattr(core(), core.FUNCTION)
        values = function(**kwargs)
        if not isinstance(values, tuple):
            values = (values,)
        return io.NodeOutput(*values)

    namespace = {
        "__module__": __name__,
        "define_schema": define_schema,
        "execute": execute,
    }
    if hasattr(core, "IS_CHANGED"):

        @classmethod
        def fingerprint_inputs(cls, **kwargs):
            return core.IS_CHANGED(**kwargs)

        namespace["fingerprint_inputs"] = fingerprint_inputs
    return type(core.__name__, (io.ComfyNode,), namespace)


async def _extension_nodes(package) -> list[type]:
    entrypoint = package.comfy_entrypoint
    extension = entrypoint()
    if inspect.isawaitable(extension):
        extension = await extension
    return list(await extension.get_node_list())


async def comfy_entrypoint():
    latest = importlib.import_module("comfy_api.latest")
    zimage = _load_internal_package("_zimage", "ComfyColab-ZImage")
    mage = _load_internal_package("_mageflow", "ComfyColab-MageFlow")
    pid = _load_internal_package("_pid", "ComfyColab-PiD")

    node_classes = [
        _v3_adapter(
            latest.io,
            node_id,
            zimage.NODE_DISPLAY_NAME_MAPPINGS.get(node_id, node_id),
            core,
        )
        for node_id, core in zimage.NODE_CLASS_MAPPINGS.items()
    ]
    node_classes.extend(await _extension_nodes(mage))
    node_classes.extend(await _extension_nodes(pid))

    class ComfyColabImageExtension(latest.ComfyExtension):
        async def get_node_list(self):
            return node_classes

    return ComfyColabImageExtension()


__all__ = ["comfy_entrypoint"]
