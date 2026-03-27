"""GPU rendering configuration and capability detection for PromptBIM.

Supports Win RTX 4090 (CUDA/Vulkan/D3D12) and macOS Metal.
"""

from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass, field

from promptbim.debug import get_logger

logger = get_logger("gpu_render")


@dataclass
class GPUInfo:
    """GPU capability info."""

    name: str = "Unknown"
    vram_gb: float = 0.0
    api: str = "none"  # cuda | metal | vulkan | d3d12 | none
    driver_version: str = ""
    cuda_available: bool = False
    rtx_capable: bool = False
    score: int = 0  # higher = better

    def __str__(self) -> str:
        return (
            f"{self.name} | {self.vram_gb:.1f}GB VRAM | "
            f"{self.api.upper()} | RTX={self.rtx_capable} | score={self.score}"
        )


def detect_gpu() -> GPUInfo:
    """Detect GPU capabilities on current platform."""
    system = platform.system()
    if system == "Darwin":
        return _detect_metal()
    elif system == "Windows":
        return _detect_windows_gpu()
    else:
        return _detect_linux_gpu()


def _detect_metal() -> GPUInfo:
    """Detect Apple Metal GPU."""
    info = GPUInfo(api="metal")
    try:
        out = subprocess.check_output(
            ["system_profiler", "SPDisplaysDataType"],
            text=True,
            timeout=5,
        )
        for line in out.splitlines():
            if "Chipset Model" in line or "Chip" in line:
                info.name = line.split(":", 1)[-1].strip()
            if "VRAM" in line:
                raw = line.split(":", 1)[-1].strip()
                try:
                    gb = float(raw.split()[0])
                    if "MB" in raw:
                        gb /= 1024
                    info.vram_gb = gb
                except ValueError:
                    pass
        info.score = int(info.vram_gb * 10)
        logger.info("GPU detected: %s", info)
    except Exception as e:  # noqa: BLE001
        logger.warning("Metal detection failed: %s", e)
    return info


def _detect_windows_gpu() -> GPUInfo:
    """Detect NVIDIA GPU on Windows via nvidia-smi."""
    info = GPUInfo(api="d3d12")
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        )
        parts = [p.strip() for p in out.strip().split(",")]
        if len(parts) >= 3:
            info.name = parts[0]
            info.vram_gb = float(parts[1]) / 1024
            info.driver_version = parts[2]
            info.cuda_available = True
            info.api = "cuda"
            info.rtx_capable = "RTX" in info.name or "3090" in info.name or "4090" in info.name
            info.score = int(info.vram_gb * 20 + (100 if info.rtx_capable else 0))
    except FileNotFoundError:
        logger.warning("nvidia-smi not found — trying wmic")
        try:
            out = subprocess.check_output(
                ["wmic", "path", "win32_VideoController", "get", "Name,AdapterRAM"],
                text=True,
                timeout=5,
            )
            for line in out.splitlines()[1:]:
                if line.strip():
                    parts = line.rsplit(None, 1)
                    if len(parts) == 2:
                        info.name = parts[0].strip()
                        try:
                            info.vram_gb = int(parts[1]) / (1024**3)
                        except ValueError:
                            pass
                    break
        except Exception as e2:  # noqa: BLE001
            logger.warning("wmic fallback failed: %s", e2)
    except Exception as e:  # noqa: BLE001
        logger.warning("Windows GPU detection failed: %s", e)
    return info


def _detect_linux_gpu() -> GPUInfo:
    """Detect GPU on Linux."""
    info = GPUInfo(api="vulkan")
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            text=True,
            timeout=5,
        )
        parts = out.strip().split(",")
        if len(parts) >= 2:
            info.name = parts[0].strip()
            info.vram_gb = float(parts[1]) / 1024
            info.cuda_available = True
            info.api = "cuda"
            info.rtx_capable = "RTX" in info.name
            info.score = int(info.vram_gb * 20 + (100 if info.rtx_capable else 0))
    except Exception as e:  # noqa: BLE001
        logger.debug("Linux GPU fallback: %s", e)
    return info


def get_render_config(gpu: GPUInfo | None = None) -> dict:
    """Return optimal render config dict for detected GPU."""
    if gpu is None:
        gpu = detect_gpu()

    config: dict = {
        "gpu_name": gpu.name,
        "vram_gb": gpu.vram_gb,
        "api": gpu.api,
        "rtx": gpu.rtx_capable,
        "shadows": gpu.score >= 50,
        "aa_samples": 8 if gpu.rtx_capable else 4,
        "max_instances": 50_000 if gpu.rtx_capable else 10_000,
        "texture_resolution": 2048 if gpu.vram_gb >= 8 else 1024,
        "pbr_enabled": gpu.score >= 30,
        "raytracing": gpu.rtx_capable and gpu.vram_gb >= 8,
    }
    logger.info("Render config: %s", config)
    return config


# --- RTX 4090 preset (Win) ---
RTX4090_CONFIG = {
    "gpu_name": "NVIDIA GeForce RTX 4090",
    "vram_gb": 24.0,
    "api": "cuda",
    "rtx": True,
    "shadows": True,
    "aa_samples": 8,
    "max_instances": 500_000,
    "texture_resolution": 4096,
    "pbr_enabled": True,
    "raytracing": True,
}

# Env override for CI / offscreen
if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
    _OFFSCREEN_CONFIG = {
        "gpu_name": "Offscreen",
        "vram_gb": 0.0,
        "api": "none",
        "rtx": False,
        "shadows": False,
        "aa_samples": 1,
        "max_instances": 1000,
        "texture_resolution": 512,
        "pbr_enabled": False,
        "raytracing": False,
    }


def active_render_config() -> dict:
    """Return config: offscreen override → env preset → auto-detect."""
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        return _OFFSCREEN_CONFIG  # type: ignore[return-value]
    if os.environ.get("PROMPTBIM_GPU_PRESET") == "rtx4090":
        return RTX4090_CONFIG
    return get_render_config()
