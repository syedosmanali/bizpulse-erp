"""Inspect Ajay user in local DB to find credentials and permissions."""
import sys
import os
# Ensure project root is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.shared.database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()
cur.execute("SELECT id, full_name, username, temp_password, module_permissions, role_id FROM user_accounts WHERE username LIKE '%ajay%' OR full_name LIKE '%ajay%'")
rows = cur.fetchall()
if not rows:
    print('No Ajay user found')
else:
    for r in rows:
        print('id:', r[0])
        print('full_name:', r[1])
        print('username:', r[2])
        print('temp_password:', r[3])
        print('module_permissions:', r[4])
        print('role_id:', r[5])
        print('---')
conn.close()