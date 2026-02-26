# Use Cases for IIIF for published scientific imaging

The scope of the application of the IIIF in the context of **published** scientific images is specially for reusing purpose, quick inspection ,  for comparison across datasets, for previewing the images without the need of downloading the whole dataset, for integrating structured metadata of the datasets and the images as well as for nriching preserved images with structured annotations. 

IIIF in this context is:

- About access

- About comparison

- About FAIR exposure

- About re-interpretation and reproducibility

Since deposit happens after research completion, IIIF: cannot influence experimental design, cannot support iterative image acquisition decisions, cannot integrate with lab instrumentation workflows. Thus , **our use cases are not focused on real-time microscopy analysis, computational image segmentation pipelines, or AI model training during experimentation**. Instead, we focus on post-deposition use cases that leverage IIIF for enhanced access, comparison, and reuse of published scientific images.


##  Case 1 : Aggregate metadata from scientific image datasets and expose it through IIIF Manifests for comparison and reuse

### Objective

Demonstrate how metadata from multiple scientific image datasets (e.g., microscopy images) stored in 4TU.ResearchData can be:

1. Programmatically harvested via the REST API
2. Aggregated across datasets
3. Embedded or referenced in IIIF Presentation API manifests
4. Used for cross-dataset comparison and reuse in IIIF-compatible viewers

This use case illustrates IIIF not merely as a visualization layer, but as an interoperability layer connecting distributed research datasets.

## Conceptual Architecture

**Source system:** 4TU.ResearchData API
**Intermediate layer:** Custom Bash processing / aggregation
**Output layer:** IIIF Presentation 3.0 manifest

Workflow logic:

4TU API → Dataset UUIDs → Individual IIIF Manifests
          ↓
     Metadata aggregation
          ↓
     Annotation enrichment (CSV → IIIF)
          ↓
     Aggregated IIIF Manifest

---

## Step 1 — Retrieve deposited datasets , e.g. from a collection (or author) 

Datasets in 4TU.ResearchData are grouped under:

* A **Collection UUID**
* An **Author (profile) UUID**

To retrieve all datasets in a collection:

```bash
curl "https://data.4tu.nl/v2/collections/de8ea9d4-f986-41fc-9412-6765985a0c9c/articles" | jq
```

This returns a JSON array containing:

* Dataset UUID
* Title
* DOI
* Author metadata
* Publication metadata

Each dataset has a unique identifier (`id` or `uuid`) which can be used to retrieve detailed metadata and associated files.


## Step 2 — Extract dataset UUIDs

From the JSON response, extract the dataset identifiers:

Example (conceptually):

```bash
curl "https://data.4tu.nl/v2/collections/<collection-uuid>/articles" \
  | jq '.[].id'
```

You now have a list of dataset UUIDs.


## Step 3 — Retrieve dataset-level metadata

For each dataset UUID:

```bash
curl "https://data.4tu.nl/v2/articles/<dataset-uuid>" | jq
```

This returns:

* Full metadata record
* File listing
* Author information
* Keywords
* Descriptions
* Publication dates


## Step 4 — Retrieve the IIIF Manifest for each dataset

If IIIF is enabled for the dataset, the manifest can be retrieved via:

```bash
curl -X GET "https://data.4tu.nl/iiif/v3/<dataset-uuid>/1/manifest" | jq  > manifest_<dataset-uuid>.json
```

This manifest typically contains:

* Canvas entries for each image
* Technical image metadata
* Dataset-level descriptive metadata


## Step 5 — Aggregate metadata across datasets

At this stage, you can extract selected metadata fields taken from `/v2/articles/<dataset-uuid>` endpoint such as:

* Title
* Authors
* Keywords
* Categories
* Related publications (DOI, title)
* Time coverage
* Geolocation (if available in custom fields)
* Derived from (if available)

Then the agregated metadata can be injected into the manifest of each dataset :

```bash

./inject_metadata.sh <dataset_uuid> manifest_<dataset_uuid>.json manifest_enriched_<dataset_uuid>.json

```

## Step 6 - Injecting structured annotations from CSV

In addition to metadata aggregation, annotations can be programmatically added to a IIIF manifest using a structured CSV file. The CSV file must follow this structure: ```canvas_label,text,xywh,motivation,lang```
Where:

| Field          | Description                                                         |
| -------------- | ------------------------------------------------------------------- |
| `canvas_label` | Label of the canvas to which the annotation applies                 |
| `text`         | Annotation body text                                                |
| `xywh`         | Region selector (pixel coordinates) formatted as `x,y,width,height` |
| `motivation`   | IIIF motivation (e.g., `commenting`, `describing`, `tagging`)       |
| `lang`         | Language code (e.g., `en`, `nl`)                                    |

Example:

```csv
canvas_label,text,xywh,motivation,lang
Image 1,Yeast nucleus marker detected,100,150,200,200,describing,en
```
- Inject Annotations into a Manifest

Use the provided script:

```bash

./annotations/inject_inline_annotations.py manifest_<dataset_uuid>.json annotations_<dataset_uuid>.csv manifest_enriched_<dataset_uuid>.json

```

## Step 7 — Publish an aggregated IIIF Manifest

The aggregated manifest acts as:

* A research object
* A curated comparison layer
* A reusable interoperability artifact

## Relevance

By programmatically harvesting metadata and embedding it into IIIF manifests, we:

* Enable structured comparison
* Preserve provenance
* Support FAIR reuse
* Turn IIIF into a research infrastructure component


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