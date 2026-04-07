#!/usr/bin/env python3
"""fix_youtube_wf.py — Create Youtube Search sub-workflow + patch workflow 62."""
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
H = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}
WF62 = "62MN6oqxOs3levjh"


def uid():
    return str(uuid.uuid4())


def make_node(name, ntype, tv, pos, params):
    return {"id": uid(), "name": name, "type": ntype,
            "typeVersion": tv, "position": pos, "parameters": params}


def build_payload():
    # ── nodes ────────────────────────────────────────────────────────────
    n_trigger = make_node(
        "execute_trigger",
        "n8n-nodes-base.executeWorkflowTrigger", 1, [-800, 160], {}
    )

    n_search = make_node(
        "search_youtube",
        "n8n-nodes-base.httpRequest", 4.2, [-608, 160],
        {
            "url": "https://www.googleapis.com/youtube/v3/search",
            "method": "GET",
            "sendQuery": True,
            "queryParameters": {"parameters": [
                {"name": "key",           "value": '={{ $env["GOOGLE_API_KEY"] }}'},
                {"name": "q",             "value": "={{ $json.search_term }}"},
                {"name": "part",          "value": "snippet"},
                {"name": "type",          "value": "video"},
                {"name": "maxResults",    "value": "3"},
                {"name": "publishedAfter","value": "={{ new Date(Date.now()-2*24*60*60*1000).toISOString() }}"},
                {"name": "regionCode",    "value": "US"},
                {"name": "order",         "value": "relevance"},
                {"name": "safeSearch",    "value": "moderate"},
            ]},
            "options": {},
        }
    )

    # Split response items[] into individual n8n items
    n_split = make_node(
        "split_results",
        "n8n-nodes-base.code", 2, [-416, 160],
        {"jsCode": (
            "const items = $input.first().json.items || [];\n"
            "if (items.length === 0) return [{ json: {} }];\n"
            "return items.map(item => ({ json: item }));"
        )}
    )

    n_loop = make_node(
        "loop_over_items1",
        "n8n-nodes-base.splitInBatches", 3, [-304, 160],
        {"options": {}}
    )

    n_details = make_node(
        "find_video_data1",
        "n8n-nodes-base.httpRequest", 4.2, [-96, 320],
        {
            "url": "https://www.googleapis.com/youtube/v3/videos?",
            "sendQuery": True,
            "queryParameters": {"parameters": [
                {"name": "key",  "value": '={{ $env["GOOGLE_API_KEY"] }}'},
                {"name": "id",   "value": "={{ $json.id.videoId }}"},
                {"name": "part", "value": "contentDetails, snippet, statistics"},
            ]},
            "options": {},
        }
    )

    n_if = make_node(
        "if_longer_than_3_",
        "n8n-nodes-base.if", 2.2, [80, 320],
        {
            "conditions": {
                "options": {"version": 2, "leftValue": "",
                            "caseSensitive": True, "typeValidation": "strict"},
                "combinator": "and",
                "conditions": [{
                    "id": uid(),
                    "operator": {"type": "boolean", "operation": "true", "singleValue": True},
                    "leftValue": (
                        "={{ (() => {"
                        " const d=$json.items[0].contentDetails.duration;"
                        " const m=d.match(/PT(?:(\\d+)H)?(?:(\\d+)M)?(?:(\\d+)S)?/);"
                        " return (parseInt(m[1]||0)*3600+parseInt(m[2]||0)*60+parseInt(m[3]||0))>210;"
                        " })() }}"
                    ),
                    "rightValue": "",
                }],
            },
            "options": {},
        }
    )

    n_group = make_node(
        "group_data1",
        "n8n-nodes-base.set", 3.4, [368, 304],
        {"assignments": {"assignments": [
            {"id": uid(), "name": "id",           "type": "string", "value": "={{ $json.items[0].id }}"},
            {"id": uid(), "name": "viewCount",    "type": "string", "value": "={{ $json.items[0].statistics.viewCount }}"},
            {"id": uid(), "name": "likeCount",    "type": "string", "value": "={{ $json.items[0].statistics.likeCount }}"},
            {"id": uid(), "name": "commentCount", "type": "string", "value": "={{ $json.items[0].statistics.commentCount }}"},
            {"id": uid(), "name": "description",  "type": "string", "value": "={{ $json.items[0].snippet.description }}"},
            {"id": uid(), "name": "title",        "type": "string", "value": "={{ $json.items[0].snippet.title }}"},
            {"id": uid(), "name": "channelTitle", "type": "string", "value": "={{ $json.items[0].snippet.channelTitle }}"},
            {"id": uid(), "name": "tags",         "type": "string", "value": "={{ ($json.items[0].snippet.tags||[]).join(', ') }}"},
            {"id": uid(), "name": "channelId",    "type": "string", "value": "={{ $json.items[0].snippet.channelId }}"},
        ]}, "options": {}}
    )

    n_save = make_node(
        "save_data_to_memory1",
        "n8n-nodes-base.code", 2, [560, 304],
        {"mode": "runOnceForEachItem", "jsCode": (
            "const wsd=$getWorkflowStaticData('global');\n"
            "if(typeof wsd.lastExecution!=='object')wsd.lastExecution={response:''};\n"
            "const cur={...$input.item};\n"
            "let s=JSON.stringify(cur).replace(/https?:\\/\\/\\S+/g,'').replace(/\\n/g,' ').trim();\n"
            "if(wsd.lastExecution.response)wsd.lastExecution.response+=' ### NEXT VIDEO FOUND: ### ';\n"
            "wsd.lastExecution.response+=s;\nreturn wsd.lastExecution;\n"
        )}
    )

    n_retrieve = make_node(
        "retrieve_data_from_memory1",
        "n8n-nodes-base.code", 2, [-16, 112],
        {"jsCode": (
            "const wsd=$getWorkflowStaticData('global');\n"
            "return wsd.lastExecution;"
        )}
    )

    n_resp = make_node(
        "response1",
        "n8n-nodes-base.set", 3.4, [304, 112],
        {"assignments": {"assignments": [
            {"id": uid(), "name": "response", "type": "string", "value": "={{ $input.all() }}"},
        ]}, "options": {}}
    )

    nodes = [n_trigger, n_search, n_split, n_loop,
             n_details, n_if, n_group, n_save, n_retrieve, n_resp]

    # ── connections ───────────────────────────────────────────────────────
    M = lambda n: [{"node": n, "type": "main", "index": 0}]
    connections = {
        "execute_trigger":            {"main": [M("search_youtube")]},
        "search_youtube":             {"main": [M("split_results")]},
        "split_results":              {"main": [M("loop_over_items1")]},
        "loop_over_items1":           {"main": [M("retrieve_data_from_memory1"),
                                                M("find_video_data1")]},
        "find_video_data1":           {"main": [M("if_longer_than_3_")]},
        "if_longer_than_3_":          {"main": [M("group_data1"),
                                                M("loop_over_items1")]},
        "group_data1":                {"main": [M("save_data_to_memory1")]},
        "save_data_to_memory1":       {"main": [M("loop_over_items1")]},
        "retrieve_data_from_memory1": {"main": [M("response1")]},
    }

    return {
        "name": "Youtube Search Workflow",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }


