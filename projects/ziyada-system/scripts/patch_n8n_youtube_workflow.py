#!/usr/bin/env python3
"""
patch_n8n_youtube_workflow.py
─────────────────────────────
Creates the missing "Youtube Search Workflow" sub-workflow that workflow 62
(15-AI_Youtube_Trend_Finder_Based_On_Niche) needs, then updates workflow 62
to reference it.

The original sub-workflow (N9DveO781xbNf8qs) was deleted.
The orphaned nodes in workflow 62 are used as the template.
get_videos1 is converted from the native YouTube node (needs OAuth2) to
an HTTP Request node using $env["GOOGLE_API_KEY"] — the same pattern
already used by find_video_data1.
"""

import json
import sys
import uuid
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJu"
    "OG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcy"
    "MDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
)
HEADERS = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}
WF62_ID = "62MN6oqxOs3levjh"


def uid():
    return str(uuid.uuid4())


def build_youtube_search_workflow():
    """
    Build the 'Youtube Search Workflow' payload.

    Entry: executeWorkflowTrigger (receives { search_term: "..." })
    → search_youtube (HTTP Request → YouTube Data API /search)
    → split_results (Code: split items array into individual items)
    → loop_over_items1 (splitInBatches)
       ├─[main/0 done] → retrieve_data_from_memory1 → response1
       └─[main/1 loop] → find_video_data1 (HTTP Request → /videos details)
                       → if_longer_than_3_
                          ├─[true]  → group_data1 → save_data_to_memory1 → loop
                          └─[false] → loop (skip short videos)
    """
    nodes = [
        # ── Entry trigger ──────────────────────────────────────────────────
        {
            "id": uid(),
            "name": "execute_trigger",
            "type": "n8n-nodes-base.executeWorkflowTrigger",
            "typeVersion": 1,
            "position": [-800, 160],
            "parameters": {},
        },
        # ── YouTube Search (HTTP) ──────────────────────────────────────────
        # Replaces the native n8n-nodes-base.youTube node that required OAuth2.
        # Uses GOOGLE_API_KEY env var — same pattern as find_video_data1.
        {
            "id": uid(),
            "name": "search_youtube",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-608, 160],
            "parameters": {
                "url": "https://www.googleapis.com/youtube/v3/search",
                "method": "GET",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "key", "value": '={{ $env["GOOGLE_API_KEY"] }}'},
                        {"name": "q", "value": "={{ $json.search_term }}"},
                        {"name": "part", "value": "snippet"},
                        {"name": "type", "value": "video"},
                        {"name": "maxResults", "value": "3"},
                        {
                            "name": "publishedAfter",
                            "value": "={{ new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString() }}",
                        },
                        {"name": "regionCode", "value": "US"},
                        {"name": "order", "value": "relevance"},
                        {"name": "safeSearch", "value": "moderate"},
                    ]
                },
                "options": {},
            },
        },
        # ── Split items array into individual items ─────────────────────────
        # The HTTP response has items: [...], we split so each item becomes
        # a separate n8n item (matching native YouTube node output format).
        {
            "id": uid(),
            "name": "split_results",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [-416, 160],
            "parameters": {
                "jsCode": (
                    "const items = $input.first().json.items || [];\n"
                    "if (items.length === 0) return [{ json: {} }];\n"
                    "return items.map(item => ({ json: item }));"
                )
            },
        },
        # ── splitInBatches loop ────────────────────────────────────────────
        {
            "id": uid(),
            "name": "loop_over_items1",
            "type": "n8n-nodes-base.splitInBatches",
            "typeVersion": 3,
            "position": [-304, 160],
            "parameters": {"options": {}},
        },
        # ── Fetch video details (unchanged from original) ──────────────────
        {
            "id": uid(),
            "name": "find_video_data1",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2,
            "position": [-96, 320],
            "parameters": {
                "url": "https://www.googleapis.com/youtube/v3/videos?",
                "sendQuery": True,
                "queryParameters": {
                    "parameters": [
                        {"name": "key", "value": '={{ $env["GOOGLE_API_KEY"] }}'},
                        {"name": "id", "value": "={{ $json.id.videoId }}"},
                        {"name": "part", "value": "contentDetails, snippet, statistics"},
                    ]
                },
                "options": {},
            },
        },
        # ── Filter: only keep videos > 3m30s ──────────────────────────────
        {
            "id": uid(),
            "name": "if_longer_than_3_",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [80, 320],
            "parameters": {
                "conditions": {
                    "options": {
                        "version": 2,
                        "leftValue": "",
                        "caseSensitive": True,
                        "typeValidation": "strict",
                    },
                    "combinator": "and",
                    "conditions": [
                        {
                            "id": uid(),
                            "operator": {
                                "type": "boolean",
                                "operation": "true",
                                "singleValue": True,
                            },
                            "leftValue": (
                                "={{ \n"
                                "  (() => {\n"
                                "    const duration = $json.items[0].contentDetails.duration;\n"
                                "    const iso8601ToSeconds = iso8601 => {\n"
                                "      const match = iso8601.match(/PT(?:(\\d+)H)?(?:(\\d+)M)?(?:(\\d+)S)?/);\n"
                                "      const hours = parseInt(match[1] || 0, 10);\n"
                                "      const minutes = parseInt(match[2] || 0, 10);\n"
                                "      const seconds = parseInt(match[3] || 0, 10);\n"
                                "      return hours * 3600 + minutes * 60 + seconds;\n"
                                "    };\n"
                                "    const durationInSeconds = iso8601ToSeconds(duration);\n"
                                "    return durationInSeconds > 210;\n"
                                "  })()\n"
                                "}}"
                            ),
                            "rightValue": "",
                        }
                    ],
                },
                "options": {},
            },
        },
        # ── Extract structured fields ──────────────────────────────────────
        {
            "id": uid(),
            "name": "group_data1",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [368, 304],
            "parameters": {
                "assignments": {
                    "assignments": [
                        {"id": uid(), "name": "id", "type": "string", "value": "={{ $json.items[0].id }}"},
                        {"id": uid(), "name": "viewCount", "type": "string", "value": "={{ $json.items[0].statistics.viewCount }}"},
                        {"id": uid(), "name": "likeCount", "type": "string", "value": "={{ $json.items[0].statistics.likeCount }}"},
                        {"id": uid(), "name": "commentCount", "type": "string", "value": "={{ $json.items[0].statistics.commentCount }}"},
                        {"id": uid(), "name": "description", "type": "string", "value": "={{ $json.items[0].snippet.description }}"},
                        {"id": uid(), "name": "title", "type": "string", "value": "={{ $json.items[0].snippet.title }}"},
                        {"id": uid(), "name": "channelTitle", "type": "string", "value": "={{ $json.items[0].snippet.channelTitle }}"},
                        {"id": uid(), "name": "tags", "type": "string", "value": "={{ ($json.items[0].snippet.tags || []).join(', ') }}"},
                        {"id": uid(), "name": "channelId", "type": "string", "value": "={{ $json.items[0].snippet.channelId }}"},
                    ]
                },
                "options": {},
            },
        },
        # ── Accumulate results in workflow static data ─────────────────────
        {
            "id": uid(),
            "name": "save_data_to_memory1",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [560, 304],
            "parameters": {
                "mode": "runOnceForEachItem",
                "jsCode": (
                    "const workflowStaticData = $getWorkflowStaticData('global');\n"
                    "\n"
                    "if (typeof workflowStaticData.lastExecution !== 'object') {\n"
                    "    workflowStaticData.lastExecution = { response: '' };\n"
                    "}\n"
                    "\n"
                    "function removeEmojis(text) {\n"
                    "    return text.replace(/[\\u{1F600}-\\u{1F64F}|\\u{1F300}-\\u{1F5FF}|\\u{1F680}-\\u{1F6FF}|\\u{2600}-\\u{26FF}|\\u{2700}-\\u{27BF}]/gu, '');\n"
                    "}\n"
                    "\n"
                    "function cleanDescription(description) {\n"
                    "    return description\n"
                    "        .replace(/https?:\\/\\/\\S+/g, '')\n"
                    "        .replace(/www\\.\\S+/g, '')\n"
                    "        .replace(/  +/g, ' ')\n"
                    "        .trim();\n"
                    "}\n"
                    "\n"
                    "const currentItem = { ...$input.item };\n"
                    "\n"
                    "if (currentItem.description) {\n"
                    "    currentItem.description = cleanDescription(currentItem.description);\n"
                    "}\n"
                    "\n"
                    "let sanitizedItem = JSON.stringify(currentItem)\n"
                    "    .replace(/\\\\r/g, ' ')\n"
                    "    .replace(/https?:\\/\\/\\S+/g, '')\n"
                    "    .replace(/www\\.\\S+/g, '')\n"
                    "    .replace(/\\\\n/g, ' ')\n"
                    "    .replace(/\\n/g, ' ')\n"
                    "    .replace(/\\\\/g, '')\n"
                    "    .replace(/  +/g, ' ')\n"
                    "    .trim();\n"
                    "\n"
                    "if (workflowStaticData.lastExecution.response) {\n"
                    "    workflowStaticData.lastExecution.response += ' ### NEXT VIDEO FOUND: ### ';\n"
                    "}\n"
                    "\n"
                    "workflowStaticData.lastExecution.response += removeEmojis(sanitizedItem);\n"
                    "\n"
                    "return workflowStaticData.lastExecution;\n"
                ),
            },
        },
        # ── Read accumulated results ───────────────────────────────────────
        {
            "id": uid(),
            "name": "retrieve_data_from_memory1",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [-16, 112],
            "parameters": {
                "jsCode": (
                    "const workflowStaticData = $getWorkflowStaticData('global');\n"
                    "const lastExecution = workflowStaticData.lastExecution;\n"
                    "return lastExecution;"
                )
            },
        },
        # ── Format final response ──────────────────────────────────────────
        {
            "id": uid(),
            "name": "response1",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3.4,
            "position": [304, 112],
            "parameters": {
                "assignments": {
                    "assignments": [
                        {
                            "id": uid(),
                            "name": "response",
                            "type": "string",
                            "value": "={{ $input.all() }}",
                        }
                    ]
                },
                "options": {},
            },
        },
    ]

    # Build node name → id mapping for connections
    name_to_id = {n["name"]: n["id"] for n in nodes}

    connections = {
        "execute_trigger": {
            "main": [[{"node": "search_youtube", "type": "main", "index": 0}]]
        },
        "search_youtube": {
            "main": [[{"node": "split_results", "type": "main", "index": 0}]]
        },
        "split_results": {
            "main": [[{"node": "loop_over_items1", "type": "main", "index": 0}]]
        },
        "loop_over_items1": {
            "main": [
                # port 0 = done (all batches processed)
                [{"node": "retrieve_data_from_memory1", "type": "main", "index": 0}],
                # port 1 = loop (each batch)
                [{"node": "find_video_data1", "type": "main", "index": 0}],
            ]
        },
        "find_video_data1": {
            "main": [[{"node": "if_longer_than_3_", "type": "main", "index": 0}]]
        },
        "if_longer_than_3_": {
            "main": [
                # port 0 = true (long enough)
                [{"node": "group_data1", "type": "main", "index": 0}],
                # port 1 = false (too short, skip back to loop)
                return {
                    "name": "Youtube Search Workflow",
                    "nodes": nodes,
                    "connections": connections,
                        [{"node": "loop_over_items1", "type": "main", "index": 0}],
        },
    }

    return {
        "name": "Youtube Search Workflow",
        "nodes": nodes,
        "connections": connections,
            return {
                "name": "Youtube Search Workflow",
                "nodes": nodes,
                "connections": connections,
                "settings": {"executionOrder": "v1"},
            }
    payload = build_youtube_search_workflow()
    r = requests.post(f"{BASE}/api/v1/workflows", headers=HEADERS, json=payload)
    print(f"Create sub-workflow status: {r.status_code}")
    if r.status_code not in (200, 201):
        print("Error:", r.text[:500])
        sys.exit(1)
    result = r.json()
    new_id = result.get("id")
    print(f"Created sub-workflow id: {new_id}  name: {result.get('name')}")
    return new_id
            "if_longer_than_3_": {
                "main": [
                    [{"node": "group_data1", "type": "main", "index": 0}],
                    [{"node": "loop_over_items1", "type": "main", "index": 0}],
                ]
            },
            "group_data1": {
                "main": [[{"node": "save_data_to_memory1", "type": "main", "index": 0}]]
            },
            "save_data_to_memory1": {
                "main": [[{"node": "loop_over_items1", "type": "main", "index": 0}]]
            },
            "retrieve_data_from_memory1": {
                "main": [[{"node": "response1", "type": "main", "index": 0}]]
            },
        }

        return {
            "name": "Youtube Search Workflow",
            "nodes": nodes,
            "connections": connections,
            "settings": {"executionOrder": "v1"},
        }


    def create_sub_workflow():
        payload = build_youtube_search_workflow()
        r = requests.post(f"{BASE}/api/v1/workflows", headers=HEADERS, json=payload)
        print(f"Create sub-workflow: {r.status_code}")
        if r.status_code not in (200, 201):
            print("Error:", r.text[:500])
            sys.exit(1)
        result = r.json()
        new_id = result.get("id")
        print(f"  id={new_id}  name={result.get('name')}")
        return new_id
        sys.exit(1)

    # Re-activate workflow 62 (PUT may deactivate it)
    r3 = requests.post(f"{BASE}/api/v1/workflows/{WF62_ID}/activate", headers=HEADERS)
    print(f"Activate workflow 62 status: {r3.status_code}")

    # Verify
    r4 = requests.get(f"{BASE}/api/v1/workflows/{WF62_ID}", headers=HEADERS)
    wf_check = r4.json()
    print(f"Verification — workflow 62 active: {wf_check.get('active')}")
    for node in wf_check.get("nodes", []):
        if node["name"] == "youtube_search":
            ref = node["parameters"].get("workflowId", {})
            print(f"  youtube_search now references: {ref.get('value')} ({ref.get('cachedResultName')})")


def main():
    print("=" * 60)
    print("Step 1: Create Youtube Search sub-workflow")
    print("=" * 60)
    sub_wf_id = create_sub_workflow()

    print()
    print("=" * 60)
    print("Step 2: Patch workflow 62 to reference new sub-workflow")
    print("=" * 60)
    patch_workflow_62(sub_wf_id)

    print()
    print("Done. Workflow 62 is now connected to a functional Youtube Search sub-workflow.")
    print(f"Sub-workflow ID: {sub_wf_id}")


if __name__ == "__main__":
    main()
