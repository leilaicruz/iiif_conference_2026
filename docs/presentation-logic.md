
For a 15-minute talk, especially at an **IIIF conference**, you should:

* Minimize general IIIF explanation (they already know it)
* Minimize repository architecture details
* Maximize *concrete research workflows*
* Show something real (even a simple demo screenshot)

You want the audience to leave thinking:

> “This is not just IIIF in a repository — this is IIIF as research infrastructure.”

Below is a precise, time-calibrated structure.

---

# 🎯 High-Level Strategy for 15 Minutes

Total time: 15 minutes
Ideal slide count: 10–14 slides
Pacing: ~1 minute per slide

Structure:

1. The Problem (2 min)
2. What We Built (3 min)
3. Deep Dive Use Case 1 (5 min)
4. Deep Dive Use Case 2 (3 min)
5. Implications + Open Questions (2 min)

---

# 🧱 Proposed Structure

---

## 1️⃣ Slide 1 — Title (30 sec)

**Title**
IIIF as Research Infrastructure in Data-Intensive Science

Subtitle:
From collection presentation to interoperable research objects in 4TU.ResearchData

Keep it short. Move on quickly.

---

## 2️⃣ Slide 2 — The Gap (1.5 min)

Frame the problem clearly:

### IIIF is mature in:

* Cultural heritage
* Digitized collections
* Manuscripts, artworks, maps

### But research data repositories face:

* Fragmented image formats
* Bespoke lab tooling
* Weak cross-dataset interoperability
* Metadata disconnected from visual access

Key sentence:

> Scientific image datasets are stored — but rarely interoperable.

This creates tension.

---

## 3️⃣ Slide 3 — Our Positioning (1 min)

Very concise.

At 4TU.ResearchData:

* IIIF Image API deployed
* IIIF Presentation API deployed
* Python-based backend
* Integrated with repository metadata (/v2/articles endpoint)

Then state the conceptual shift:

> We treat IIIF manifests as machine-readable research objects.

Then move immediately to use cases.

---

# 🔬 USE CASE SECTION (Core of Talk)

This is where you go deep.

---

# USE CASE 1

## Aggregating Experimental Imaging Datasets

(5 minutes)

This is where your earlier idea fits perfectly.

---

### Slide 4 — The Research Context

Example:

Microscopy datasets from:

* Same lab
* Same organism
* Same marker
* Different experiments

Each dataset:

* Has images
* Has DOI
* Has metadata
* Has publication links

But they exist as isolated deposits.

Problem:

> No structured way to compare images across datasets.

---

### Slide 5 — What We Do Technically (Simple Diagram)

Keep architecture simple:

1. Query 4TU API
2. Retrieve IIIF manifests
3. Retrieve dataset metadata (/v2/articles/uuid)
4. Enrich manifest with:

   * resource_title
   * resource_doi
   * derivedFrom
   * categories
5. Generate aggregated manifest

No code. Just a conceptual diagram.

---

### Slide 6 — What This Enables

Now shift to research value.

With aggregated manifest:

Researchers can:

* Compare images across experiments
* View publication context directly in viewer
* Traverse provenance relationships
* Treat manifest as reusable object

Important conceptual move:

> The manifest becomes a curated research corpus.

That is powerful language for this audience.

---

### Slide 7 — Why This Is Different from Heritage Aggregation

In heritage:

* Aggregation = exhibition

In science:

* Aggregation = hypothesis exploration
* Aggregation = experimental comparison
* Aggregation = provenance tracing

This reframes IIIF’s purpose.

---

# USE CASE 2

## Historical Maps + Engineering Research

(3 minutes)

This gives you domain diversity.

---

### Slide 8 — Historical Maps in Engineering Research

Example:

* Digitized historical maps
* Used for spatial modeling
* Used in climate or infrastructure studies

IIIF enables:

* Tiled access
* Annotation
* Cross-institution comparison
* Integration into analysis pipelines

Important point:

> IIIF becomes a bridge between cultural heritage and scientific modeling.

That’s attractive for this audience.

---

# 4️⃣ Implications Section

(2 minutes)

---

## Slide 9 — IIIF as Interoperability Layer

Highlight:

* Manifests as research objects
* Repository-native IIIF
* API-driven generation
* Machine-actionable structure
* FAIR interoperability

Connect explicitly to FAIR:

* I → standardized API
* R → structured metadata + provenance
* A → HTTP-based access

Keep this tight.

---

## Slide 10 — Open Questions for the IIIF Community

End with discussion triggers:

* How should IIIF evolve for multi-dimensional scientific images?
* How do we represent analytical derivatives?
* Should Presentation API better support scientific metadata?
* Can IIIF integrate with OME, NetCDF, or other scientific standards?

Invite collaboration.

---

# ⚖️ Time Allocation Summary

| Section                 | Time   |
| ----------------------- | ------ |
| Problem framing         | 2 min  |
| Implementation overview | 3 min  |
| Use case 1              | 5 min  |
| Use case 2              | 3 min  |
| Implications            | 2 min  |
| Total                   | 15 min |

---

# 🧠 Important Strategic Advice

At IIIF 2026, your audience will include:

* Spec contributors
* Server developers
* Heritage institutions
* Tool builders

So emphasize:

* What this demands from IIIF
* What works well already
* Where scientific workflows stress the model

Not:

* Repository promotion
* Basic FAIR explanation

---

# 🔥 Optional Enhancement

If possible, show:

* A live aggregated manifest in a viewer
  OR
* A short GIF showing:

  * Manifest enrichment
  * Metadata visible in viewer
  * Cross-dataset navigation

Visual proof makes this much stronger.


