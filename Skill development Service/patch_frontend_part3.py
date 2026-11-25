app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Platform Admin Dashboard sub-tabs to include "Skill Hierarchy & Centre Matrix"
old_admin_tabs = """          {/* Admin Sub-Tabs Navigation */}
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem' }}>
            <button
              className={`nav-item-btn ${adminTab === 'applications' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('applications')}
            >
              Citizen Applications Queue ({adminEnrollments.length})
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'skills' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('skills')}
            >
              Skill Catalogue Management
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'programmes' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('programmes')}
            >
              Training Programmes & Batches
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'centres' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('centres')}
            >
              Training Centres
            </button>
          </div>"""

new_admin_tabs = """          {/* Admin Sub-Tabs Navigation */}
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', flexWrap: 'wrap' }}>
            <button
              className={`nav-item-btn ${adminTab === 'applications' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('applications')}
            >
              Citizen Applications Queue ({adminEnrollments.length})
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'hierarchy' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem', backgroundColor: adminTab === 'hierarchy' ? '#0f2444' : '#f8fafc', color: adminTab === 'hierarchy' ? '#ffffff' : '#0f2444', border: '1.5px solid #0f2444' }}
              onClick={() => { setAdminTab('hierarchy'); fetchAdminCatalogueSummary(); }}
            >
              Catalogue Hierarchy & Centre Linkage
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'skills' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('skills')}
            >
              Skill Catalogue Directory
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'programmes' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('programmes')}
            >
              Training Programmes & Batches
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'centres' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('centres')}
            >
              Training Centres
            </button>
          </div>"""

assert old_admin_tabs in content, "old_admin_tabs not found"
content = content.replace(old_admin_tabs, new_admin_tabs, 1)

# 2. Add the TAB content for adminTab === 'hierarchy'
hierarchy_tab_content = """          {/* TAB: CATALOGUE HIERARCHY & TRAINING CENTRE MATRIX (Platform Admin Read-Only) */}
          {adminTab === 'hierarchy' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Layers size={22} color="#0284c7" /> Skill Hierarchy & Centre Affiliation Matrix
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    Read-only monitoring of the 7 main accredited sectors, 36 subcategories, 228 industry skills, and registered training centre offerings.
                  </p>
                </div>
                <button
                  type="button"
                  className="btn-navy-outline"
                  onClick={fetchAdminCatalogueSummary}
                  disabled={adminCatalogueLoading}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}
                >
                  <RefreshCw size={14} className={adminCatalogueLoading ? 'animate-spin' : ''} /> Refresh Catalogue
                </button>
              </div>

              {adminCatalogueLoading && !adminCatalogueData ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                  <Loader2 size={32} className="animate-spin" style={{ margin: '0 auto 1rem auto', color: '#0284c7' }} />
                  Loading comprehensive catalogue hierarchy from MySQL...
                </div>
              ) : adminCatalogueData ? (
                <div style={{ display: 'grid', gap: '1.75rem' }}>
                  {/* Summary Metric Counters */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                    <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1e3a8a' }}>{adminCatalogueData.total_categories}</div>
                      <div style={{ fontSize: '0.78rem', color: '#2563eb', fontWeight: 600 }}>Main Industry Sectors</div>
                    </div>
                    <div style={{ backgroundColor: '#faf5ff', border: '1px solid #e9d5ff', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#6b21a8' }}>{adminCatalogueData.total_subcategories}</div>
                      <div style={{ fontSize: '0.78rem', color: '#9333ea', fontWeight: 600 }}>Specialised Subcategories</div>
                    </div>
                    <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#14532d' }}>{adminCatalogueData.total_skills}</div>
                      <div style={{ fontSize: '0.78rem', color: '#16a34a', fontWeight: 600 }}>Total Accredited Skills</div>
                    </div>
                  </div>

                  {/* Categories & Subcategories Accordion / Listing */}
                  <div style={{ display: 'grid', gap: '1.25rem' }}>
                    {adminCatalogueData.categories?.map((cat: any) => (
                      <div key={cat.category_id} style={{ border: '1.5px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                        <div style={{ backgroundColor: '#f8fafc', padding: '1rem 1.25rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0284c7', backgroundColor: '#e0f2fe', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                              {cat.category_code}
                            </span>
                            <strong style={{ fontSize: '1.1rem', color: '#0f2444' }}>{cat.category_name}</strong>
                          </div>
                          <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.78rem', color: '#475569' }}>
                            <span><strong>{cat.subcategories_count}</strong> Subcategories</span>
                            <span>•</span>
                            <span><strong>{cat.total_skills}</strong> Skills</span>
                            <span>•</span>
                            <span><strong>{cat.total_programmes}</strong> Live Programmes</span>
                          </div>
                        </div>

                        <div style={{ padding: '1.25rem', display: 'grid', gap: '1rem' }}>
                          {cat.subcategories?.map((sub: any) => (
                            <div key={sub.subcategory_id} style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#64748b', backgroundColor: '#f1f5f9', padding: '0.15rem 0.45rem', borderRadius: '3px' }}>
                                    {sub.subcategory_code}
                                  </span>
                                  <span style={{ fontWeight: 700, color: '#0f172a', fontSize: '0.95rem' }}>{sub.subcategory_name}</span>
                                </div>
                                <span style={{ fontSize: '0.75rem', color: '#0284c7', fontWeight: 700, backgroundColor: '#f0f9ff', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                                  {sub.skills_count} Skills Configured
                                </span>
                              </div>

                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem' }}>
                                {sub.skills?.map((sk: any) => (
                                  <div key={sk.skill_id} style={{ backgroundColor: '#f8fafc', border: '1px solid #f1f5f9', borderRadius: '6px', padding: '0.75rem', fontSize: '0.8rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                                      <strong style={{ color: '#0f2444' }}>{sk.skill_name}</strong>
                                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{sk.level}</span>
                                    </div>
                                    <div style={{ fontSize: '0.74rem', color: '#64748b', marginBottom: '0.5rem' }}>
                                      Duration: {sk.duration_hours}h • {sk.has_programmes ? `${sk.programmes_count} live programme(s)` : 'No live batches currently'}
                                    </div>
                                    {sk.centres_offering?.length > 0 ? (
                                      <div style={{ fontSize: '0.72rem', color: '#0f766e', backgroundColor: '#f0fdfa', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #ccfbf1' }}>
                                        <strong>Offered by:</strong> {sk.centres_offering.map((co: any) => co.centre_name.split('(')[0].trim()).join(', ')}
                                      </div>
                                    ) : (
                                      <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontStyle: 'italic' }}>
                                        Curriculum registered; awaiting centre batch scheduling
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}

"""

target_insert_admin = "{/* TAB 1: APPLICATIONS QUEUE */}"
assert target_insert_admin in content, "target_insert_admin not found"
content = content.replace(target_insert_admin, hierarchy_tab_content + "\n          " + target_insert_admin, 1)

print("Part 3: Admin Hierarchy tab patched.")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
