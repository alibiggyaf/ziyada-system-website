# AI Video Automation Pipeline

Production-ready planning pack for a reusable n8n video generation system built around Airtable-driven approvals, Kie.ai generation models, ElevenLabs voice, Suno music, and FFmpeg final rendering.

## Scope

This package is designed for:
- Product brands with product boards and product shots
- Service businesses with no product board, where the workflow must still produce premium cinematic ads
- Local-first testing before moving to cloud execution
- Future expansion to auto-publishing on social media

## Recommended Folder Structure

```text
projects/ziyada-system/video-automation/
├── README.md
├── .env.example
├── airtable/
│   └── field-mappings.json
├── samples/
│   └── sample_records.json
├── workflows/
│   └── ai_video_pipeline_blueprint.json
└── scripts/
    ├── check_env.py
    └── render_final_video.py
```

## Architecture Summary

The system is split into 6 executable workflows plus 1 future scaffold:

1. `WF01 - Project Prompt Orchestrator`
2. `WF02 - Scene Image Generator`
3. `WF03 - Scene Video Generator`
4. `WF04 - Scene Voice Generator`
5. `WF05 - Scene Music Generator`
6. `WF06 - Final Render Orchestrator`
7. `WF07 - Publish Scaffold`

Each workflow is independently triggerable and only advances when Airtable approval fields allow it.

## Airtable Design

Use three tables:
- `Projects`
- `Scenes`
- `Final Outputs`

The field-level mapping is defined in [airtable/field-mappings.json](./airtable/field-mappings.json).

## Approval Model

Recommended manual approvals:
- `Projects.approved_project`
- `Scenes.approved_prompt`
- `Scenes.approved_images`
- `Scenes.approved_video`
- `Final Outputs.approved_for_final_render`
- `Final Outputs.approved_for_posting`

Recommended full automation:
- Scene prompt parsing into records
- Image polling and persistence
- Video polling and persistence
- Voice polling and persistence
- Music polling and persistence
- Final scene readiness checks
- Final render asset download/prep

## Workflow Details

### WF01 - Project Prompt Orchestrator

Trigger:
- `Projects.trigger_generate_prompts = true`

Primary responsibility:
- Read one project
- Infer whether it is product-led or service-led
- Generate concept, style, Saudi voiceover master script, music prompt, scene breakdown
- Convert the narrative into structured scene records

Node sequence:

1. `Manual Trigger - Local Test`
   - Local-only runner during build

2. `Airtable Trigger - Projects Prompt Request`
   - Watches `Projects`
   - Fires when `trigger_generate_prompts` becomes true

3. `Normalize Project Input`
   - Code node
   - Maps Airtable fields into a clean project object
   - Computes `creative_mode`:
     - `product_brand` if `has_product = true` or `product_board` exists
     - `service_ad` otherwise

4. `Build Prompt Builder Payload`
   - Code node
   - Creates the structured instruction block for the built-in `video-prompt-builder` style logic
   - Enforces Saudi Najdi-inspired storytelling voice

5. `LLM - Generate Concept Package`
   - HTTP Request or AI node
   - Returns strict JSON:
     - `concept_idea`
     - `video_style`
     - `voiceover_master_script`
     - `music_prompt`
     - `scene_count`
     - `scenes[]`

6. `Parse Concept JSON`
   - Code node
   - Validates required fields
   - Rejects malformed scene arrays

7. `Build Scene Records`
   - Code node
   - Expands scene objects into Airtable-ready insert payloads
   - Copies `project_id` to every scene

8. `Airtable - Upsert Scene Records`
   - HTTP Request or Airtable node
   - Creates one record per scene

9. `Airtable - Update Project Outputs`
   - Writes:
     - `concept_idea`
     - `video_style`
     - `voiceover_master_script`
     - `music_prompt`
     - `scene_count`
     - `project_status = prompts_generated`
     - `trigger_generate_prompts = false`

10. `Error Handler - Project Prompt Failure`
   - Updates `Projects.error_log`
   - Sets `project_status = prompt_generation_failed`

Manual approval after WF01:
- Review `concept_idea`
- Review generated `Scenes`
- Set `approved_project = true`
- Approve scene prompts individually via `Scenes.approved_prompt`

### WF02 - Scene Image Generator

Trigger:
- `Scenes.trigger_generate_images = true`
- `Scenes.approved_prompt = true`

