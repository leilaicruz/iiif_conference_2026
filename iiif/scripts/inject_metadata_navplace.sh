#!/usr/bin/env bash
set -euo pipefail

UUID="${1:?Usage: $0 <dataset_uuid> <manifest_in.json> <manifest_out.json>}"
MANIFEST_IN="${2:?Usage: $0 <dataset_uuid> <manifest_in.json> <manifest_out.json>}"
MANIFEST_OUT="${3:?Usage: $0 <dataset_uuid> <manifest_in.json> <manifest_out.json>}"

API="https://data.4tu.nl/v2/articles/${UUID}"

dataset="$(curl -fsS "$API")"

# Core fields
resource_title="$(jq -r '.resource_title // empty' <<<"$dataset")"
resource_doi="$(jq -r '.resource_doi // empty' <<<"$dataset")"
categories="$(jq -r '.categories // [] | map(.title) | unique | join("; ")' <<<"$dataset")"
description_html="$(jq -r '.description // empty' <<<"$dataset")"

# Clean HTML description (basic)
description_clean="$(printf "%s" "$description_html" \
  | sed -E 's/<[^>]+>//g' \
  | sed -e 's/&nbsp;/ /g' \
        -e 's/&amp;/\&/g' \
        -e 's/&lt;/</g' \
        -e 's/&gt;/>/g' \
        -e 's/&quot;/"/g' \
  | awk 'NF {print} !NF {print ""}' \
)"

# Helper: get custom_field by name, returning a JSON value (string/array/number/etc.)
cf_json() {
  local key="$1"
  jq -c --arg k "$key" '
    (.custom_fields // [])
    | map(select(.name == $k) | .value)
    | first // null
  ' <<<"$dataset"
}

# Extract custom_fields we care about
time_cov="$(cf_json "Time coverage")"
derived_from="$(cf_json "Derived From")"
geo_lon="$(cf_json "Geolocation Longitude")"
geo_lat="$(cf_json "Geolocation Latitude")"

# Build metadata array (normalize values to strings)
meta="$(jq -n \
  --arg rt "$resource_title" \
  --arg rdoi "$resource_doi" \
  --arg cats "$categories" \
  --arg desc "$description_clean" \
  --argjson time_cov "$time_cov" \
  --argjson derived_from "$derived_from" '
  def md($k; $v): {label:{en:[$k]}, value:{en:[$v]}};

  def as_text($v):
    if $v == null then ""
    elif ($v|type)=="array" then ($v | map(tostring) | join("; "))
    else ($v|tostring)
    end;

  [
    (if $rt   != "" then md("Resource title"; $rt) else empty end),
    (if $rdoi != "" then md("Resource DOI";   $rdoi) else empty end),
    (if $cats != "" then md("Categories";     $cats) else empty end),
    (if $desc != "" then md("Description";    $desc) else empty end),

    (if as_text($time_cov)     != "" then md("Time coverage"; as_text($time_cov)) else empty end),
    (if as_text($derived_from) != "" then md("Derived From";  as_text($derived_from)) else empty end)
  ]
')"

# Build navPlace if both lon/lat exist and are numeric-ish
navplace="$(jq -n --argjson lon "$geo_lon" --argjson lat "$geo_lat" '
  def to_num($x):
    if $x == null then null
    elif ($x|type)=="number" then $x
    elif ($x|type)=="string" then
      ($x | gsub(","; ".") | tonumber)
    else null
    end;

  (to_num($lon)) as $lo |
  (to_num($lat)) as $la |
  if ($lo == null or $la == null) then
    null
  else
    {
      type: "FeatureCollection",
      features: [
        {
          type: "Feature",
          properties: { label: { en: ["Location"] } },
          geometry: { type: "Point", coordinates: [ $lo, $la ] }
        }
      ]
    }
  end
')"

# Inject into manifest
jq --argjson meta "$meta" --argjson nav "$navplace" '
  (.metadata //= [])
  | .metadata = ((.metadata + $meta) | unique_by(.label.en[0]))

  # Optionally set summary from Description if empty
  | if (.summary|type) != "object" then
        .summary = {en: [ ($meta[] | select(.label.en[0]=="Description") | .value.en[0]) ]} 
    elif ((.summary.en // []) | length) == 0 then
        .summary.en = [ ($meta[] | select(.label.en[0]=="Description") | .value.en[0]) ]
    else .
    end

  # navPlace (only if we successfully built it)
  | if $nav == null then . else .navPlace = $nav end
' "$MANIFEST_IN" > "$MANIFEST_OUT"

echo "Wrote: $MANIFEST_OUT"