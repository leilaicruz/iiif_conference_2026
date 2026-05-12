"""Small IIIF image-analysis helpers for Streamlit demos.

The functions intentionally avoid saving local image copies. They discover Image API
services from a IIIF Presentation v3 manifest, fetch downsampled derivatives, and run
lightweight in-memory analyses that can later be moved into a reusable repository module.
"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Any

import numpy as np
import requests
from PIL import Image


@dataclass
class CanvasImageAnalysis:
    index: int
    label: str
    canvas_id: str
    service_id: str
    image_url: str
    brightness: float


def _first(value: Any, default=None):
    if value is None:
        return default
    if isinstance(value, list):
        return value[0] if value else default
    return value


def get_canvas_label(canvas: dict[str, Any]) -> str:
    """Best-effort human-readable label for a canvas."""
    label = canvas.get("label")
    if isinstance(label, dict):
        if "en" in label and label["en"]:
            return str(label["en"][0])
        for values in label.values():
            if values:
                return str(values[0])
        return ""
    return str(label) if label is not None else ""


def get_image_service_id_from_canvas(canvas: dict[str, Any]) -> str | None:
    """Extract the IIIF Image API service base URL from a IIIF v3 canvas."""
    annotation_page = _first(canvas.get("items"), default={})
    annotation = _first(annotation_page.get("items"), default={})
    body = annotation.get("body") or {}
    service = _first(body.get("service"), default=None)

    if not isinstance(service, dict):
        return None

    return service.get("id") or service.get("@id")


def build_iiif_image_url(
    service_id: str,
    region: str = "full",
    size: str = "!300,300",
    rotation: str = "0",
    quality: str = "default",
    fmt: str = "jpg",
) -> str:
    """Construct a IIIF Image API URL."""
    return f"{service_id.rstrip('/')}/{region}/{size}/{rotation}/{quality}.{fmt}"


def fetch_pil_image(url: str, timeout: int = 240) -> Image.Image:
    """Fetch an image URL into memory as a PIL Image."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")


def brightness_score(image: Image.Image) -> float:
    """Mean luminance score using Rec. 601 luma coefficients."""
    arr = np.asarray(image).astype(np.float32)
    y = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    return float(y.mean())


def canvases_with_image_services(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Return manifest canvases that expose a IIIF Image API service."""
    canvases = manifest.get("items") or []
    return [canvas for canvas in canvases if get_image_service_id_from_canvas(canvas)]


def analyze_brightness(
    manifest: dict[str, Any],
    max_canvases: int = 12,
    derivative_size: str = "!256,256",
) -> list[CanvasImageAnalysis]:
    """Compute mean brightness for downsampled derivatives of manifest canvases."""
    results: list[CanvasImageAnalysis] = []
    for index, canvas in enumerate(canvases_with_image_services(manifest)[:max_canvases]):
        label = get_canvas_label(canvas) or f"Canvas {index}"
        service_id = get_image_service_id_from_canvas(canvas)
        if not service_id:
            continue
        image_url = build_iiif_image_url(service_id, size=derivative_size)
        image = fetch_pil_image(image_url)
        results.append(
            CanvasImageAnalysis(
                index=index,
                label=label,
                canvas_id=str(canvas.get("id", "")),
                service_id=service_id,
                image_url=image_url,
                brightness=brightness_score(image),
            )
        )
    return results


def fetch_thumbnail_grid(
    manifest: dict[str, Any],
    max_canvases: int = 8,
    derivative_size: str = "!300,300",
) -> list[tuple[str, Image.Image]]:
    """Fetch thumbnails for a small preview gallery."""
    thumbnails: list[tuple[str, Image.Image]] = []
    for index, canvas in enumerate(canvases_with_image_services(manifest)[:max_canvases]):
        label = get_canvas_label(canvas) or f"Canvas {index}"
        service_id = get_image_service_id_from_canvas(canvas)
        if not service_id:
            continue
        url = build_iiif_image_url(service_id, size=derivative_size)
        thumbnails.append((label, fetch_pil_image(url)))
    return thumbnails


def sobel_edge_magnitude(gray: np.ndarray) -> np.ndarray:
    """Small Sobel implementation using NumPy only, suitable for small regions."""
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)

    g = gray.astype(np.float32)
    gp = np.pad(g, 1, mode="edge")
    gx = np.zeros_like(g, dtype=np.float32)
    gy = np.zeros_like(g, dtype=np.float32)

    for i in range(g.shape[0]):
        for j in range(g.shape[1]):
            patch = gp[i : i + 3, j : j + 3]
            gx[i, j] = np.sum(patch * kx)
            gy[i, j] = np.sum(patch * ky)

    return np.sqrt(gx**2 + gy**2)


def analyze_central_region_edges(
    manifest: dict[str, Any],
    canvas_index: int = 0,
    region: str = "full",
    derivative_size: str = "!512,512",
) -> tuple[str, Image.Image, Image.Image]:
    """Fetch the full image from one canvas and return it plus an edge image.

    Some IIIF servers reject percentage regions such as ``pct:25,25,50,50``
    for specific resources. Using ``full`` is more robust for this demo.
    The ``derivative_size`` parameter still keeps the downloaded image small.
    """
    canvases = canvases_with_image_services(manifest)
    if not canvases:
        raise ValueError("No canvases with IIIF Image API services were found.")
    if canvas_index < 0 or canvas_index >= len(canvases):
        raise ValueError(f"canvas_index must be between 0 and {len(canvases) - 1}.")

    canvas = canvases[canvas_index]
    service_id = get_image_service_id_from_canvas(canvas)
    if not service_id:
        raise ValueError("Selected canvas does not expose an Image API service.")

    region_url = build_iiif_image_url(service_id, region=region, size=derivative_size)
    region_image = fetch_pil_image(region_url)

    arr = np.asarray(region_image).astype(np.float32)
    gray = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]
    edges = sobel_edge_magnitude(gray)
    max_value = float(edges.max()) if edges.size else 0.0
    if max_value > 0:
        edges = edges / max_value * 255.0
    edge_image = Image.fromarray(edges.astype(np.uint8), mode="L")

    return region_url, region_image, edge_image
