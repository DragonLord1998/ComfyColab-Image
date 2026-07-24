#!/usr/bin/env python3
"""Install standalone-only dependencies without changing ComfyUI's core stack."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STANDALONE_ROOT = ROOT / ".standalone"
MAGE_ROOT = STANDALONE_ROOT / "mage"
MAGE_SOURCE = MAGE_ROOT / "source" / "Mage"
MAGE_PACKAGES = MAGE_ROOT / "python-packages"
MAGE_REF = "1c4727a6daea1200488d9c68544ebea2e784c765"
MAGE_ARCHIVE_URL = f"https://github.com/microsoft/Mage/archive/{MAGE_REF}.zip"
MAGE_ARCHIVE_SHA256 = (
    "18cfe789666a37f79d5b40376aa1ddfae5f5d29a90a6d690dcbe70baf1644944"
)
GGUF_REPOSITORY = "https://github.com/city96/ComfyUI-GGUF.git"
GGUF_REF = "6ea2651e7df66d7585f6ffee804b20e92fb38b8a"
MAGE_PACKAGE_MODULES = (
    "accelerate",
    "diffusers",
    "huggingface_hub",
    "hf_xet",
    "loguru",
    "transformers",
)


def _run(*argv: str, cwd: Path | None = None) -> None:
    subprocess.run(
        list(argv),
        cwd=str(cwd) if cwd else None,
        check=True,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ComfyColab-Image-Standalone-Installer/1"},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)


def _commit(path: Path) -> str | None:
    if not (path / ".git").is_dir():
        return None
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _mage_packages_ready() -> bool:
    return all(
        (MAGE_PACKAGES / module / "__init__.py").is_file()
        for module in MAGE_PACKAGE_MODULES
    )


def _install_mage_source() -> None:
    marker = MAGE_ROOT / "source.json"
    pipeline = MAGE_SOURCE / "mage_flow" / "pipeline.py"
    expected = {"revision": MAGE_REF, "archive_sha256": MAGE_ARCHIVE_SHA256}
    if pipeline.is_file() and marker.is_file():
        try:
            if json.loads(marker.read_text(encoding="utf-8")) == expected:
                return
        except (OSError, json.JSONDecodeError):
            pass

    MAGE_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="comfycolab-mage-install-") as raw:
        temporary = Path(raw)
        archive = temporary / "mage.zip"
        _download(MAGE_ARCHIVE_URL, archive)
        actual = _sha256(archive)
        if actual != MAGE_ARCHIVE_SHA256:
            raise RuntimeError(
                "Pinned Mage archive checksum mismatch: "
                f"expected {MAGE_ARCHIVE_SHA256}, got {actual}"
            )
        extract_root = temporary / "extract"
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(extract_root)
        candidates = list(extract_root.glob("Mage-*/mage_flow/pipeline.py"))
        if len(candidates) != 1:
            raise RuntimeError("Pinned Mage archive has an unexpected layout")
        source_root = candidates[0].parents[1]
        staged = temporary / "Mage"
        shutil.copytree(source_root, staged)
        if MAGE_SOURCE.exists():
            shutil.rmtree(MAGE_SOURCE)
        staged.replace(MAGE_SOURCE)
    marker.write_text(json.dumps(expected, sort_keys=True) + "\n", encoding="utf-8")


def _install_mage_packages() -> None:
    requirements = ROOT / "requirements-mage-worker.txt"
    expected = {
        "python": sys.version.split()[0],
        "requirements_sha256": _sha256(requirements),
    }
    marker = MAGE_ROOT / "python-packages.json"
    if marker.is_file():
        try:
            if (
                json.loads(marker.read_text(encoding="utf-8")) == expected
                and _mage_packages_ready()
            ):
                return
        except (OSError, json.JSONDecodeError):
            pass
    if MAGE_PACKAGES.exists():
        shutil.rmtree(MAGE_PACKAGES)
    MAGE_PACKAGES.mkdir(parents=True, exist_ok=True)
    _run(
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-deps",
        "--target",
        str(MAGE_PACKAGES),
        "-r",
        str(requirements),
    )
    marker.write_text(json.dumps(expected, sort_keys=True) + "\n", encoding="utf-8")


def _custom_nodes_root() -> Path | None:
    parent = ROOT.parent
    return parent if parent.name == "custom_nodes" else None


def _install_gguf() -> None:
    custom_nodes = _custom_nodes_root()
    if custom_nodes is None:
        print(
            "[ComfyColab Image] Repository is not directly under a custom_nodes "
            "folder; skipping sibling ComfyUI-GGUF installation."
        )
        return
    target = custom_nodes / "ComfyUI-GGUF"
    if target.exists():
        actual = _commit(target)
        if actual != GGUF_REF:
            raise RuntimeError(
                "Existing ComfyUI-GGUF is not the audited revision required by "
                f"ComfyColab Image. Expected {GGUF_REF}, found "
                f"{actual or 'a non-git installation'}. Move or update that "
                "checkout explicitly, then rerun this installer."
            )
        print(
            "[ComfyColab Image] Existing pinned ComfyUI-GGUF installation reused: "
            f"{target} ({actual})."
        )
        return
    _run(
        "git",
        "clone",
        "--filter=blob:none",
        GGUF_REPOSITORY,
        str(target),
    )
    _run("git", "fetch", "origin", GGUF_REF, "--depth", "1", cwd=target)
    _run("git", "checkout", "--detach", "FETCH_HEAD", cwd=target)
    requirements = target / "requirements.txt"
    if requirements.is_file():
        _run(
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(requirements),
        )


def _check() -> None:
    checks = {
        "mage_source": (MAGE_SOURCE / "mage_flow" / "pipeline.py").is_file(),
        "mage_packages": _mage_packages_ready(),
        "mage_worker": (
            ROOT / "worker" / "mage_flow" / "worker_main.py"
        ).is_file(),
    }
    custom_nodes = _custom_nodes_root()
    if custom_nodes is not None:
        gguf = custom_nodes / "ComfyUI-GGUF"
        checks["comfyui_gguf"] = (
            (gguf / "__init__.py").is_file() and _commit(gguf) == GGUF_REF
        )
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks.values()):
        raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify standalone dependencies without changing anything.",
    )
    parser.add_argument(
        "--skip-gguf",
        action="store_true",
        help="Do not install the sibling ComfyUI-GGUF dependency.",
    )
    args = parser.parse_args()
    if args.check:
        _check()
        return 0
    _install_mage_source()
    _install_mage_packages()
    if not args.skip_gguf:
        _install_gguf()
    _check()
    print("[ComfyColab Image] Standalone installation complete. Restart ComfyUI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
