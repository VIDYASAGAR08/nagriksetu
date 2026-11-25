app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the beginning of TAB 3: PROGRAMMES & SKILLS in centre_profile
target_prog_tab = """              {/* TAB 3: PROGRAMMES & SKILLS */}
              {publicCentreTab === 'programmes' && (
                <div>
                  <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      Accredited Training Programmes Offered at this Centre
                    </h3>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {publicCentreProfile.programs?.length || 0} active courses
                    </span>
                  </div>"""

replacement_prog_tab = """              {/* TAB 3: PROGRAMMES & SKILLS */}
              {publicCentreTab === 'programmes' && (
                <div>
                  {/* Distinct Sectors and Specialisations Offered by this Centre */}
                  {publicCentreProfile.offered_categories && publicCentreProfile.offered_categories.length > 0 && (
                    <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.25rem', marginBottom: '1.5rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Compass size={16} color="#0f766e" /> Accredited Sectors Offered at this Centre:
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                        {publicCentreProfile.offered_categories.map((cat: any) => (
                          <span
                            key={cat.name}
                            style={{
                              backgroundColor: '#f0fdfa',
                              border: '1px solid #99f6e4',
                              color: '#0f766e',
                              padding: '0.25rem 0.65rem',
                              borderRadius: '20px',
                              fontSize: '0.76rem',
                              fontWeight: 700
                            }}
                          >
                            {cat.name} ({cat.program_count} programme{cat.program_count !== 1 ? 's' : ''})
                          </span>
                        ))}
                      </div>
                      {publicCentreProfile.offered_subcategories && publicCentreProfile.offered_subcategories.length > 0 && (
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          <strong>Specialisations:</strong> {publicCentreProfile.offered_subcategories.map((s: any) => s.name).join(' • ')}
                        </div>
                      )}
                    </div>
                  )}

                  <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      Accredited Training Programmes Offered at this Centre
                    </h3>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {publicCentreProfile.programs?.length || 0} active courses
                    </span>
                  </div>"""

assert target_prog_tab in content, "target_prog_tab not found"
content = content.replace(target_prog_tab, replacement_prog_tab, 1)

print("Part 4: Centre Profile offered categories and subcategories banner patched.")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
