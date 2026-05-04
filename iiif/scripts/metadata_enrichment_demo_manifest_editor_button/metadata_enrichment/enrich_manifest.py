"""Utilities for enriching IIIF Presentation API v3 manifests with 4TU.ResearchData metadata."""

from __future__ import annotations

import copy
import html
import json
import re
from dataclasses import dataclass
from typing import Any, Iterable

import requests

FOURTU_ARTICLE_API = "https://data.4tu.nl/v2/articles/{uuid}"
FOURTU_IIIF_MANIFEST_API = "https://data.4tu.nl/iiif/v3/{uuid}/1/manifest"

DEFAULT_FIELDS = [
    "resource_title",
    "resource_doi",
    "categories",
    "description",
    "time_coverage",
    "derived_from",
    "geolocation",
]

FIELD_LABELS = {
    "resource_title": "Resource title",
    "resource_doi": "Resource DOI",
    "categories": "Categories",
    "description": "Description",
    "time_coverage": "Time coverage",
    "derived_from": "Derived From",
}

CUSTOM_FIELD_NAMES = {
    "time_coverage": "Time coverage",
    "derived_from": "Derived From",
    "geo_lon": "Geolocation Longitude",
    "geo_lat": "Geolocation Latitude",
}


@dataclass
class EnrichmentResult:
    manifest: dict[str, Any]
    added_metadata: list[dict[str, Any]]
    nav_place_added: bool
    warnings: list[str]


