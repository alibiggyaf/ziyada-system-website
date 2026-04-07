# Workflow: Create Professional Introduction Slides

## Objective
Generate a Google Slides presentation for a professional self-introduction or project overview using the Google Workspace CLI.

## Required Inputs
- Title of the presentation
- Your name and role
- Key points or bullet list to include
- (Optional) logo or image URL

## Tools Required
- `gws` CLI installed and authenticated
- Optional: a shell script `tools/create_slides.sh` to automate the sequence

## Steps
1. Use the CLI to create a new Slides deck with the provided title.
2. Add a cover slide containing title, name, and role.
3. For each bullet point, append a new slide with the text.
4. If a logo/image URL is provided, insert it on the cover or relevant slide.
5. Share the presentation if desired.

### Example commands
```bash
# create a new deck and capture the ID
TITLE="Professional Introduction"
DECK_ID=$(gws slides presentations create --json "{\"title\":\"$TITLE\"}" | jq -r '.presentationId')

# add a title slide
# note: object IDs are returned by createSlide; you may need to query the deck first
# for simplicity this script assumes predefined layout TITLE and known object ids

# append bullet slides for each point
POINTS=("Background" "Experience" "Skills" "Contact")
for pt in "${POINTS[@]}"; do
  gws slides presentations batchUpdate --presentationId "$DECK_ID" --json "{\"requests\":[{\"createSlide\":{\"slideLayoutReference\":{\"predefinedLayout\":\"BLANK\"}}},{\"insertText\":{\"objectId\":\"title_0\",\"text\":\"$pt\"}}]}"
done

# share the presentation (optional)
gws drive permissions create --fileId "$DECK_ID" --json '{"role":"reader","type":"anyone"}'
```
