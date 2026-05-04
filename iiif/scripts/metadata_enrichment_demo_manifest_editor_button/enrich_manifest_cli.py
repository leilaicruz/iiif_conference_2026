#!/usr/bin/env python3
"""CLI wrapper for enriching a 4TU IIIF manifest.

Example:
    python enrich_manifest_cli.py \
      --uuid de8ea9d4-f986-41fc-9412-6765985a0c9c \
      --manifest-in manifest.json \
      --manifest-out enriched_manifest.json \
      --fields resource_title resource_doi categories description time_coverage derived_from geolocation
"""

from __future__ import annotations

import argparse

from metadata_enrichment.enrich_manifest import (
    DEFAULT_FIELDS,
    enrich_manifest,
    fetch_dataset_metadata,
    load_json,
    save_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich a IIIF manifest with 4TU.ResearchData metadata.")
    parser.add_argument("--uuid", required=True, help="4TU dataset/article UUID")
    parser.add_argument("--manifest-in", required=True, help="Input IIIF manifest JSON path")
    parser.add_argument("--manifest-out", required=True, help="Output enriched IIIF manifest JSON path")
    parser.add_argument(
        "--fields",
        nargs="+",
        default=DEFAULT_FIELDS,
        choices=DEFAULT_FIELDS,
        help="Fields to add to the manifest metadata/navPlace",
    )
    parser.add_argument("--lang", default="en", help="Language code for IIIF language maps")
    parser.add_argument(
        "--overwrite-existing-metadata",
        action="store_true",
        help="Replace existing manifest metadata entries with the same label",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = fetch_dataset_metadata(args.uuid)
    manifest = load_json(args.manifest_in)
    result = enrich_manifest(
        manifest=manifest,
        dataset=dataset,
        selected_fields=args.fields,
        lang=args.lang,
        overwrite_existing_metadata=args.overwrite_existing_metadata,
    )
    save_json(result.manifest, args.manifest_out)
    print(f"Wrote: {args.manifest_out}")
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
