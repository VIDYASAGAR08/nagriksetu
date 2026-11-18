from database import get_connection
from auth import verify_password
conn = get_connection()
h = conn.execute("SELECT password_hash FROM users WHERE email = 'admin.central@nagriksetu.gov'").fetchone()['password_hash']
print("Matches Central@NagrikSetu2026!:", verify_password("Central@NagrikSetu2026!", h))
