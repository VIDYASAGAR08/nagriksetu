import sqlite3
import hashlib

def test_gen():
    sid = "PCMB260001"
    psid = "NS-A1B2C3D4E5F6"
    seed = int(hashlib.md5(sid.encode()).hexdigest()[:8], 16)
    print("Seed:", seed)
    
    blood_groups = ['O+', 'B+', 'A+', 'AB+', 'O-', 'A-', 'B-', 'AB-']
    bg_weights = [38, 30, 20, 7, 2, 1, 1, 1]
    bg_choice = blood_groups[seed % len(blood_groups)]
    print("Blood Group:", bg_choice)

test_gen()
