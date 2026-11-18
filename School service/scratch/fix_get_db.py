file_path = r"C:\Users\callm\nagriksetu\backend\main.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace Depends(get_db) with conn = get_connection()
code = code.replace("conn: sqlite3.Connection = Depends(get_db)", "# db conn")

# Now let's check functions where conn is needed
replacements = [
    (
        'def invite_staff_candidate(\n    payload: StaffCandidateInvitePayload,\n    current_user: dict = Depends(require_school_admin),\n    # db conn\n):',
        'def invite_staff_candidate(\n    payload: StaffCandidateInvitePayload,\n    current_user: dict = Depends(require_school_admin)\n):\n    conn = get_connection()'
    ),
    (
        'def list_staff_applications(\n    current_user: dict = Depends(require_school_admin),\n    # db conn\n):',
        'def list_staff_applications(\n    current_user: dict = Depends(require_school_admin)\n):\n    conn = get_connection()'
    ),
    (
        'def get_staff_application_detail(\n    application_id: str,\n    current_user: dict = Depends(require_school_admin),\n    # db conn\n):',
        'def get_staff_application_detail(\n    application_id: str,\n    current_user: dict = Depends(require_school_admin)\n):\n    conn = get_connection()'
    ),
    (
        'def request_staff_application_correction(\n    application_id: str,\n    payload: StaffCandidateCorrectionPayload,\n    current_user: dict = Depends(require_school_admin),\n    # db conn\n):',
        'def request_staff_application_correction(\n    application_id: str,\n    payload: StaffCandidateCorrectionPayload,\n    current_user: dict = Depends(require_school_admin)\n):\n    conn = get_connection()'
    ),
    (
        'def approve_staff_application(\n    application_id: str,\n    payload: StaffCandidateApprovePayload,\n    current_user: dict = Depends(require_school_admin),\n    # db conn\n):',
        'def approve_staff_application(\n    application_id: str,\n    payload: StaffCandidateApprovePayload,\n    current_user: dict = Depends(require_school_admin)\n):\n    conn = get_connection()'
    ),
    (
        'def decline_staff_application(\n    application_id: str,\n    payload: StaffCandidateDeclinePayload,\n    current_user: dict = Depends(require_school_admin),\n    # db conn\n):',
        'def decline_staff_application(\n    application_id: str,\n    payload: StaffCandidateDeclinePayload,\n    current_user: dict = Depends(require_school_admin)\n):\n    conn = get_connection()'
    ),
    (
        'def get_candidate_application(token: str = Query(...), # db conn):',
        'def get_candidate_application(token: str = Query(...)):\n    conn = get_connection()'
    ),
    (
        'def submit_candidate_application(\n    payload: StaffCandidateSubmitPayload,\n    # db conn\n):',
        'def submit_candidate_application(\n    payload: StaffCandidateSubmitPayload\n):\n    conn = get_connection()'
    ),
    (
        'def activate_approved_candidate(\n    payload: StaffCandidateActivatePayload,\n    # db conn\n):',
        'def activate_approved_candidate(\n    payload: StaffCandidateActivatePayload\n):\n    conn = get_connection()'
    ),
    (
        'def get_global_staff_monitoring(\n    institution_id: Optional[str] = None,\n    category: Optional[str] = None,\n    search: Optional[str] = None,\n    limit: int = 100,\n    current_user: dict = Depends(require_platform_admin),\n    # db conn\n):',
        'def get_global_staff_monitoring(\n    institution_id: Optional[str] = None,\n    category: Optional[str] = None,\n    search: Optional[str] = None,\n    limit: int = 100,\n    current_user: dict = Depends(require_platform_admin)\n):\n    conn = get_connection()'
    )
]

for old, new in replacements:
    assert old in code, f"Could not find:\n{old}"
    code = code.replace(old, new)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(code)

print("Fixed get_connection in main.py!")
