# capture_streaming.py
"""Zero‑copy, asynchronous screen‑capture pipeline for scouter_agent.

This module provides:
    * CaptureConfig – simple dataclass for tunables.
    * capture_frame() – core routine: grabs one PNG via ADB, returns np.ndarray (BGR).
    * capturer() – coroutine that streams frames into an asyncio.Queue with back‑pressure.
    * Example CLI benchmark: `python -m capture_streaming --benchmark`.

Designed to be *importable* by ScreenshotScoutingService, but also runnable
stand‑alone for latency profiling.
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import cv2
import numpy as np

PNG_HEADER = b"\x89PNG\r\n\x1a\n"
PNG_FOOTER = b"IEND\xaeB`\x82"


@dataclass(slots=True)
class CaptureConfig:
    adb_path: str = "adb"                    # Override if not on PATH
    device_serial: Optional[str] = None       # "emulator-5554", etc.
    queue_maxsize: int = 32                   # Back‑pressure depth
    log_every: int = 50                       # Print FPS every N frames


async def _run_adb_screencap(cfg: CaptureConfig) -> bytes:
    """Executes a single `adb exec-out screencap -p` and returns raw PNG bytes."""
    cmd = [cfg.adb_path]
    if cfg.device_serial:
        cmd += ["-s", cfg.device_serial]
    cmd += ["exec-out", "screencap", "-p"]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"adb screencap failed: {stderr.decode().strip()}")
    return stdout


def _decode_png(buf: bytes) -> np.ndarray:
    """Zero‑copy PNG→BGR np.ndarray using cv2.imdecode."""
    # Guard: some devices prepend stray bytes before PNG header
    start = buf.find(PNG_HEADER)
    if start == -1:
        raise ValueError("PNG header not found in adb output")
    # imdecode needs a contiguous uint8 array
    np_buf = np.frombuffer(buf[start:], dtype=np.uint8)
    img = cv2.imdecode(np_buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("cv2.imdecode returned None – corrupted PNG?")
    return img


async def capture_frame(cfg: CaptureConfig) -> np.ndarray:
    """High‑level helper: one frame → ndarray (BGR)."""
    raw_png = await _run_adb_screencap(cfg)
    return _decode_png(raw_png)


async def capturer(queue: asyncio.Queue[np.ndarray], cfg: CaptureConfig, stop_event: asyncio.Event | None = None):
    """Continuously capture frames and place them in *queue* (with back‑pressure)."""
    frame_count = 0
    t0 = time.perf_counter()
    while stop_event is None or not stop_event.is_set():
        frame = await capture_frame(cfg)
        await queue.put(frame)  # blocks when queue is full (back‑pressure)
        frame_count += 1
        if frame_count % cfg.log_every == 0:
            t1 = time.perf_counter()
            fps = cfg.log_every / (t1 - t0)
            print(f"[CAPTURE] {fps:.2f} FPS (last {cfg.log_every} frames)")
            t0 = t1


# -----------------------------------------------------------------------------
# Example standalone benchmark
# -----------------------------------------------------------------------------
async def _benchmark(cfg: CaptureConfig, n_frames: int = 100):
    t0 = time.perf_counter()
    for _ in range(n_frames):
        await capture_frame(cfg)
    dt = time.perf_counter() - t0
    print(f"Captured {n_frames} frames in {dt:.2f}s  →  {n_frames/dt:.2f} FPS")


def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark ADB screencap streaming")
    parser.add_argument("--frames", type=int, default=100, help="Number of frames to grab")
    parser.add_argument("--serial", type=str, help="ADB device serial")
    parser.add_argument("--adb", type=str, default="adb", help="ADB executable path")
    args = parser.parse_args()

    cfg = CaptureConfig(adb_path=args.adb, device_serial=args.serial)
    asyncio.run(_benchmark(cfg, n_frames=args.frames))


if __name__ == "__main__":
    _cli()
