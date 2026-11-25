from database import get_connection
from auth import verify_password

conn = get_connection()
h = conn.execute("SELECT password_hash FROM users WHERE email = 'admin.central@nagriksetu.gov'").fetchone()[0]

candidates = [
    'Admin@NagrikSetu2026!',
    'Platform@2026!',
    'Admin@123',
    'Password@123',
    'PlatformAdmin@2026!',
    'CentralAdmin@2026!',
    'Staff@NagrikSetu2026!',
    'NagrikSetu@2026!',
    'AdminCentral@2026!',
    'Central@NagrikSetu2026!'
]

for p in candidates:
    if verify_password(p, h):
        print('Matched password:', p)
        break
else:
    print('None matched')
