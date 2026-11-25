import os
import zipfile

src_dir = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL"
zip_path = r"C:\Users\karth\OneDrive\Documents\NAGRIKSETU_SKILL_DEVELOPMENT_FINAL.zip"

exclude_dirs = {"node_modules", ".git", "__pycache__", ".pytest_cache", "dist_old", ".venv", "venv"}
exclude_extensions = {".pyc", ".pyo", ".log"}

count = 0
total_bytes = 0

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_extensions:
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, src_dir)
            zipf.write(full_path, rel_path)
            count += 1
            total_bytes += os.path.getsize(full_path)

print(f"Packaged {count} files into {zip_path}")
print(f"Total uncompressed size: {total_bytes / (1024*1024):.2f} MB")
print(f"Compressed archive size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