Node sequence:

1. `Airtable Trigger - Scene Image Request`
2. `Fetch Scene + Parent Project`
3. `Build Nano Banana Start Payload`
4. `HTTP - Nano Banana Start Frame`
5. `Poll Nano Banana Start Frame`
6. `Build Nano Banana End Payload`
7. `HTTP - Nano Banana End Frame`
8. `Poll Nano Banana End Frame`
9. `Airtable - Update Scene Images`
   - Writes:
     - `start_image_url`
     - `end_image_url`
     - `image_done = true`
     - `final_scene_status = images_ready`
     - `trigger_generate_images = false`
10. `Error Handler - Scene Image Failure`

### WF03 - Scene Video Generator

Trigger:
- `Scenes.trigger_generate_video = true`
- `Scenes.approved_images = true`

Node sequence:

1. `Airtable Trigger - Scene Video Request`
2. `Fetch Scene Assets`
3. `Build Veo Payload`
4. `HTTP - Veo 3.1 Generate`
5. `Poll Veo Job`
6. `Airtable - Update Scene Video`
   - Writes:
     - `scene_video_url`
     - `video_done = true`
     - `final_scene_status = video_ready`
     - `trigger_generate_video = false`
7. `Error Handler - Scene Video Failure`

### WF04 - Scene Voice Generator

Trigger:
- `Scenes.trigger_generate_voice = true`
- `Scenes.approved_video = true`

Node sequence:

1. `Airtable Trigger - Scene Voice Request`
2. `Fetch Scene + Project Voice Settings`
3. `Build ElevenLabs Payload`
4. `HTTP - ElevenLabs TTS`
5. `Store Voice File`
6. `Airtable - Update Scene Voice`
   - Writes:
     - `voiceover_url`
     - `voice_done = true`
     - `trigger_generate_voice = false`
7. `Error Handler - Scene Voice Failure`

### WF05 - Scene Music Generator

Trigger:
- `Scenes.trigger_generate_music = true`
- `Scenes.approved_video = true`

Node sequence:

1. `Airtable Trigger - Scene Music Request`
2. `Fetch Scene + Project Music Inputs`
3. `Build Suno Prompt`
4. `HTTP - Suno Generate`
5. `Poll Suno Job`
6. `Pick Best Two Music Variants`
7. `Airtable - Update Scene Music`
   - Writes:
     - `music_url_1`
     - `music_url_2`
     - `music_done = true`
     - `trigger_generate_music = false`
8. `Error Handler - Scene Music Failure`

### WF06 - Final Render Orchestrator

Trigger:
- `Final Outputs.trigger_final_render = true`
- `Final Outputs.approved_for_final_render = true`

Node sequence:

1. `Airtable Trigger - Final Render Request`
2. `Fetch Final Output Record`
3. `Fetch Project`
4. `Fetch Scenes For Project`
5. `Validate Render Readiness`
   - Ensures every required scene has:
     - `scene_video_url`
     - `voiceover_url`
     - optional music URL if music is enabled
     - `ready_for_final_render = true`

6. `Sort Scenes By Order`
7. `Build Render Manifest`
8. `Execute Local Render Script`
   - Calls `scripts/render_final_video.py`

9. `Airtable - Update Final Output`
   - Writes:
     - `final_video_url`
     - `posting_status = render_complete`
     - `trigger_final_render = false`

10. `Error Handler - Final Render Failure`

### WF07 - Publish Scaffold

Not fully implemented yet.

Required future nodes:
- `Router - Platform Target`
- `Prepare Caption Package`
- `Publish Instagram Reels`
- `Publish TikTok`
- `Publish YouTube Shorts`
- `Publish LinkedIn Video`
- `Write Publishing Result`

This scaffold should consume:
- `final_video_url`
- `final_caption`
- `hashtags`
- `platform_target`

## Prompt Generation Logic

The prompt generator should always produce one of two creative modes:

### Product mode

Use when:
- `has_product = true`
- `product_board` is present

Behavior:
- Product is featured clearly in at least 2 scenes
- Start/end image prompts preserve packaging and product identity
- Voiceover ties emotion to product benefit

### Service mode

Use when:
- No `product_board`
- No usable product image

Behavior:
- Build a cinematic business ad around:
  - central character
  - environment
  - operational pain point
  - premium transformation
  - service trust signal
  - CTA

