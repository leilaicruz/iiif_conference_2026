# Use Cases for IIIF for published scientific imaging

The scope of the application of the IIIF in the context of **published** scientific images is specially for reusing purpose, quick inspection ,  for comparison across datasets, for previewing the images without the need of downloading the whole dataset, for integrating structured metadata of the datasets and the images as well as for nriching preserved images with structured annotations. 

IIIF in this context is:

- About access

- About comparison

- About FAIR exposure

- About re-interpretation and reproducibility

Since deposit happens after research completion, IIIF: cannot influence experimental design, cannot support iterative image acquisition decisions, cannot integrate with lab instrumentation workflows. Thus , **our use cases are not focused on real-time microscopy analysis, computational image segmentation pipelines, or AI model training during experimentation**. Instead, we focus on post-deposition use cases that leverage IIIF for enhanced access, comparison, and reuse of published scientific images.


Here is a clean, internally consistent rewrite of your use case under the **enrichment framing**, with terminology, architecture, and outcomes aligned.

---

# Use Case 1: Enrich IIIF Manifests of Scientific Image Datasets with Repository Metadata and Structured Annotations

## Objective

Demonstrate how IIIF Presentation API manifests generated for scientific image datasets in 4TU.ResearchData can be **systematically enriched** with:

1. Additional structured metadata retrieved via the 4TU REST API
2. Domain-relevant descriptive fields aligned with the 4TU metadata schema
3. Structured annotations derived from external sources (e.g., CSV)

This use case positions IIIF not only as a visualization layer, but as a **carrier of enriched, FAIR-aligned metadata and annotations**, improving the interpretability and reusability of individual datasets.

---

## Conceptual Framing

This is a **manifest enrichment workflow**, not a cross-dataset aggregation pipeline.

* **Scope:** Per dataset
* **Input:** Existing IIIF manifest + repository metadata + optional annotation files
* **Output:** Enriched IIIF manifest

Key idea:

- Each dataset’s IIIF manifest becomes a **self-contained, semantically richer research object**.

- The value is not in adding missing metadata, but in enabling multiple, reproducible, and user-defined semantic projections of the same dataset via IIIF manifests.

## Conceptual Architecture

**Source system:** 4TU.ResearchData API
**Processing layer:** Metadata extraction + transformation scripts (Bash/Python)
**Output layer:** Enriched IIIF Presentation 3.0 manifest

Workflow:

```
4TU API → Dataset UUID  
        ↓  
   Retrieve dataset metadata  
        ↓  
   Retrieve IIIF manifest  
        ↓  
   Metadata enrichment (4TU → IIIF)  
        ↓  
   Annotation injection (CSV → IIIF)  
        ↓  
   Enriched IIIF manifest
```



## Step 1 — Retrieve deposited datasets (e.g., from a collection)

Datasets can be retrieved via a collection or author endpoint:

```bash
curl "https://data.4tu.nl/v2/collections/<collection-uuid>/articles" | jq
```

This returns:

* Dataset UUID
* Title
* DOI
* Author and publication metadata



## Step 2 — Extract dataset UUIDs

```bash
curl "https://data.4tu.nl/v2/collections/<collection-uuid>/articles" \
  | jq '.[].id'
```

These identifiers are used to drive downstream processing.



## Step 3 — Retrieve dataset-level metadata

```bash
curl "https://data.4tu.nl/v2/articles/<dataset-uuid>" | jq
```

This provides:

* Descriptive metadata (title, description, keywords)
* Authors and affiliations
* Publication details
* Custom metadata fields (e.g., geolocation, time coverage)
* File listings



## Step 4 — Retrieve the IIIF Manifest

```bash
curl -X GET "https://data.4tu.nl/iiif/v3/<dataset-uuid>/1/manifest" \
  | jq > manifest_<dataset-uuid>.json
```

The base manifest typically includes:

* Canvases (images)
* Technical image metadata
* Basic descriptive metadata



## Step 5 — Enrich the IIIF Manifest with Repository Metadata

Selected metadata fields from the 4TU API are mapped and injected into the manifest.

Typical fields include:

* Title
* Authors
* Keywords
* Categories
* Related publications (DOI, title)
* Temporal coverage
* Geospatial metadata
* Provenance fields (e.g., “derived from”)

Example enrichment step:

```bash
./inject_metadata.sh <dataset_uuid> \
  manifest_<dataset_uuid>.json \
  manifest_enriched_<dataset_uuid>.json
```

### Result

The enriched manifest:

* Aligns IIIF metadata with repository metadata
* Improves semantic completeness
* Enhances machine readability and FAIR exposure



## Step 6 — Inject Structured Annotations from CSV

Annotations can be programmatically added using a structured CSV file.

### CSV format

```csv
canvas_label,text,xywh,motivation,lang
Image 1,Yeast nucleus marker detected,100,150,200,200,describing,en
```

| Field          | Description                                 |
| -------------- | ------------------------------------------- |
| `canvas_label` | Target canvas                               |
| `text`         | Annotation content                          |
| `xywh`         | Region selector (x,y,width,height)          |
| `motivation`   | IIIF motivation (e.g., describing, tagging) |
| `lang`         | Language code                               |

### Injection step

```bash
./annotations/inject_inline_annotations.py \
  manifest_<dataset_uuid>.json \
  annotations_<dataset_uuid>.csv \
  manifest_enriched_<dataset_uuid>.json
```

### Result

* Region-specific annotations embedded in the manifest
* Supports interpretation, reuse, and domain-specific insights



## Step 7 — Publish the Enriched IIIF Manifest

The final output is a **standalone enriched IIIF manifest** that:

* Can be loaded in any IIIF-compatible viewer
* Encapsulates both image data and rich metadata
* Includes structured annotations



## Relevance

This enrichment workflow enables:

### 1. Improved FAIR Exposure

* Metadata becomes explicitly structured and embedded
* Enhances interoperability and machine-actionability

### 2. Enhanced Data Reuse

* Users can interpret datasets without consulting external metadata systems
* Context travels with the manifest

### 3. Semantic Alignment

* Bridges repository metadata (4TU schema) and IIIF Presentation model
* Reduces metadata fragmentation

### 4. Annotation-Driven Interpretation

* Supports domain-specific insights (e.g., microscopy features)
* Enables reproducibility of observations



This use case demonstrates how IIIF can function as a **metadata integration layer at the dataset level**, strengthening the FAIRness and usability of published scientific images. The the manifest could include all this metadata from the start, but the added value of this approach lies in decoupling, flexibility, and user-driven reinterpretation after deposition.



## Use case 2 : (Reinterpretation and reproducibility) Image analysis after deposition (no local copies): fetch, preview, and analyze images on-the-fly. 

This use case shows a research-workflow for working with deposited image datasets exposed via **IIIF Presentation API v3** (manifests served by 4TU.ResearchData) and the **IIIF Image API** (derivatives, regions, sizes).

Key ideas:

- Use the **manifest** to discover canvases (pages/frames) and their associated **Image API service**.
- Request **only the pixels you need** (thumbnail, region, or downsampled version) using Image API URL parameters.
- Perform lightweight imaging analysis in-memory (NumPy arrays) without downloading full-resolution originals.

See [this notebook](iiif/scripts/iiif-python-refined.ipynb) for a demonstration of this workflow using Python libraries like `requests` and `PIL` to fetch and analyze IIIF-served images on-the-fly.

- Environment installation

```bash

python -m venv iiif-env
source iiif-env/bin/activate
pip install -r iiif/scripts/requirements.txt

```