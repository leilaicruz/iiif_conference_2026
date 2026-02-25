import csv, json, re, sys

manifest_in = sys.argv[1]
csv_in = sys.argv[2]
manifest_out = sys.argv[3]

with open(manifest_in, encoding="utf-8") as f:
    m = json.load(f)

# index canvases by label
canvas_by_label = {}
for c in m.get("items", []):
    lab = c.get("label", {})
    if isinstance(lab, dict):
        lbl = (lab.get("en") or lab.get("none") or [""])[0]
        if lbl:
            canvas_by_label[lbl] = c

def norm_xywh(x):
    if not x:
        return None
    x = x.strip()
    m = re.match(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$", x)
    if not m:
        raise ValueError(f"Invalid xywh: {x!r} (expected x,y,w,h)")
    return ",".join(m.groups())

# read CSV and inject inline
with open(csv_in, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        label = (row.get("canvas_label") or "").strip()
        text = (row.get("text") or "").strip()
        if not label or not text:
            continue

        canvas = canvas_by_label.get(label)
        if not canvas:
            # no matching canvas; skip silently (or print warning)
            continue

        motivation = (row.get("motivation") or "commenting").strip() or "commenting"
        lang = (row.get("lang") or "en").strip() or "en"
        xywh = norm_xywh(row.get("xywh") or "")

        canvas_id = canvas["id"]

        # Ensure inline AnnotationPage exists
        if "annotations" not in canvas or not isinstance(canvas["annotations"], list) or len(canvas["annotations"]) == 0:
            canvas["annotations"] = [{
                "id": canvas_id + "/annotationpage/1",
                "type": "AnnotationPage",
                "items": []
            }]

        page = canvas["annotations"][0]
        if "items" not in page or not isinstance(page["items"], list):
            page["items"] = []

        anno_id = f"{page['id']}/anno/{len(page['items'])+1}"
        target = canvas_id + (f"#xywh={xywh}" if xywh else "")

        page["items"].append({
            "id": anno_id,
            "type": "Annotation",
            "motivation": motivation,
            "body": {
                "type": "TextualBody",
                "value": text,
                "format": "text/plain",
                "language": lang
            },
            "target": target
        })

with open(manifest_out, "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)

print(f"Wrote: {manifest_out}")