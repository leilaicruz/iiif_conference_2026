## Use case : Aggregate metadata from scientific image datasets and make it visible in the manifest for comparison and reuse

Workflow:

- Use the api to download manifests of a collection or images from the same author .
- get all the uuid of the datasets of the collection or author and then for each uuid get the manifest with the api, for example:

```
curl "https://data.4tu.nl/v2/collections/de8ea9d4-f986-41fc-9412-6765985a0c9c/articles" | jq

curl "https://data.4tu.nl/v2/articles/bcf01712-4f8d-4f12-bfc6-84fed4ddc086" | jq # microscopy images 

curl "https://data.4tu.nl/v2/articles/bc373b4b-29f1-4108-b166-85420628ff97 | jq # microscopy images 

```
- Then read the uuid of each dataset and get the manifest with the api, for example:
``` 
curl -X GET "https://data.4tu.nl/iiif/v3/uuid_1/1/manifest" | jq  > manifest_uuid1.json
curl -X GET "https://data.4tu.nl/iiif/v3/uuid_2/1/manifest" | jq  > manifest_uuid2.json

```

- Add information of categories, related publications (resource_title and resource_doi) and derived from, time coverage , geolocation(custom_fields) in the metadata of the manifest (so it is shown in the viewer, so far is not shown with the current implementation of the manifest) from the metadata of the datasets taken from /v2/articles/uuid endpoint.

```bash

./inject_metadata.sh <dataset_uuid> <manifest_in.json> <manifest_out.json>

```

- To add annotations using  csv file with the following format:

```
canvas_label,text,xywh,motivation,lang
```
 to the manifest, you can use the following command:

 ```
./annotations/inject_inline_annotations.py <manifest_in.json> <annotations.csv> <manifest_out.json>

 ```

- Update the enriched manifest to a IIIF viewer , either locally or host it online. (https://manifest-editor.digirati.services/)