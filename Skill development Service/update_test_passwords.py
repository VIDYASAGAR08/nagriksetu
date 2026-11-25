path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\test_comprehensive_regression.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_block = """CENTRES = [
    (1, "centre.bengaluru@nagriksetu.local", "Blr#w$Qr%m9@!", "Bengaluru Central Skill Hub (Rajajinagar)"),
    (2, "centre.admin.mysuru@nagriksetu.local", "Mys#kxUERTN4!", "Mysuru Regional Skilling Institute"),
    (3, "centre.admin.hubballi@nagriksetu.local", "Hub#ukl2Lk$y!", "Hubballi-Dharwad Tech Development Centre"),
    (4, "centre.admin.mangaluru@nagriksetu.local", "Mng#HAFHUM%5!", "Mangaluru Coastal Technology Institute"),
    (5, "centre.virtual@nagriksetu.local", "Vrt#@G%gfJXm!", "Karnataka Virtual Skill Academy (Online)"),
    (6, "centre.dharwad@nagriksetu.local", "Dhw#EdspKs6c!", "Dharwad Agricultural Technology & Rural Skilling Centre"),
    (8, "centre.belagavi@nagriksetu.local", "Blg#7T%PxYtj!", "Belagavi Manufacturing & Precision Engineering Centre"),
    (9, "centre.davanagere@nagriksetu.local", "Dvg#K6@W#7W$!", "Davanagere Textile & Agro-Industry Vocational Institute"),
    (10, "centre.kalaburagi@nagriksetu.local", "Klb##hPdqEA7!", "Kalaburagi Regional Skill Development Centre"),
    (11, "centre.shivamogga@nagriksetu.local", "Shv#j5E!5Ls0!", "Shivamogga Malnad Skill & Electronics Centre"),
]"""

new_block = """CENTRES = [
    (1, "centre.bengaluru@nagriksetu.local", "BengaluruHub#2026", "Bengaluru Central Skill Hub (Rajajinagar)"),
    (2, "centre.admin.mysuru@nagriksetu.local", "MysuruSkill#2026", "Mysuru Regional Skilling Institute"),
    (3, "centre.admin.hubballi@nagriksetu.local", "HubballiTech#2026", "Hubballi-Dharwad Tech Development Centre"),
    (4, "centre.admin.mangaluru@nagriksetu.local", "MangaluruSea#2026", "Mangaluru Coastal Skill Academy"),
    (5, "centre.virtual@nagriksetu.local", "VirtualLearn#2026", "NagrikSetu Virtual Learning Portal"),
    (6, "centre.dharwad@nagriksetu.local", "DharwadInno#2026", "Dharwad Innovation & Regional Skilling Centre"),
    (8, "centre.belagavi@nagriksetu.local", "BelagaviHub#2026", "Belagavi Regional Skilling Hub"),
    (9, "centre.davanagere@nagriksetu.local", "DavanagereVoc#2026", "Davanagere Vocational & Technical Institute"),
    (10, "centre.kalaburagi@nagriksetu.local", "KalaburagiDev#2026", "Kalaburagi Regional Skill Development Centre"),
    (11, "centre.shivamogga@nagriksetu.local", "ShivamoggaMal#2026", "Shivamogga Malnad Skill Development Centre"),
]"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("test_comprehensive_regression.py updated with new permanent passwords.")
else:
    print("Could not find old_block in test_comprehensive_regression.py")