def step1_create():
    payload = build_payload()
    r = requests.post(f"{BASE}/api/v1/workflows", headers=H, json=payload)
    print(f"Create sub-workflow: {r.status_code}")
    if r.status_code not in (200, 201):
        print("Error:", r.text[:600])
        sys.exit(1)
    data = r.json()
    wf_id = data.get("id")
    print(f"  id={wf_id}  name={data.get('name')}")
    return wf_id


def step2_patch(sub_id):
    r = requests.get(f"{BASE}/api/v1/workflows/{WF62}", headers=H)
    wf = r.json()

    patched = False
    for node in wf.get("nodes", []):
        if node["name"] == "youtube_search" and "toolWorkflow" in node["type"]:
            old = node["parameters"].get("workflowId", {}).get("value", "?")
            node["parameters"]["workflowId"] = {
                "__rl": True,
                "mode": "list",
                "value": sub_id,
                "cachedResultName": "Youtube Search Workflow",
            }
            print(f"  youtube_search: {old} -> {sub_id}")
            patched = True
            break

    if not patched:
        print("ERROR: youtube_search node not found")
        sys.exit(1)


        # Send only the fields the PUT endpoint accepts
        put_body = {
            "name": wf["name"],
            "nodes": wf["nodes"],
            "connections": wf["connections"],
            "settings": wf.get("settings", {}),
        }

    r2 = requests.put(f"{BASE}/api/v1/workflows/{WF62}", headers=H, json=wf)
    print(f"PUT workflow 62: {r2.status_code}")
    if r2.status_code not in (200, 201):
        print("Error:", r2.text[:300])
        sys.exit(1)

    r3 = requests.post(f"{BASE}/api/v1/workflows/{WF62}/activate", headers=H)
    print(f"Activate: {r3.status_code}")

    check = requests.get(f"{BASE}/api/v1/workflows/{WF62}", headers=H).json()
    print(f"Verified active={check.get('active')}")
    for n in check.get("nodes", []):
        if n["name"] == "youtube_search":
            ref = n["parameters"].get("workflowId", {})
            print(f"  youtube_search -> {ref.get('value')} ({ref.get('cachedResultName')})")


print("=" * 50)
print("Step 1: Create Youtube Search sub-workflow")
print("=" * 50)
sub_id = step1_create()

print()
print("=" * 50)
print("Step 2: Patch workflow 62")
print("=" * 50)
step2_patch(sub_id)

print()
print("Done! Sub-workflow ID:", sub_id)
