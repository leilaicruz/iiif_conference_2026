# Next steps to implement in the dashboard to showcase possible features:

- Add the navPlace per file as Jules did here: https://sammeltassen.nl/iiif-manifests/allmaps/port-city-atlas.json
  - in our case we have geolocation information at the dataset-level, but in the enrichment tool we should add then the geolocation as a navplace per file in the manifest. 
  - We can add more metadata fields . 
  - Remove the description as a posible metadata field, because it is already loaded in the manifest.



- In the upload process, if the format is one of the following for iiif , please bring a pop up , that recomend not to upload a zip folder! 
  - One solution is to have a drop down with specific formats and have room for also introducing text if someone is submitting another format that is not in the list. 