Typical service scenes:
1. frustrated status quo
2. discovery/setup
3. transformation in workflow
4. business confidence/result
5. CTA close

## Voice Rules

ElevenLabs generation should target:
- Saudi Arabia audience
- Clean Saudi spoken Arabic
- Najdi-inspired natural rhythm
- Conversational premium tone
- No formal MSA announcer voice
- No exaggerated radio-commercial energy

Recommended voice instruction text:

```text
Natural Saudi Arabic, Najdi-inspired cadence, premium conversational delivery, human and warm, storytelling tone, confident but not loud, modern business ad, clean pronunciation, avoid formal newsreader style, avoid theatrical exaggeration.
```

## Music Rules

Music prompt should combine:
- cinematic underscore
- brand tone
- local relevance where appropriate
- no distracting vocals unless explicitly requested

Recommended music prompt pattern:

```text
Cinematic instrumental background for a premium Saudi business ad. Modern, emotional, polished, commercially safe, elegant pacing, subtle Middle Eastern texture if appropriate, no dominant vocals, should support voiceover and brand confidence.
```

## HTTP Request Payload Examples

These payloads are also embedded in [workflows/ai_video_pipeline_blueprint.json](./workflows/ai_video_pipeline_blueprint.json).

### Nano Banana Pro - Image Generation

Assumed node:
- `HTTP - Nano Banana Start Frame`

Method:
- `POST`

URL:
- `={{$env.KIE_BASE_URL}}/api/v1/images/generate`

Headers:

```json
{
  "Authorization": "=Bearer {{$env.KIE_API_KEY}}",
  "Content-Type": "application/json"
}
```

Body:

```json
{
  "model": "nano-banana-pro",
  "input": {
    "prompt": "={{ $json.start_image_prompt }}",
    "aspect_ratio": "9:16",
    "quality": "high",
    "safety_filter": "standard",
    "reference_images": [
      "={{ $json.core_character_board }}",
      "={{ $json.setting_board }}",
      "={{ $json.product_board }}"
    ]
  }
}
```

Polling example:

```json
{
  "method": "GET",
  "url": "={{$env.KIE_BASE_URL}}/api/v1/jobs/{{$json.job_id}}",
  "headers": {
    "Authorization": "=Bearer {{$env.KIE_API_KEY}}"
  }
}
```

### Veo 3.1 - Video Generation

Method:
- `POST`

URL:
- `={{$env.KIE_BASE_URL}}/api/v1/veo/generate`

Body:

```json
{
  "model": "veo-3.1",
  "generationType": "FIRST_AND_LAST_FRAMES_2_VIDEO",
  "aspect_ratio": "9:16",
  "prompt": "={{ $json.video_prompt }}",
  "imageUrls": [
    "={{ $json.start_image_url }}",
    "={{ $json.end_image_url }}"
  ],
  "metadata": {
    "scene_id": "={{ $json.scene_id }}",
    "project_id": "={{ $json.project_id }}"
  }
}
```

Polling example:

```json
{
  "method": "GET",
  "url": "={{$env.KIE_BASE_URL}}/api/v1/jobs/{{$json.taskId || $json.job_id}}",
  "headers": {
    "Authorization": "=Bearer {{$env.KIE_API_KEY}}"
  }
}
```

### ElevenLabs - Voice Generation

Method:
- `POST`

URL:
- `=https://api.elevenlabs.io/v1/text-to-speech/{{$env.ELEVENLABS_VOICE_ID}}`

Headers:

```json
{
  "xi-api-key": "={{$env.ELEVENLABS_API_KEY}}",
  "Content-Type": "application/json",
  "Accept": "audio/mpeg"
}
```

Body:

```json
{
  "text": "={{ $json.voiceover_segment }}",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.45,
    "similarity_boost": 0.8,
    "style": 0.2,
    "use_speaker_boost": true
  }
}
```

### Suno - Music Generation

Method:
- `POST`

URL:
- `={{$env.SUNO_BASE_URL}}/v1/generate`

Headers:

```json
{
  "Authorization": "=Bearer {{$env.SUNO_API_KEY}}",
  "Content-Type": "application/json"
}
```

Body:

