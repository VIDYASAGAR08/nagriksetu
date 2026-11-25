import re

path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State type
content = content.replace(
    'const [activeCentreProfileId, setActiveCentreProfileId] = useState<number | null>(null);',
    'const [activeCentreProfileId, setActiveCentreProfileId] = useState<string | number | null>(null);'
)

# 2. Function signature
target_fn = """  // Open Public Training Centre Profile
  const openPublicCentreProfile = async (cId: number) => {
    setActiveCentreProfileId(cId);
    setPublicCentreLoading(true);
    setPublicCentreTab('overview');
    setActiveTab('centre_profile');
    try {
      const res = await fetch(`${API_BASE}/api/centres/${cId}/profile`);"""

repl_fn = """  // Open Public Training Centre Profile
  const openPublicCentreProfile = async (cId: string | number) => {
    setActiveCentreProfileId(cId);
    setPublicCentreLoading(true);
    setPublicCentreTab('overview');
    setActiveTab('centre_profile');
    try {
      const res = await fetch(`${API_BASE}/api/centres/${encodeURIComponent(String(cId))}/profile`);"""

if target_fn in content:
    content = content.replace(target_fn, repl_fn)
    print("Found and replaced openPublicCentreProfile")
else:
    print("Could not find openPublicCentreProfile")

# 3. Card button
target_card = """        {/* Bottom Action Buttons: Full Institutional Profile + View on Map */}
        <div style={{ marginTop: '1.25rem', borderTop: '1px solid #f1f5f9', paddingTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {c.is_official_centre !== false && c.id && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                openPublicCentreProfile(c.id);
              }}"""

repl_card = """        {/* Bottom Action Buttons: Full Institutional Profile + View on Map */}
        <div style={{ marginTop: '1.25rem', borderTop: '1px solid #f1f5f9', paddingTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {(c.id || c.code || c.place_id) && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                openPublicCentreProfile(c.id || c.code || c.place_id);
              }}"""

if target_card in content:
    content = content.replace(target_card, repl_card)
    print("Found and replaced renderCentreCard button")
else:
    print("Could not find renderCentreCard button")

# 4. Profile view programmes tab button
# If official centre: "Apply for this Course"
# If external institute: "Contact Institute Directly" or link
target_apply = """                          <button
                            type="button"
                            onClick={() => {
                              setEnrollingProgram(p);
                              if (p.batches && p.batches.length > 0) {
                                setSelectedBatchId(p.batches[0].id);
                              }
                            }}
                            style={{
                              width: '100%',
                              padding: '0.65rem 1rem',
                              backgroundColor: '#ea580c',
                              color: '#ffffff',
                              border: 'none',
                              borderRadius: '6px',
                              fontWeight: 700,
                              fontSize: '0.85rem',
                              cursor: 'pointer'
                            }}
                          >
                            Apply for this Course
                          </button>"""

repl_apply = """                          {publicCentreProfile.is_official_centre !== false ? (
                            <button
                              type="button"
                              onClick={() => {
                                setEnrollingProgram(p);
                                if (p.batches && p.batches.length > 0) {
                                  setSelectedBatchId(p.batches[0].id);
                                }
                              }}
                              style={{
                                width: '100%',
                                padding: '0.65rem 1rem',
                                backgroundColor: '#ea580c',
                                color: '#ffffff',
                                border: 'none',
                                borderRadius: '6px',
                                fontWeight: 700,
                                fontSize: '0.85rem',
                                cursor: 'pointer'
                              }}
                            >
                              Apply for this Course
                            </button>
                          ) : (
                            <div style={{ display: 'grid', gap: '0.5rem' }}>
                              <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic', textAlign: 'center' }}>
                                Verified External Directory Programme • Direct Institutional Admission
                              </div>
                              {publicCentreProfile.website && (
                                <a
                                  href={publicCentreProfile.website}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    display: 'block',
                                    textAlign: 'center',
                                    padding: '0.65rem 1rem',
                                    backgroundColor: '#0f766e',
                                    color: '#ffffff',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    fontSize: '0.85rem',
                                    textDecoration: 'none'
                                  }}
                                >
                                  Visit Institute Website
                                </a>
                              )}
                            </div>
                          )}"""

if target_apply in content:
    content = content.replace(target_apply, repl_apply)
    print("Found and replaced apply button in profile")
else:
    print("Could not find apply button in profile")

# 5. Add Source Directory Badge in Profile Hero Banner
target_banner_badges = """                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '2px 8px', borderRadius: '4px' }}>
                          {publicCentreProfile.code}
                        </span>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#15803d', backgroundColor: '#dcfce7', padding: '2px 8px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 size={12} /> {publicCentreProfile.approval_status || 'ACCREDITED & VERIFIED'}
                        </span>"""

repl_banner_badges = """                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: publicCentreProfile.is_official_centre !== false ? '#0f766e' : '#1e40af', backgroundColor: publicCentreProfile.is_official_centre !== false ? '#ccfbf1' : '#dbeafe', padding: '2px 8px', borderRadius: '4px' }}>
                          {publicCentreProfile.code}
                        </span>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#15803d', backgroundColor: '#dcfce7', padding: '2px 8px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 size={12} /> {publicCentreProfile.approval_status || 'ACCREDITED & VERIFIED'}
                        </span>
                        {publicCentreProfile.source && (
                          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#7c3aed', backgroundColor: '#f3e8ff', padding: '2px 8px', borderRadius: '4px' }}>
                            Source: {publicCentreProfile.source}
                          </span>
                        )}"""

if target_banner_badges in content:
    content = content.replace(target_banner_badges, repl_banner_badges)
    print("Found and replaced banner badges")
else:
    print("Could not find banner badges")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Update completed successfully.")
