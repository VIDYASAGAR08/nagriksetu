app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Enhance metric badges in Category Details to include subcategories count
old_badges = """                {/* Category Metric Badges */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', paddingTop: '1.25rem', borderTop: '1px solid #f1f5f9' }}>
                  <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1e3a8a' }}>{categoryDetailsData.stats.total_skills}</div>
                    <div style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 600 }}>Skills Available</div>
                  </div>
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#14532d' }}>{categoryDetailsData.stats.total_programmes}</div>
                    <div style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: 600 }}>Training Programmes</div>
                  </div>
                  <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#7c2d12' }}>{categoryDetailsData.stats.total_centres}</div>
                    <div style={{ fontSize: '0.75rem', color: '#ea580c', fontWeight: 600 }}>Registered Training Centres</div>
                  </div>
                </div>"""

new_badges = """                {/* Category Metric Badges */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', paddingTop: '1.25rem', borderTop: '1px solid #f1f5f9' }}>
                  <div style={{ backgroundColor: '#faf5ff', border: '1px solid #e9d5ff', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#6b21a8' }}>{categoryDetailsData.subcategories?.length || categoryDetailsData.stats.total_subcategories || 5}</div>
                    <div style={{ fontSize: '0.75rem', color: '#9333ea', fontWeight: 600 }}>Subcategories</div>
                  </div>
                  <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1e3a8a' }}>{categoryDetailsData.stats.total_skills}</div>
                    <div style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 600 }}>Skills Available</div>
                  </div>
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#14532d' }}>{categoryDetailsData.stats.total_programmes}</div>
                    <div style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: 600 }}>Training Programmes</div>
                  </div>
                  <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#7c2d12' }}>{categoryDetailsData.stats.total_centres}</div>
                    <div style={{ fontSize: '0.75rem', color: '#ea580c', fontWeight: 600 }}>Registered Training Centres</div>
                  </div>
                </div>"""

assert old_badges in content, "old_badges not found"
content = content.replace(old_badges, new_badges, 1)

# 2. Add Subcategory Selector & Filtering in category_details
old_skills_section = """              {/* Sub-Section 2: Skills Curriculum Included in This Category */}
              <div>
                <div className="section-header" style={{ marginBottom: '1.25rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.25rem 0' }}>
                      Skills & Learning Modules in {categoryDetailsData.category.name}
                    </h3>
                    <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                      Accredited technical skills with certified learning outcomes and modular syllabi.
                    </p>
                  </div>
                </div>

                <div className="cards-grid">
                  {categoryDetailsData.skills.map((s: any) => (
                    <div key={s.code} className="skill-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <span className="badge-category">{s.category_name}</span>
                        <span className={`badge-level ${s.level.toLowerCase()}`}>{s.level}</span>
                      </div>
                      <h3>{s.name}</h3>
                      <p className="summary">{s.summary}</p>
                      <div className="card-meta-row">
                        <span className="meta-item"><Clock size={14} /> {s.duration_hours} Hours ({s.duration_weeks} wks)</span>
                        <span className="meta-item"><Users size={14} /> {s.enrolled_count} Enrolled</span>
                      </div>
                      <button className="btn-card-action" onClick={() => openCourseDetail(s.code)}>
                        View Skill Details <ArrowRight size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>"""

new_skills_section = """              {/* Sub-Section 2: Subcategories & Skills Hierarchy */}
              <div style={{ marginBottom: '3rem' }}>
                <div className="section-header" style={{ marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.25rem 0' }}>
                      Accredited Subcategories & Specialisations
                    </h3>
                    <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                      Explore domain-specific specialisations. Click a subcategory to filter and view its accredited skills.
                    </p>
                  </div>
                </div>

                {/* Subcategories Pills / Filter Bar */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', marginBottom: '1.5rem' }}>
                  <button
                    type="button"
                    onClick={() => setSelectedSubcategoryId(null)}
                    style={{
                      padding: '0.45rem 0.9rem',
                      borderRadius: '20px',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      border: '1.5px solid',
                      backgroundColor: selectedSubcategoryId === null ? '#0f2444' : '#ffffff',
                      color: selectedSubcategoryId === null ? '#ffffff' : '#475569',
                      borderColor: selectedSubcategoryId === null ? '#0f2444' : '#cbd5e1',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    All Subcategories ({categoryDetailsData.skills?.length || 0} Skills)
                  </button>
                  {categoryDetailsData.subcategories?.map((sub: any) => (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => setSelectedSubcategoryId(selectedSubcategoryId === sub.id ? null : sub.id)}
                      style={{
                        padding: '0.45rem 0.9rem',
                        borderRadius: '20px',
                        fontSize: '0.82rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        border: '1.5px solid',
                        backgroundColor: selectedSubcategoryId === sub.id ? '#ea580c' : '#ffffff',
                        color: selectedSubcategoryId === sub.id ? '#ffffff' : '#334155',
                        borderColor: selectedSubcategoryId === sub.id ? '#ea580c' : '#cbd5e1',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      {sub.name} ({sub.skill_count || sub.skills?.length || 0})
                    </button>
                  ))}
                </div>

                {/* Skills Grid filtered by subcategory */}
                <div className="cards-grid">
                  {(categoryDetailsData.skills || [])
                    .filter((s: any) => selectedSubcategoryId === null || s.subcategory_id === selectedSubcategoryId)
                    .map((s: any) => (
                      <div key={s.code} className="skill-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <span className="badge-category">{s.subcategory_name || s.category_name}</span>
                          <span className={`badge-level ${s.level.toLowerCase()}`}>{s.level}</span>
                        </div>
                        <h3>{s.name}</h3>
                        <p className="summary">{s.summary}</p>
                        <div className="card-meta-row">
                          <span className="meta-item"><Clock size={14} /> {s.duration_hours} Hours ({s.duration_weeks} wks)</span>
                          <span className="meta-item"><Users size={14} /> {s.enrolled_count} Enrolled</span>
                        </div>
                        <button className="btn-card-action" onClick={() => openCourseDetail(s.code)}>
                          View Skill Details <ArrowRight size={14} />
                        </button>
                      </div>
                    ))}
                </div>
              </div>"""

assert old_skills_section in content, "old_skills_section not found"
content = content.replace(old_skills_section, new_skills_section, 1)

print("Part 2: Category Details subcategories selector patched.")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
