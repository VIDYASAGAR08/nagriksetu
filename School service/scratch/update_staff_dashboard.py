# -*- coding: utf-8 -*-
path = r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import
import_marker = "import AdmissionDeskTab from '../../components/admissions/AdmissionDeskTab.jsx'"
import_replacement = """import AdmissionDeskTab from '../../components/admissions/AdmissionDeskTab.jsx'
import StaffAcademicDesk from '../../components/academic/StaffAcademicDesk.jsx'"""

if import_marker in content:
    content = content.replace(import_marker, import_replacement, 1)
    print("Import added!")
else:
    print("Import marker not found!")

# 2. Add Tab Button
btn_marker = """            {(isSchoolAdmin || permissions.can_manage_academics) && (
              <button
                onClick={() => setActiveTab('program-distribution')}
                className={`btn btn--sm ${activeTab === 'program-distribution' ? 'btn--accent' : 'btn--ghost'}`}
                style={{ fontWeight: 600 }}
              >
                📊 Programme Distribution
              </button>
            )}"""

btn_replacement = """            {(isSchoolAdmin || permissions.can_manage_academics) && (
              <button
                onClick={() => setActiveTab('program-distribution')}
                className={`btn btn--sm ${activeTab === 'program-distribution' ? 'btn--accent' : 'btn--ghost'}`}
                style={{ fontWeight: 600 }}
              >
                📊 Programme Distribution
              </button>
            )}
            <button
              onClick={() => setActiveTab('academics')}
              className={`btn btn--sm ${activeTab === 'academics' ? 'btn--accent' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              📝 Academic & Attendance Desk
            </button>"""

if btn_marker in content:
    content = content.replace(btn_marker, btn_replacement, 1)
    print("Tab button added!")
else:
    print("Tab button marker not found!")

# 3. Add Tab Content
content_marker = """              </div>
            )}
          </div>
        )}

        {/* Review & Approval Modal */}"""

content_replacement = """              </div>
            )}
          </div>
        )}

        {/* Tab: Academic & Attendance Desk */}
        {activeTab === 'academics' && (
          <StaffAcademicDesk
            token={token}
            schoolId={assignedSchoolId}
            institutionName={schoolInfo?.school_name || assignedSchoolId}
          />
        )}

        {/* Review & Approval Modal */}"""

if content_marker in content:
    content = content.replace(content_marker, content_replacement, 1)
    print("Academic desk view added!")
else:
    print("Content marker not found!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("StaffDashboard.jsx updated successfully!")
