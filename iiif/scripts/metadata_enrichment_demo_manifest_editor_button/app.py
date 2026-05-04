from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from metadata_enrichment.enrich_manifest import (
    DEFAULT_FIELDS,
    FIELD_LABELS,
    build_metadata_entries,
    enrich_manifest,
    fetch_dataset_metadata,
    fetch_iiif_manifest,
    metadata_label,
)
from metadata_enrichment.iiif_image_analysis import (
    analyze_brightness,
    analyze_central_region_edges,
    canvases_with_image_services,
    fetch_thumbnail_grid,
    get_canvas_label,
)

st.set_page_config(page_title="IIIF Metadata Enrichment Demo", layout="wide")

FIELD_HELP = {
    "resource_title": "Adds the dataset resource_title as IIIF metadata.",
    "resource_doi": "Adds the dataset DOI as IIIF metadata.",
    "categories": "Adds unique category titles from the dataset metadata.",
    "description": "Adds a cleaned plain-text version of the dataset description.",
    "time_coverage": "Adds the custom field named 'Time coverage'.",
    "derived_from": "Adds the custom field named 'Derived From'.",
    "geolocation": "Adds navPlace from Geolocation Longitude and Geolocation Latitude custom fields.",
}


def metadata_to_dataframe(metadata: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for item in metadata or []:
        label = metadata_label(item)
        value_map = item.get("value") or {}
        values = value_map.get("en") or next(iter(value_map.values()), []) if value_map else []
        value = "; ".join(str(v) for v in values) if isinstance(values, list) else str(values)
        rows.append({"label": label, "value": value})
    return pd.DataFrame(rows)


def show_manifest_summary(manifest: dict[str, Any]) -> None:
    st.write("**Manifest label**")
    st.json(manifest.get("label", {}), expanded=False)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Canvases", len(manifest.get("items") or []))
    col_b.metric("Metadata entries", len(manifest.get("metadata") or []))
    col_c.metric("Has navPlace", "yes" if "navPlace" in manifest else "no")


def read_uploaded_manifest(uploaded_file) -> dict[str, Any]:
    return json.loads(uploaded_file.getvalue().decode("utf-8"))

def extract_thumbnail_urls(manifest, max_items=12, size=128):
    if not isinstance(manifest, dict):
        return []

    urls = []

    for item in manifest.get("items", [])[:max_items]:
        label_obj = item.get("label", {})
        label = (
            label_obj.get("en", ["Untitled canvas"])[0]
            if isinstance(label_obj, dict)
            else "Untitled canvas"
        )

        try:
            body = item["items"][0]["items"][0]["body"]

            service = body.get("service", [])
            if isinstance(service, dict):
                service_id = service.get("id") or service.get("@id")
            elif isinstance(service, list) and service:
                service_id = service[0].get("id") or service[0].get("@id")
            else:
                service_id = None

            if service_id:
                thumb_url = f"{service_id}/full/!{size},{size}/0/default.jpg"
                urls.append((label, thumb_url))
                continue

            body_id = body.get("id")
            if body_id:
                urls.append((label, body_id))

        except Exception:
            continue

    return urls


st.title("IIIF Manifest Metadata Enrichment Demo")
st.caption("Fetch or upload a IIIF manifest, select 4TU metadata fields, enrich the manifest, run lightweight image analysis, and export the result.")

with st.sidebar:
    st.header("Input")
    source_mode = st.radio(
        "Manifest source",
        ["Fetch from dataset UUID", "Upload manifest JSON"],
    )

    dataset_uuid = st.text_input("4TU dataset UUID", placeholder="e.g. de8ea9d4-f986-41fc-9412-6765985a0c9c")
    uploaded_manifest = None
    if source_mode == "Upload manifest JSON":
        uploaded_manifest = st.file_uploader("Upload manifest JSON", type=["json"])

    st.header("Fields to add")
    selected_fields = []
    for field in DEFAULT_FIELDS:
        label = FIELD_LABELS.get(field, "Geolocation / navPlace")
        if st.checkbox(label, value=True, help=FIELD_HELP[field]):
            selected_fields.append(field)

    st.header("Options")
    overwrite = st.checkbox("Overwrite existing metadata labels", value=False)
    set_summary = st.checkbox("Set summary from description if empty", value=True)
    lang = st.text_input("IIIF language code", value="en")

    run_button = st.button("Run enrichment", type="primary")

    st.header("Image analysis demo")
    max_analysis_canvases = st.slider("Canvases to analyze", min_value=1, max_value=30, value=8)
    derivative_size = st.selectbox("Analysis derivative size", ["!128,128", "!256,256", "!512,512"], index=1)
    show_thumbnails = st.checkbox("Show thumbnail gallery", value=True)
    run_image_analysis = st.button("Analyze images in Python")

manifest: dict[str, Any] | None = None
dataset: dict[str, Any] | None = None

st.subheader("Load manifest and dataset metadata")

if source_mode == "Fetch from dataset UUID":
    if dataset_uuid:
        try:
            with st.spinner("Fetching IIIF manifest and dataset metadata from 4TU.ResearchData..."):
                manifest = fetch_iiif_manifest(dataset_uuid)
                dataset = fetch_dataset_metadata(dataset_uuid)
            st.success("Fetched manifest and dataset metadata.")
        except Exception as exc:
            st.error(f"Could not fetch data for UUID {dataset_uuid}: {exc}")
    else:
        st.info("Enter a dataset UUID in the sidebar to fetch a manifest and dataset metadata.")
else:
    if uploaded_manifest is not None:
        try:
            manifest = read_uploaded_manifest(uploaded_manifest)
            st.success("Uploaded manifest loaded.")
        except Exception as exc:
            st.error(f"Could not parse uploaded manifest JSON: {exc}")

        if dataset_uuid:
            try:
                with st.spinner("Fetching dataset metadata from 4TU.ResearchData..."):
                    dataset = fetch_dataset_metadata(dataset_uuid)
                st.success("Fetched dataset metadata.")
            except Exception as exc:
                st.error(f"Could not fetch dataset metadata for UUID {dataset_uuid}: {exc}")
        else:
            st.info("For enrichment, also enter the dataset UUID so the app can fetch the /v2/articles/{uuid} metadata.")
    else:
        st.info("Upload a manifest JSON file and enter the corresponding dataset UUID.")

if manifest:
    with st.expander("Original manifest overview", expanded=True):
        show_manifest_summary(manifest)
        st.dataframe(metadata_to_dataframe(manifest.get("metadata") or []), use_container_width=True)

if dataset:
    with st.expander("Dataset API response preview", expanded=False):
        st.json(dataset, expanded=False)

    with st.expander("Metadata entries that would be added", expanded=True):
        preview_entries = build_metadata_entries(dataset, selected_fields, lang=lang)
        st.dataframe(metadata_to_dataframe(preview_entries), use_container_width=True)
        if "geolocation" in selected_fields:
            st.caption("Geolocation is added as IIIF navPlace, not as a regular metadata row.")

if isinstance(manifest, dict):
    st.header("Image thumbnails from the manifest")

    thumbnail_urls = extract_thumbnail_urls(manifest, size=128)

    if not thumbnail_urls:
        st.warning("No image URLs could be extracted from this manifest.")
    else:
        cols = st.columns(4)

        for index, (label, url) in enumerate(thumbnail_urls):
            with cols[index % 4]:
                st.image(url, caption=label, use_container_width=True)
else:
    st.info("Load or upload a manifest to preview image thumbnails.")

st.subheader("Analyze images in Python")

st.markdown("""
This demo shows how IIIF image derivatives can be requested directly from the manifest
and analyzed in Python without manually downloading the original image files.

The current analysis performs two simple operations:

1. **Brightness / intensity summary**
   - The app requests a downsampled version of each canvas image.
   - It converts the image to grayscale.
   - It calculates the mean pixel intensity.
   - Higher values indicate a brighter image; lower values indicate a darker image.

2. **Edge detection demo**
   - The app selects one canvas image.
   - It applies a Sobel edge filter to highlight sharp intensity changes.
   - This can reveal object boundaries, cell edges, texture, or other structural features.

This is not intended as a full scientific image-analysis workflow.
It is a small proof of concept showing that image-processing functionality can later be
embedded into the repository.
""")

if manifest:
    image_canvases = canvases_with_image_services(manifest)
    st.write(
        f"Found **{len(image_canvases)}** canvas/canvases with IIIF Image API services. "
        "The demo requests downsampled IIIF derivatives and analyzes them in memory."
    )

    if image_canvases:
        canvas_options = [get_canvas_label(canvas) or f"Canvas {i}" for i, canvas in enumerate(image_canvases)]
        selected_canvas_label = st.selectbox("Select an image for the edge-detection preview", canvas_options)
        selected_canvas_index = canvas_options.index(selected_canvas_label)
    else:
        selected_canvas_index = 0

    if run_image_analysis:
        if not image_canvases:
            st.error("No IIIF Image API services were found in this manifest.")
        else:
            try:
                with st.spinner("Fetching IIIF derivatives and running lightweight Python image analysis..."):
                    brightness_results = analyze_brightness(
                        manifest,
                        max_canvases=max_analysis_canvases,
                        derivative_size=derivative_size,
                    )
                    region_url, region_img, edge_img = analyze_central_region_edges(
                        manifest,
                        canvas_index=selected_canvas_index,
                    )
                    thumbnails = fetch_thumbnail_grid(manifest, max_canvases=8) if show_thumbnails else []

                st.success("Image analysis completed.")

                if thumbnails:
                    st.write("**Thumbnail preview from IIIF Image API derivatives**")
                    thumb_cols = st.columns(4)
                    for i, (label, image) in enumerate(thumbnails):
                        with thumb_cols[i % 4]:
                            st.image(image, caption=label, use_container_width=True)

                st.write("**Mean brightness by canvas**")
                brightness_df = pd.DataFrame(
                    [
                        {
                            "canvas_index": item.index,
                            "label": item.label,
                            "brightness": item.brightness,
                            "image_url": item.image_url,
                        }
                        for item in brightness_results
                    ]
                )
                st.dataframe(brightness_df, use_container_width=True)
                if not brightness_df.empty:
                    st.line_chart(brightness_df.set_index("canvas_index")["brightness"])

                st.write("**Full-image edge demo**")
                col_region, col_edges = st.columns(2)
                with col_region:
                    st.image(region_img, caption="Requested full image derivative", use_container_width=True)
                with col_edges:
                    st.image(edge_img, caption="Sobel edge magnitude", use_container_width=True)
                st.caption(f"IIIF Image API URL used: {region_url}")

            except Exception as exc:
                st.error(f"Image analysis failed: {exc}")
else:
    st.info("Load a manifest first to enable the image-analysis demo.")

st.subheader("Enrich manifest")



if run_button:
    if not manifest:
        st.error("No manifest loaded.")
    elif not dataset:
        st.error("No dataset metadata loaded. Enter a valid dataset UUID.")
    elif not selected_fields:
        st.error("Select at least one field to add.")
    else:
        result = enrich_manifest(
            manifest=manifest,
            dataset=dataset,
            selected_fields=selected_fields,
            lang=lang,
            overwrite_existing_metadata=overwrite,
            set_summary_from_description=set_summary,
        )

        st.success("Manifest enriched.")
        if result.warnings:
            for warning in result.warnings:
                st.warning(warning)

        left, right = st.columns(2)
        with left:
            st.write("**Added metadata**")
            st.dataframe(metadata_to_dataframe(result.added_metadata), use_container_width=True)
            st.write(f"**navPlace added:** {'yes' if result.nav_place_added else 'no'}")

        with right:
            st.write("**Enriched manifest overview**")
            show_manifest_summary(result.manifest)

        st.subheader("4. Export")
        enriched_json = json.dumps(result.manifest, indent=2, ensure_ascii=False)
        st.download_button(
            label="Download enriched manifest JSON",
            data=enriched_json,
            file_name=f"enriched_manifest_{dataset_uuid or 'uploaded'}.json",
            mime="application/json",
        )

        with st.expander("View enriched manifest JSON", expanded=False):
            st.code(enriched_json, language="json")

        
else:
    st.info("Choose fields in the sidebar, then run enrichment.")

st.subheader("Preview in Digirati Manifest Editor")
st.write(
    "Open the editor from here at any point. "
    "If your manifest is only local or uploaded in this dashboard, first download it and then upload/import it in the editor."
)
st.link_button(
    "Open Digirati Manifest Editor",
    "https://manifest-editor.digirati.services/?tab=recent",
    type="primary"
)

if dataset_uuid:
    source_manifest_url = f"https://data.4tu.nl/iiif/v3/{dataset_uuid}/1/manifest"
    st.caption(
        "Source manifest URL. This points to the original 4TU manifest, not the enriched local JSON:"
    )
    st.code(source_manifest_url, language="text")