```json
{
  "prompt": "={{ $json.combined_music_prompt }}",
  "instrumental": true,
  "duration_sec": "={{ $json.scene_duration_sec || 8 }}",
  "num_variants": 2,
  "metadata": {
    "scene_id": "={{ $json.scene_id }}",
    "project_id": "={{ $json.project_id }}"
  }
}
```

Polling example:

```json
{
  "method": "GET",
  "url": "={{$env.SUNO_BASE_URL}}/v1/jobs/{{$json.music_job_id}}",
  "headers": {
    "Authorization": "=Bearer {{$env.SUNO_API_KEY}}"
  }
}
```

## Code Node Logic

### Normalize project and infer creative mode

```javascript
const record = $json;
const fields = record.fields || record;

const hasProduct =
  fields.has_product === true ||
  fields.has_product === "true" ||
  !!fields.product_board;

return [{
  json: {
    airtable_record_id: record.id || null,
    project_id: fields.project_id,
    project_name: fields.project_name,
    business_type: fields.business_type || "general_business",
    product_or_service: fields.product_or_service || "",
    has_product: hasProduct,
    creative_mode: hasProduct ? "product_brand" : "service_ad",
    platform_target: fields.platform_target || "instagram_reels",
    video_goal: fields.video_goal || "",
    target_audience: fields.target_audience || "",
    video_duration_sec: Number(fields.video_duration_sec || 30),
    language: fields.language || "Arabic",
    dialect: fields.dialect || "Saudi Najdi-inspired",
    creative_direction: fields.creative_direction || "",
    core_character_board: fields.core_character_board || "",
    setting_board: fields.setting_board || "",
    product_board: fields.product_board || "",
    brand_notes: fields.brand_notes || "",
    cta: fields.cta || "",
    reference_links: fields.reference_links || "",
    music_style: fields.music_style || "cinematic premium",
    voice_gender: fields.voice_gender || "male",
    voice_style: fields.voice_style || "conversational premium"
  }
}];
```

### Parse scene JSON into Airtable records

```javascript
const project = $('Normalize Project Input').first().json;
const payload = $json;

if (!Array.isArray(payload.scenes) || !payload.scenes.length) {
  throw new Error('Scene array missing from concept payload');
}

return payload.scenes.map((scene, idx) => ({
  json: {
    fields: {
      scene_id: `${project.project_id}-SC${String(idx + 1).padStart(2, '0')}`,
      project_id: project.project_id,
      scene_order: idx + 1,
      scene_name: scene.scene_name || `Scene ${idx + 1}`,
      scene_duration_sec: Number(scene.scene_duration_sec || 5),
      start_image_prompt: scene.start_image_prompt || "",
      end_image_prompt: scene.end_image_prompt || "",
      transition_prompt: scene.transition_prompt || "",
      video_prompt: scene.video_prompt || "",
      voiceover_segment: scene.voiceover_segment || "",
      sfx_prompt: scene.sfx_prompt || "",
      music_cue: scene.music_cue || "",
      visual_notes: scene.visual_notes || "",
      approved_prompt: false,
      trigger_generate_images: false,
      image_done: false,
      approved_images: false,
      trigger_generate_video: false,
      video_done: false,
      approved_video: false,
      trigger_generate_voice: false,
      voice_done: false,
      trigger_generate_music: false,
      music_done: false,
      ready_for_final_render: false,
      final_scene_status: "prompt_generated",
      generation_log: JSON.stringify({
        created_from: "WF01",
        creative_mode: project.creative_mode
      })
    }
  }
}));
```

### Polling loop result parser

```javascript
const job = $json;

const status =
  job.status ||
  job.data?.status ||
  job.data?.state ||
  "unknown";

const normalized = String(status).toLowerCase();

if (["queued", "pending", "processing", "running", "submitted"].includes(normalized)) {
  return [{ json: { done: false, status: normalized, raw: job } }];
}

if (["completed", "success", "succeeded", "finished"].includes(normalized)) {
  return [{
    json: {
      done: true,
      status: normalized,
      asset_url:
        job.data?.output?.url ||
        job.data?.result?.url ||
        job.output?.url ||
        job.url ||
        "",
      raw: job
    }
  }];
}

throw new Error(`Generation job failed with status: ${status}`);
```

### Final render scene sort and validation

