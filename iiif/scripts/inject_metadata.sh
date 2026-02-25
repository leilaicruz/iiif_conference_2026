#!/usr/bin/env bash
set -euo pipefail

UUID="${1:?Usage: $0 <dataset_uuid> <manifest_in.json> <manifest_out.json>}"
MANIFEST_IN="${2:?Usage: $0 <dataset_uuid> <manifest_in.json> <manifest_out.json>}"
MANIFEST_OUT="${3:?Usage: $0 <dataset_uuid> <manifest_in.json> <manifest_out.json>}"

API="https://data.4tu.nl/v2/articles/${UUID}"

# Fetch dataset JSON
dataset="$(curl -fsS "$API")"

# Extract raw fields
resource_title="$(jq -r '.resource_title // empty' <<<"$dataset")"
resource_doi="$(jq -r '.resource_doi // empty' <<<"$dataset")"
categories="$(jq -r '.categories // [] | map(.title) | unique | join("; ")' <<<"$dataset")"
description_html="$(jq -r '.description // empty' <<<"$dataset")"

# --- Clean HTML description ---
# 1. Remove tags
# 2. Decode common HTML entities
# 3. Collapse multiple blank lines

description_clean="$(printf "%s" "$description_html" \
  | sed -E 's/<[^>]+>//g' \
  | sed -e 's/&nbsp;/ /g' \
        -e 's/&amp;/\&/g' \
        -e 's/&lt;/</g' \
        -e 's/&gt;/>/g' \
        -e 's/&quot;/"/g' \
  | awk 'NF {print} !NF {print ""}' \
)"

# --- Build metadata JSON ---
meta="$(jq -n \
  --arg rt "$resource_title" \
  --arg rdoi "$resource_doi" \
  --arg cats "$categories" \
  --arg desc "$description_clean" '
  def md($k; $v):
    {label:{en:[$k]}, value:{en:[$v]}};

  [
    (if $rt   != "" then md("Resource title"; $rt) else empty end),
    (if $rdoi != "" then md("Resource DOI";   $rdoi) else empty end),
    (if $cats != "" then md("Categories";     $cats) else empty end),
    (if $desc != "" then md("Description";    $desc) else empty end)
  ]
')"

# --- Inject into manifest ---
jq --argjson meta "$meta" '
  (.metadata //= [])
  | .metadata = ((.metadata + $meta) | unique_by(.label.en[0]))

  # Also set summary if missing
  | if (.summary|type) != "object" then
        .summary = {en: [ ($meta[] | select(.label.en[0]=="Description") | .value.en[0]) ]}
    elif ((.summary.en // []) | length) == 0 then
        .summary.en = [ ($meta[] | select(.label.en[0]=="Description") | .value.en[0]) ]
    else .
    end
' "$MANIFEST_IN" > "$MANIFEST_OUT"

echo "Wrote: $MANIFEST_OUT"




## usage
# ./inject_metadata.sh <dataset_uuid> <manifest_in.json> <manifest_out.json>