def fetch_dataset_metadata(uuid: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch dataset/article metadata from the 4TU.ResearchData v2 API."""
    url = FOURTU_ARTICLE_API.format(uuid=uuid)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_iiif_manifest(uuid: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch the IIIF Presentation API v3 manifest for a 4TU dataset UUID."""
    url = FOURTU_IIIF_MANIFEST_API.format(uuid=uuid)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def clean_html_description(description_html: str | None) -> str:
    """Remove basic HTML tags and decode common HTML entities."""
    if not description_html:
        return ""
    text = re.sub(r"<[^>]+>", "", description_html)
    text = html.unescape(text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def get_custom_field(dataset: dict[str, Any], field_name: str) -> Any:
    """Return the value of a 4TU custom field by name, or None."""
    for field in dataset.get("custom_fields") or []:
        if field.get("name") == field_name:
            return field.get("value")
    return None


def as_text(value: Any) -> str:
    """Normalize API values to a human-readable string for IIIF metadata."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "; ".join(str(item) for item in value if item is not None).strip()
    return str(value).strip()


def make_language_map_metadata(label: str, value: str, lang: str = "en") -> dict[str, Any]:
    return {"label": {lang: [label]}, "value": {lang: [value]}}


def build_metadata_entries(
    dataset: dict[str, Any],
    selected_fields: Iterable[str],
    lang: str = "en",
) -> list[dict[str, Any]]:
    """Build IIIF metadata entries from selected 4TU dataset fields."""
    selected = set(selected_fields)
    entries: list[dict[str, Any]] = []

    if "resource_title" in selected:
        value = as_text(dataset.get("resource_title"))
        if value:
            entries.append(make_language_map_metadata(FIELD_LABELS["resource_title"], value, lang))

    if "resource_doi" in selected:
        value = as_text(dataset.get("resource_doi"))
        if value:
            entries.append(make_language_map_metadata(FIELD_LABELS["resource_doi"], value, lang))

    if "categories" in selected:
        categories = dataset.get("categories") or []
        titles = sorted({cat.get("title") for cat in categories if cat.get("title")})
        value = "; ".join(titles)
        if value:
            entries.append(make_language_map_metadata(FIELD_LABELS["categories"], value, lang))

    if "description" in selected:
        value = clean_html_description(dataset.get("description"))
        if value:
            entries.append(make_language_map_metadata(FIELD_LABELS["description"], value, lang))

    if "time_coverage" in selected:
        value = as_text(get_custom_field(dataset, CUSTOM_FIELD_NAMES["time_coverage"]))
        if value:
            entries.append(make_language_map_metadata(FIELD_LABELS["time_coverage"], value, lang))

    if "derived_from" in selected:
        value = as_text(get_custom_field(dataset, CUSTOM_FIELD_NAMES["derived_from"]))
        if value:
            entries.append(make_language_map_metadata(FIELD_LABELS["derived_from"], value, lang))

    return entries


def metadata_label(entry: dict[str, Any], lang: str = "en") -> str:
    labels = entry.get("label", {}).get(lang) or []
    if labels:
        return str(labels[0])
    # Fallback for manifests that use another language map key.
    label_map = entry.get("label") or {}
    for values in label_map.values():
        if values:
            return str(values[0])
    return ""


def merge_metadata(
    existing: list[dict[str, Any]],
    additions: list[dict[str, Any]],
    lang: str = "en",
    overwrite: bool = False,
) -> list[dict[str, Any]]:
    """Merge metadata entries, de-duplicating by label."""
    merged = copy.deepcopy(existing or [])
    label_to_index = {metadata_label(item, lang): idx for idx, item in enumerate(merged)}

    for item in additions:
        label = metadata_label(item, lang)
        if not label:
            continue
        if label in label_to_index:
            if overwrite:
                merged[label_to_index[label]] = item
        else:
            label_to_index[label] = len(merged)
            merged.append(item)
    return merged


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None
    return None


def build_nav_place(dataset: dict[str, Any]) -> dict[str, Any] | None:
    lon = to_float(get_custom_field(dataset, CUSTOM_FIELD_NAMES["geo_lon"]))
    lat = to_float(get_custom_field(dataset, CUSTOM_FIELD_NAMES["geo_lat"]))

    if lon is None or lat is None:
        return None

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"label": {"en": ["Location"]}},
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        ],
    }


def ensure_summary_from_description(
    manifest: dict[str, Any],
    dataset: dict[str, Any],
    selected_fields: Iterable[str],
    lang: str = "en",
) -> None:
    """Set manifest summary from dataset description if summary is empty and description was selected."""
    if "description" not in set(selected_fields):
        return

    description = clean_html_description(dataset.get("description"))
    if not description:
        return

    summary = manifest.get("summary")
    if not isinstance(summary, dict):
        manifest["summary"] = {lang: [description]}
        return

    if not summary.get(lang):
        summary[lang] = [description]


def enrich_manifest(
    manifest: dict[str, Any],
    dataset: dict[str, Any],
    selected_fields: Iterable[str] = DEFAULT_FIELDS,
    lang: str = "en",
    overwrite_existing_metadata: bool = False,
    set_summary_from_description: bool = True,
) -> EnrichmentResult:
    """Return a copy of an IIIF manifest enriched with selected 4TU metadata fields."""
    selected = set(selected_fields)
    warnings: list[str] = []

    enriched = copy.deepcopy(manifest)
    additions = build_metadata_entries(dataset, selected, lang=lang)
    enriched["metadata"] = merge_metadata(
        enriched.get("metadata") or [],
        additions,
        lang=lang,
        overwrite=overwrite_existing_metadata,
    )

    if set_summary_from_description:
        ensure_summary_from_description(enriched, dataset, selected, lang=lang)

    nav_place_added = False
    if "geolocation" in selected:
        nav_place = build_nav_place(dataset)
        if nav_place:
            enriched["navPlace"] = nav_place
            nav_place_added = True
        else:
            warnings.append("No valid Geolocation Longitude/Latitude custom fields found; navPlace was not added.")

    if not additions:
        warnings.append("No selected metadata fields had values in the dataset API response.")

    return EnrichmentResult(
        manifest=enriched,
        added_metadata=additions,
        nav_place_added=nav_place_added,
        warnings=warnings,
    )
