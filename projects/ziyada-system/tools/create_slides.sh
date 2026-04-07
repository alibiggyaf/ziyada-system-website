#!/usr/bin/env bash

# simple helper to create an intro deck via gws
# usage: create_slides.sh "Presentation Title" "Your Name" "Your Role" "Point1;Point2;Point3" [logo_url]

set -euo pipefail

TITLE="$1"
NAME="$2"
ROLE="$3"
IFS=';' read -r -a POINTS <<< "$4"
LOGO_URL="${5-}"

# create deck
DECK_ID=$(gws slides presentations create --json "{\"title\":\"$TITLE\"}" | jq -r '.presentationId')
echo "Created deck $DECK_ID"

# add title slide
REQS="[]"
REQS=$(jq -n --arg t "$TITLE" --arg n "$NAME" --arg r "$ROLE" '
  [{"createSlide":{"slideLayoutReference":{"predefinedLayout":"TITLE"}}},
   {"insertText":{"objectId":"title","text":$t}},
   {"insertText":{"objectId":"subtitle","text":($n + " – " + $r)}}]
')

if [[ -n "$LOGO_URL" ]]; then
  # insert image request
  IMG_REQ=$(jq -n --arg url "$LOGO_URL" '{"createImage":{"url":$url,"elementProperties":{"pageObjectId":""}}}')
  REQS=$(echo "$REQS" | jq '. + [ $img ]' --argjson img "$IMG_REQ")
fi

gws slides presentations batchUpdate --presentationId "$DECK_ID" --json "{\"requests\": $REQS}"

# add bullets
for pt in "${POINTS[@]}"; do
  # create blank slide and add text
  gws slides presentations batchUpdate --presentationId "$DECK_ID" --json "{\"requests\":[{\"createSlide\":{\"slideLayoutReference\":{\"predefinedLayout\":\"BLANK\"}}},{\"insertText\":{\"objectId\":\"title_0\",\"text\":\"$pt\"}}]}"
done

echo "Deck ready: https://docs.google.com/presentation/d/$DECK_ID/edit"
