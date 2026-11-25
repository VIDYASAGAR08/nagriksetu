import json

with open(r'C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('source') == 'USER_EXPLICIT':
            print(f"STEP: {data.get('step_index')} | CONTENT: {repr(data.get('content'))[:100]} | MEDIA: {data.get('media')}")
