import json

with open(r'C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('step_index', 0) >= 21195:
            print(f"STEP: {data.get('step_index')} | SOURCE: {data.get('source')} | TYPE: {data.get('type')} | MEDIA: {bool(data.get('media'))}")
            if data.get('source') == 'USER_EXPLICIT' or data.get('type') == 'USER_INPUT':
                print("USER INPUT:", repr(data.get('content'))[:200])
