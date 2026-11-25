import sys
sys.path.append('C:/Users/karth/OneDrive/Documents/NagrikSetu_Skill_Development_FINAL/backend')
from app.places_registry import AUTHENTIC_REAL_WORLD_CENTRES
import json

sample_names = [
    'Simplilearn Digital Skilling Academy',
    'Aptech Computer Education',
    'Apponix Technical Skilling Centre',
    'DRDO Technical Apprentice Training Wing',
    'PMKK Electronic City',
    'IIIT-Bangalore Innovation & Skilling Centre',
    'GTTC Whitefield',
    'PMKK Whitefield',
    'Government Industrial Training Institute (ITI) Kengeri',
    'Vokkaligara Sangha Private Industrial Training Institute'
]

print("=== CHECKING TEST INSTITUTES IN AUTHENTIC_REAL_WORLD_CENTRES ===")
for name in sample_names:
    matches = [inst for inst in AUTHENTIC_REAL_WORLD_CENTRES if name.lower() in inst['name'].lower() or inst['name'].lower() in name.lower()]
    if matches:
        m = matches[0]
        print(f"FOUND: ID '{m['id']}' | '{m['name']}' | {m.get('locality')} | {m.get('phone')} | {m.get('source')}")
    else:
        print(f"NOT FOUND: '{name}'")
