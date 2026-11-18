# -*- coding: utf-8 -*-
path = r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add import
import_marker = "import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'"
import_replacement = """import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'
import InstitutionAdminAcademicDesk from '../../components/academic/InstitutionAdminAcademicDesk.jsx'"""

if import_marker in content:
    content = content.replace(import_marker, import_replacement, 1)
    print("Import added!")
else:
    print("Import marker not found!")

# 2. Add Tab Button
tab_marker = """              {staffList.length}
            </span>
          </button>
        </div>"""

tab_replacement = """              {staffList.length}
            </span>
          </button>

          <button
            onClick={() => setMainTab('academics')}
            style={{
              padding: '0.75rem 1.4rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              border: 'none',
              background: 'none',
              borderBottom: mainTab === 'academics' ? '3px solid #155EEF' : '3px solid transparent',
              color: mainTab === 'academics' ? '#155EEF' : '#667085',
              cursor: 'pointer',
              marginBottom: '-0.35rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease'
            }}
          >
            📊 Academic Management & Oversight
          </button>
        </div>"""

if tab_marker in content:
    content = content.replace(tab_marker, tab_replacement, 1)
    print("Tab button added!")
else:
    print("Tab marker not found!")

# 3. Add Tab Content
block_marker = """            )}
          </div>
        )}

        {/* =================================================================
            APPLICATION DETAIL & REVIEW MODAL"""

block_replacement = """            )}
          </div>
        )}

        {/* =================================================================
            ACADEMIC MANAGEMENT & SUPERVISION TAB
            ================================================================= */}
        {mainTab === 'academics' && (
          <InstitutionAdminAcademicDesk
            token={token}
            institutionId={user?.school_id || overview?.institution_id}
            institutionName={overview?.institution_name || user?.school_name || 'Assigned Institution'}
          />
        )}

        {/* =================================================================
            APPLICATION DETAIL & REVIEW MODAL"""

if block_marker in content:
    content = content.replace(block_marker, block_replacement, 1)
    print("Academic tab content block added!")
else:
    print("Block marker not found!")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("InstitutionAdminDashboard.jsx updated successfully!")
