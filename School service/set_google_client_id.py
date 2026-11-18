client_id = "749043481096-lut97cp4b3ko1hfuoslm5otqu6jkkuqh.apps.googleusercontent.com"
files = [
    r"C:\Users\callm\nagriksetu\backend\.env",
    r"C:\Users\callm\nagriksetu\backend\data\.env",
    r"C:\Users\callm\nagriksetu\.env",
]

for fpath in files:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith("GOOGLE_CLIENT_ID="):
                new_lines.append(f"GOOGLE_CLIENT_ID={client_id}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"GOOGLE_CLIENT_ID={client_id}\n")
            
        with open(fpath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"Updated {fpath}")
    except Exception as e:
        print(f"Error updating {fpath}: {e}")