```javascript
const scenes = $input.all().map(i => i.json.fields || i.json);

const invalid = scenes.filter(scene =>
  !scene.scene_video_url ||
  !scene.voiceover_url ||
  scene.ready_for_final_render !== true
);

if (invalid.length) {
  throw new Error(`Scenes not ready for final render: ${invalid.map(s => s.scene_id).join(', ')}`);
}

scenes.sort((a, b) => Number(a.scene_order) - Number(b.scene_order));

return [{
  json: {
    project_id: scenes[0].project_id,
    scene_count: scenes.length,
    scenes
  }
}];
```

## Local Testing

### 1. Prepare `.env`

Copy [`.env.example`](./.env.example) and fill it with real values.

Important:
- This repo’s root `.env` currently contains malformed and mixed content. Do not reuse it directly for this package without cleanup.
- Keep this package’s environment file clean and dedicated.

### 2. Validate environment

```bash
cd "/Users/djbiggy/Downloads/Claude Code- File Agents/projects/ziyada-system/video-automation"
python3 scripts/check_env.py
```

### 3. Test final render helper

Prepare scene assets under your temp directory and run:

```bash
python3 scripts/render_final_video.py \
  --manifest samples/sample_records.json \
  --output ./tmp/test-final.mp4
```

### 4. Test n8n workflows locally

Recommended local n8n launch:

```bash
export $(grep -v '^#' .env | xargs)
n8n start
```

Then import:
- `workflows/ai_video_pipeline_blueprint.json`

## Testing Plan

### Prompt generation test

Goal:
- Confirm project input produces valid concept JSON and scene records

Test steps:
1. Create one `Projects` record from the sample JSON
2. Set `trigger_generate_prompts = true`
3. Confirm project updates:
   - `concept_idea`
   - `video_style`
   - `voiceover_master_script`
   - `music_prompt`
   - `scene_count`
4. Confirm `Scenes` records were created in order

Pass criteria:
- Scene array count matches `scene_count`
- Every scene has all required prompt fields

### Image generation test

Goal:
- Confirm start/end images are generated only after prompt approval

Test steps:
1. Set `approved_prompt = true`
2. Set `trigger_generate_images = true`
3. Confirm `start_image_url`, `end_image_url`, and `image_done = true`

Pass criteria:
- Both URLs exist
- Failed generation writes to `error_log`

### Video generation test

Goal:
- Confirm Veo uses the generated images and transition prompt

Test steps:
1. Set `approved_images = true`
2. Set `trigger_generate_video = true`
3. Confirm `scene_video_url` and `video_done = true`

Pass criteria:
- Valid scene clip URL exists
- Job polling completes inside retry window

### Voice generation test

Goal:
- Confirm Arabic Saudi voice output is produced and stored

Test steps:
1. Set `approved_video = true`
2. Set `trigger_generate_voice = true`
3. Confirm `voiceover_url` and `voice_done = true`

Pass criteria:
- Audio file stored successfully
- Segment uses scene-only script, not full project script

### Music generation test

Goal:
- Confirm Suno returns one or two options per scene

Test steps:
1. Set `approved_video = true`
2. Set `trigger_generate_music = true`
3. Confirm `music_url_1`, optional `music_url_2`, and `music_done = true`

Pass criteria:
- At least one music URL exists
- Prompt includes project-level and scene-level cues

### Final render test

Goal:
- Confirm all scene assets are downloaded, sorted, and rendered

Test steps:
1. Mark all scenes `ready_for_final_render = true`
2. Create one `Final Outputs` record
3. Set `approved_for_final_render = true`
4. Set `trigger_final_render = true`
5. Confirm final file path or URL is written

Pass criteria:
- Final MP4 exists
- `posting_status = render_complete`
- `render_log` contains asset manifest and FFmpeg command summary

## Practical Approval Notes

Approve manually:
- project concept if campaign matters strategically
- scene prompts if the brand is visual-sensitive
- scene images before video spend
- scene videos before voice/music spend
- final render before publishing

Automate fully:
- retries and polling
- logs and status updates
- ready-state calculations
- render asset preparation
- future publishing handoff formatting

## Production Notes

- Never store API keys inside nodes. Use `$env.*`.
- Keep one shared error pattern across all workflows.
- Use retry-aware HTTP nodes for all async providers.
- Store provider job IDs in Airtable when available.
- Add `generation_log` JSON snapshots for debugging.
- Use a dedicated storage target later for final video delivery.
- Keep publishing separate from render. They are different failure domains.
