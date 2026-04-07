#!/usr/bin/env python3
import requests

BASE = "https://n8n.srv953562.hstgr.cloud"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMTU5ZDRmNC03MTExLTQ4NTAtOGQ5OC0yYWM1MzU1Mjg3ZWUiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzczOTM3NjU5LCJleHAiOjE3ODE2NDcyMDB9.57H2mbac54qiRQusl37xQXlnfYYRNvJ3-lm4crYBlqA"
WF = "INHDUWqaC4WMae1R"


def main() -> None:
	get_headers = {"X-N8N-API-KEY": KEY}
	put_headers = {"X-N8N-API-KEY": KEY, "Content-Type": "application/json"}

	r = requests.get(f"{BASE}/api/v1/workflows/{WF}", headers=get_headers, timeout=30)
	r.raise_for_status()
	wf = r.json()

	for node in wf.get("nodes", []):
		if node.get("name") == "search_youtube":
			node["parameters"] = {
				"url": "https://r.jina.ai/http://www.youtube.com/results",
				"method": "GET",
				"sendQuery": True,
				"queryParameters": {
					"parameters": [
						{
							"name": "search_query",
							"value": "={{ (() => { const q = $json.search_term ?? $json.query ?? $json.chatInput ?? $json.input ?? 'YouTube trends'; return typeof q === 'string' ? q : JSON.stringify(q); })() }}",
						}
					]
				},
				"options": {
					"response": {
						"response": {
							"responseFormat": "text"
						}
					}
				},
			}
		elif node.get("name") == "split_results":
			node["parameters"]["jsCode"] = (
				"const src = $input.first().json;\n"
				"const rawValue = src.data ?? src.body ?? src.response ?? src.text ?? src;\n"
				"const raw = typeof rawValue === 'string' ? rawValue : JSON.stringify(rawValue);\n"
				"const rows = [];\n"
				"const seen = new Set();\n"
				"const pairRe = /\\[([^\\]\\n]{5,180})\\]\\(https?:\\/\\/www\\.youtube\\.com\\/watch\\?v=([\\w-]{11})[^)]*\\)/g;\n"
				"let p;\n"
				"while ((p = pairRe.exec(raw)) !== null) {\n"
				"  const title = p[1].replace(/\\s+/g, ' ').trim();\n"
				"  const id = p[2];\n"
				"  if (!seen.has(id) && !/^Image\\s+\\d+$/i.test(title)) {\n"
				"    seen.add(id);\n"
				"    rows.push({ id, title });\n"
				"  }\n"
				"  if (rows.length >= 5) break;\n"
				"}\n"
				"if (rows.length === 0) {\n"
				"  const ids = [];\n"
				"  const idRe = /watch\\?v=([\\w-]{11})/g;\n"
				"  let m;\n"
				"  while ((m = idRe.exec(raw)) !== null) {\n"
				"    if (!ids.includes(m[1])) ids.push(m[1]);\n"
				"    if (ids.length >= 5) break;\n"
				"  }\n"
				"  if (ids.length === 0) {\n"
				"    return [{ json: { id: { videoId: '' }, snippet: { title: 'No matching videos found', description: 'Search source returned no parsable results.', channelTitle: 'YouTube', channelId: '' } } }];\n"
				"  }\n"
				"  return ids.map((id, idx) => ({ json: { id: { videoId: id }, snippet: { title: `YouTube result ${idx + 1}`, description: `Result for query: ${$json.search_term || $json.query || 'YouTube trends'}`, channelTitle: 'YouTube', channelId: '' } } }));\n"
				"}\n"
				"return rows.map((row) => ({\n"
				"  json: {\n"
				"    id: { videoId: row.id },\n"
				"    snippet: {\n"
				"      title: row.title,\n"
				"      description: `Result for query: ${$json.search_term || $json.query || 'YouTube trends'}`,\n"
				"      channelTitle: 'YouTube',\n"
				"      channelId: ''\n"
				"    }\n"
				"  }\n"
				"}));"
			)
		elif node.get("name") == "group_data1":
			node["parameters"] = {
				"assignments": {
					"assignments": [
						{"name": "id", "type": "string", "value": '={{ $json.id?.videoId || $json.id || "" }}'},
						{"name": "viewCount", "type": "string", "value": "n/a"},
						{"name": "likeCount", "type": "string", "value": "n/a"},
						{"name": "commentCount", "type": "string", "value": "n/a"},
						{"name": "description", "type": "string", "value": '={{ $json.snippet?.description || "" }}'},
						{"name": "title", "type": "string", "value": '={{ $json.snippet?.title || "" }}'},
						{"name": "channelTitle", "type": "string", "value": '={{ $json.snippet?.channelTitle || "" }}'},
						{"name": "tags", "type": "string", "value": ""},
						{"name": "channelId", "type": "string", "value": '={{ $json.snippet?.channelId || "" }}'},
						{"name": "url", "type": "string", "value": '={{ $json.id?.videoId ? "https://www.youtube.com/watch?v=" + $json.id.videoId : "" }}'},
					]
				},
				"options": {},
			}

	wf["connections"]["loop_over_items1"] = {
		"main": [
			[{"node": "retrieve_data_from_memory1", "type": "main", "index": 0}],
			[{"node": "group_data1", "type": "main", "index": 0}],
		]
	}
	wf["connections"]["group_data1"] = {
		"main": [[{"node": "save_data_to_memory1", "type": "main", "index": 0}]]
	}
	wf["connections"]["save_data_to_memory1"] = {
		"main": [[{"node": "loop_over_items1", "type": "main", "index": 0}]]
	}

	payload = {k: wf.get(k) for k in ["name", "nodes", "connections", "settings"]}
	up = requests.put(f"{BASE}/api/v1/workflows/{WF}", headers=put_headers, json=payload, timeout=30)
	print("PUT", up.status_code)
	print(up.text[:300])

	act = requests.post(f"{BASE}/api/v1/workflows/{WF}/activate", headers=get_headers, timeout=30)
	print("ACT", act.status_code)


if __name__ == "__main__":
	main()
