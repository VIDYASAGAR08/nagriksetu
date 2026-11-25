from app.main import app
for r in app.routes:
    if hasattr(r, 'path') and ('enrol' in r.path or 'centre' in r.path):
        print(f"{r.methods} {r.path}")
