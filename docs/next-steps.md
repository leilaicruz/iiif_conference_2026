- Look for uses cases within the microscopy field that would like to use IIIF to share their data.

"We present concrete use cases from ongoing research at Delft University of Technology, focusing on experimental imaging datasets and historical maps. In these cases, IIIF manifests function as machine-readable research objects that organize images, metadata, and structural relationships in a way that supports downstream reuse. We envision that researchers could compare datasets across experiments, aggregate images from multiple sources, and enrich data through annotations that are relevant for scientific interpretation ."

- possible authors: Olha MAIKOVYCH and Felix Dahle

https://data.4tu.nl/authors/fea320e2-8b69-405d-9629-ee001f2d26b4
https://data.4tu.nl/authors/609650c6-743c-4d13-9d3f-18b9c8525589

- check https://systemik-solutions.github.io/Glycerine_Guide/intro.html ,  Image Annotation Workbench

## Use case : agregate manifests from multiple datasets of one collection or one author in order to create manifest of a collection of images that can be used for comparison or reuse.


- Use the api to download manifests of a collection or images from the same author .
- Add information of categories, related publications (resource_title and resource_doi) and derived from (custom_fields) in the metadata of the manifest (so it is shown in the viewer, so far is not shown with the current implementation of the manifest) from the metadata of the datasets taken from /v2/articles/uuid endpoint.
- Use a simple python script that can create a new manifest that aggregates the images and metadata from the downloaded manifests.
- Make a shareable exhibition with the aggregated manifest that can be used for comparison or reuse.


### Analysis of the use case 

Your idea is strategically strong. You are repositioning IIIF from a *presentation framework for cultural heritage* to an *interoperability layer for scientific image collections*. That is conceptually sound — but it needs careful validation against actual researcher workflows.

I will structure this in three parts:

1. Critical analysis of your idea
2. Questions you should clarify before approaching researchers
3. A draft email you can send to microscopy researchers

---

# 1️⃣ Critical Assessment of Your Use Case

## Conceptual Strengths

### 1. IIIF as a FAIR Enabler for Image Data

IIIF natively provides:

* Persistent image addressing
* Standardized metadata structure
* Deep zoom (important for microscopy)
* API-based access
* Interoperability across viewers

For microscopy datasets, this aligns strongly with:

* Reusability
* Comparability
* Cross-dataset aggregation
* Visual reproducibility

Your idea of aggregating manifests across:

* One author
* One collection
* One research project
* Or even one biological condition

is technically feasible and conceptually powerful.

---

## 🔍 Where You Need to Be Critical

### 1. Are Researchers Actually Comparing Images Visually?

In digital humanities, IIIF is useful because visual comparison is central.

In microscopy:

* Many researchers extract quantitative data (segmentation, intensity values, features)
* Images are often intermediate data
* Reuse often means *analysis reuse*, not visual reuse

You must verify:

> Do they actually need cross-dataset visual comparison in a viewer?

If not, the value proposition must shift toward:

* Metadata harmonization
* Dataset discoverability
* Structured linking between images and publications
* Provenance tracking

---

### 2. Scale and Technical Constraints

Microscopy datasets can be:

* Multi-channel
* Multi-dimensional (z-stacks, time series)
* Stored in OME-TIFF or proprietary formats

Questions:

* Does current IIIF implementation in 4TU handle multi-dimensional images?
* Are you only exposing 2D rendered derivatives?
* Are you losing scientific metadata when converting?

If scientific metadata is stripped during manifest creation, researchers may not consider it serious infrastructure.

---

### 3. Metadata Enrichment — Very Strong Idea

Your idea to enrich manifests with:

* Categories
* Related publications (resource_title, resource_doi)
* Derived-from relationships
* Custom fields

is actually the strongest part of your proposal.

This transforms IIIF from:

> “viewer for images”

into:

> “interoperable research object aggregator”

That is highly aligned with FAIR principles.

---

### 4. Aggregated Manifest as "Exhibition"

The term “exhibition” may resonate poorly with scientists.

Better framing:

* Comparative research collection
* Image corpus
* Research dataset aggregation
* Curated visual dataset
* Thematic image collection

Language matters.

---

# 2️⃣ Questions You Should Clarify Before Testing

When you speak with researchers, try to validate:

### A. Discovery

* Do you ever want to browse all microscopy images from a specific author or lab?
* Would it help if images across datasets could be aggregated automatically?

### B. Comparison

* Do you visually compare images across experiments?
* Would a browser-based deep zoom comparison tool help?

### C. Metadata

* Is the current metadata in the repository sufficient?
* Would it help to have publication links and derived relationships directly visible in a viewer?

### D. Reuse

* When reusing microscopy data, what is your main entry point?

  * Raw files?
  * Processed images?
  * Quantitative tables?
  * Publications?

### E. Infrastructure Gaps

* What is currently frustrating about image reuse?
* How do you currently share microscopy images?

You are not testing whether IIIF works technically.
You are testing whether it solves a real friction point.

---



# Strategic Advice

When you talk to researchers:

Do NOT pitch IIIF.

Pitch:

* Easier comparison
* Better visibility
* Better linking between data and publications
* Less friction in reuse

IIIF is the technical layer.
Researchers care about workflow efficiency.

