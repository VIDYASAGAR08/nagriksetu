with open(r'C:\Users\callm\nagriksetu\update_desk.py', 'r', encoding='utf-8') as f:
    orig_text = f.read()

subtab2_marker = "{/* SUB-TAB 2: DATA CORRECTION REQUESTS */}"
modal1_marker = "{/* MODAL 1: OFFICIAL VERIFICATION CODE ISSUED"
modal3_marker = "{/* MODAL 3: DATA CORRECTION REVIEW MODAL */}"

subtab2_idx = orig_text.find(subtab2_marker)
modal1_idx = orig_text.find(modal1_marker)
modal3_idx = orig_text.find(modal3_marker)

subtab2_body = orig_text[subtab2_idx:modal1_idx]
modal3_body = orig_text[modal3_idx:]

with open(r'C:\Users\callm\nagriksetu\patch_institution_desk.py', 'r', encoding='utf-8') as f:
    patch_code = f.read()

# Extract top_half and new_linking_modals from patch_institution_desk.py
top_half_marker = 'top_half = """'
new_modals_marker = 'new_linking_modals = """'

top_start = patch_code.find(top_half_marker) + len(top_half_marker)
top_end = patch_code.find('"""\n\n# Now build the new modals')

modals_start = patch_code.find(new_modals_marker) + len(new_modals_marker)
modals_end = patch_code.find('"""\n\nsubtab2_content = text[subtab2_idx:modal1_idx]')

top_half = patch_code[top_start:top_end]
new_linking_modals = patch_code[modals_start:modals_end]

final_content = top_half + subtab2_body + new_linking_modals + modal3_body

with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("InstitutionParentRequestsDesk.jsx correctly stitched together.")
