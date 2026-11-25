import json

log_file = r"C:\Users\callm\.gemini\antigravity\brain\010bed14-ca45-4c39-a172-471440a90a20\.system_generated\logs\transcript.jsonl"
with open(log_file, "rb") as f:
    f.seek(0, 2)
    size = f.tell()
    f.seek(max(0, size - 200000))
    lines = f.readlines()

for line in lines:
    try:
        obj = json.loads(line)
        if 21945 <= obj.get("step_index", 0) <= 21955:
            print(f"STEP: {obj.get('step_index')}, SOURCE: {obj.get('source')}, TYPE: {obj.get('type')}, MEDIA: {len(obj.get('media', []))}")
            if obj.get("content"):
                print("CONTENT:", repr(obj.get("content"))[:200])
    except Exception as e:
        pass
