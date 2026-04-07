import urllib.request, json, time
webhook = "https://n8n.srv953562.hstgr.cloud/webhook/ziyada-blog-ingest"
data = {"update_id":999999,"message":{"date":int(time.time()),"chat":{"id":-1001,"type":"group"},"text":"اسم الشركة: Ziyada\nالمجال: Tech\nالجمهور: Leaders\nالرابط: https://ziyada.com\nابدأ"}}
try:
    req = urllib.request.Request(webhook, data=json.dumps(data).encode(), headers={"Content-Type":"application/json"}, method="POST")
    r = urllib.request.urlopen(req)
    print(f"✓ Webhook triggered! Status: {r.status}")
    print(f"  Response: {r.read().decode()}")
except Exception as e:
    print(f"✗ Error: {e}")
