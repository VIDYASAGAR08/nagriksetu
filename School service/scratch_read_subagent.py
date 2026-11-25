import json
log_path = r'C:\Users\callm\.gemini\antigravity\brain\9dbd477c-b589-4419-ab92-38d1538ec64a\.system_generated\logs\transcript.jsonl'
with open(log_path, 'r', encoding='utf-8') as f_log:
    lines = f_log.readlines()
for l in lines[-10:]:
    d = json.loads(l)
    print(d.get('step_index'), d.get('type'), str(d.get('content'))[:100], str(d.get('tool_calls'))[:80])
