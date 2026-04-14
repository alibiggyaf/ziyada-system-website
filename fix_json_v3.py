import json

with open('final_payload.json', 'r') as f:
    text = f.read()

# Print first 200 chars to debug
print(text[:200])
