# IIIF Metadata Enrichment Demo

A minimal Streamlit dashboard and Python module for enriching 4TU.ResearchData IIIF manifests with selected dataset metadata from the `/v2/articles/{uuid}` endpoint.

The dashboard also includes a small image-analysis demo based on `iiif-python-refined.ipynb`: it discovers IIIF Image API services from the manifest, requests downsampled derivatives, computes thumbnail-derived brightness scores, and runs a simple Sobel edge-magnitude demo on a downsampled full-image derivative.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run dashboard

```bash
streamlit run app.py
```

## Run CLI

```bash
python enrich_manifest_cli.py \
  --uuid <dataset_uuid> \
  --manifest-in manifest.json \
  --manifest-out enriched_manifest.json \
  --fields resource_title resource_doi categories description time_coverage derived_from geolocation
```

## Dashboard workflow

1. Fetch a manifest from a 4TU dataset UUID or upload a manifest JSON.
2. Fetch the corresponding `/v2/articles/{uuid}` dataset metadata.
3. Select the metadata fields to inject into the IIIF manifest.
4. Optionally run lightweight Python image analysis from IIIF Image API derivatives.
5. Download the enriched manifest JSON.

## Metadata fields

- `resource_title`
- `resource_doi`
- `categories`
- `description`
- `time_coverage`
- `derived_from`
- `geolocation`

## Image-analysis demo

The image-analysis code lives in:

```text
metadata_enrichment/iiif_image_analysis.py
```

It is intentionally separated from `app.py` so the same functions can later be reused in scripts, notebooks, tests, or repository workflows.

Current analysis examples:

- preview thumbnails using IIIF Image API derivatives
- compute mean brightness from downsampled canvas images
- request the full image region with `full`, downsampled to keep the demo lightweight
- compute Sobel edge magnitude using NumPy

This is meant as a demonstrator rather than a final scientific image-analysis pipeline.


## Previewing in the Digirati Manifest Editor

After enrichment, the Streamlit app now shows a fifth step: **Preview in Digirati Manifest Editor**.

Because the enriched manifest is generated locally in the dashboard, the app first lets you download the enriched JSON. Open the Manifest Editor button, then import/open that downloaded JSON in the editor. If you later publish the enriched manifest at a stable HTTPS URL, you can use that hosted URL directly in the editor.
