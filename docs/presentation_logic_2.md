
# 🧱 SLIDES

---

## 1️⃣ Slide 1 — Title (30 sec)

**IIIF as Research Infrastructure in Data-Intensive Science**
*From repository feature to interoperable research workflows at 4TU.ResearchData*

---

## 2️⃣ Slide 2 — The Gap (1.5 min)

Skip basic IIIF explanation. Go straight to tension:

Scientific repositories struggle with:

* Heterogeneous image formats
* Dataset-level silos
* Weak interoperability across experiments
* Metadata not tightly coupled to visual access

Key message:

> Scientific image datasets are accessible, but not composable.

---

## 3️⃣ Slide 3 — Our Positioning (1 min)

At **4TU.ResearchData**:

* IIIF Image API deployed
* IIIF Presentation API deployed
* Python-based backend (Djehuty)

Conceptual shift:

> We treat IIIF manifests as *machine-actionable research objects*, not just viewers.

---

## 4️⃣ Slide 4 — Use Case 1: Enrich IIIF Manifests After Deposition


**Why ?**


### ❓ Couldn’t the manifest include all metadata from the start?

Yes — but that leads to a **static, one-size-fits-all representation** defined by the repository.

---

### ⚠️ Limitation of Default IIIF Manifests

* Fixed metadata mapping (repository-controlled)
* Optimized for **generic access**, not domain-specific use
* Cannot anticipate all future reuse scenarios
* Hard to evolve without changing the repository infrastructure

---

### ✅ Added Value of Post-Deposition Enrichment

#### 1. **User-defined metadata projection**

* Select only relevant fields (e.g., microscopy vs. provenance)
* Tailor manifests to specific research questions

#### 2. **Late-binding of semantics**

* Integrate improved metadata *after publication*
* Align with evolving standards and domain ontologies

#### 3. **Reproducible transformation**

* Enrichment pipelines (scripts) make changes transparent
* Enables sharing and reuse of transformation logic

#### 4. **Decoupled architecture**

* Repository = source of truth
* IIIF = flexible interoperability layer
* Users build custom representations without modifying datasets

 message: 
> IIIF manifests are not just outputs — they can be **recomputed, enriched, and repurposed as dynamic research objects**.


---

# 🧱 Slide 5 — Workflow (demo)

> We programmatically aggregate IIIF manifests and enrich them with repository metadata to enable cross-dataset comparison.


### Workflow 

1. **Discover datasets**

   * Query collection or author via repository API
     (`/v2/collections/{id}/articles`)

2. **Retrieve manifests**

   * For each dataset UUID → fetch IIIF Presentation manifest
     (`/iiif/v3/{uuid}/manifest`)

3. **Retrieve rich metadata**

   * Query `/v2/articles/{uuid}` endpoint

4. **Inject metadata into manifest**
   Add fields not exposed in default manifests:

   * categories
   * related publications (`resource_title`, `resource_doi`)
   * provenance (`derivedFrom`)
   * temporal coverage
   * geolocation (custom fields)

5. **Output**

   * Enriched, comparable IIIF manifests


---





# Slide 7: IIIF manifest enabling analysis after deposition

Use case 2 : (Reinterpretation and reproducibility) Image analysis after deposition (no local copies): fetch, preview, and analyze images on-the-fly. 

This use case shows a research-workflow for working with deposited image datasets exposed via **IIIF Presentation API v3** (manifests served by 4TU.ResearchData) and the **IIIF Image API** (derivatives, regions, sizes).

Key ideas:

- Use the **manifest** to discover canvases (pages/frames) and their associated **Image API service**.
- Request **only the pixels you need** (thumbnail, region, or downsampled version) using Image API URL parameters.
- Perform lightweight imaging analysis in-memory (NumPy arrays) without downloading full-resolution originals.

See [this notebook](iiif/scripts/iiif-python-refined.ipynb) for a demonstration of this workflow using Python libraries like `requests` and `PIL` to fetch and analyze IIIF-served images on-the-fly.



# Slide 8 — From scripting to services : IIIF Manifest Builder Interface and Image analysis computational environment





## 8️⃣ Slide 9 — Performance & System Challenges (2 min)


### Problem Areas

* High request frequency (tile-based access)
* Large image sizes (microscopy scale)
* Dynamic manifest generation overhead
* API chaining latency (repository + IIIF)

## Slide 10: What's next 



* How should IIIF evolve for **multi-dimensional scientific data**?
* How do we represent **analytical derivatives and transformations**?
* Can Presentation API better support **scientific metadata schemas**?

Closing line:

> If IIIF is to support science at scale, it must evolve from presentation layer to computational infrastructure.








