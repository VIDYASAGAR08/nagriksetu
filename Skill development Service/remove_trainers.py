path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove 'trainers' from activeTab type union
old_active_tab = "const [activeTab, setActiveTab] = useState<'home' | 'explore_skills' | 'category_details' | 'courses' | 'programmes' | 'trainers' | 'centres' | 'centre_profile' | 'applications' | 'profile' | 'gap' | 'certificates'>('home');"
new_active_tab = "const [activeTab, setActiveTab] = useState<'home' | 'explore_skills' | 'category_details' | 'courses' | 'programmes' | 'centres' | 'centre_profile' | 'applications' | 'profile' | 'gap' | 'certificates'>('home');"

if old_active_tab in content:
    content = content.replace(old_active_tab, new_active_tab)
    print("1. Updated activeTab state type")
else:
    print("1. Could not find old_active_tab")

# 2. Remove Trainers navigation button
old_nav_btn = """            <button className={`nav-item-btn ${activeTab === 'programmes' ? 'active' : ''}`} onClick={() => { setActiveTab('programmes'); setMobileMenuOpen(false); }}>
              {t('nav.training_programmes')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'trainers' ? 'active' : ''}`} onClick={() => { setActiveTab('trainers'); setMobileMenuOpen(false); }}>
              {t('nav.trainers')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'centres' ? 'active' : ''}`} onClick={() => { setActiveTab('centres'); setMobileMenuOpen(false); }}>"""

new_nav_btn = """            <button className={`nav-item-btn ${activeTab === 'programmes' ? 'active' : ''}`} onClick={() => { setActiveTab('programmes'); setMobileMenuOpen(false); }}>
              {t('nav.training_programmes')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'centres' ? 'active' : ''}`} onClick={() => { setActiveTab('centres'); setMobileMenuOpen(false); }}>"""

if old_nav_btn in content:
    content = content.replace(old_nav_btn, new_nav_btn)
    print("2. Removed Trainers button from navigation bar")
else:
    print("2. Could not find old_nav_btn")

# 3. Remove public Trainers section
old_section = """      {/* TRAINERS PROFILES */}
      {activeTab === 'trainers' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('sections.trainers_heading')}</h2>
              <p>Government certified Master Trainers and senior technology mentors</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
            {trainers.map((t: any) => (
              <div key={t.code} style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                  <div style={{ width: '50px', height: '50px', borderRadius: '50%', backgroundColor: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0f2444' }}>
                    <User size={24} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>{t.name}</h3>
                    <span style={{ fontSize: '0.78rem', color: '#ea580c', fontWeight: 600 }}>{t.specialisation}</span>
                  </div>
                </div>
                <p style={{ fontSize: '0.82rem', color: '#475569', marginBottom: '0.75rem' }}>
                  <strong>Qualification:</strong> {t.qualification}
                </p>
                <div style={{ fontSize: '0.8rem', color: '#64748b', borderTop: '1px solid #f1f5f9', paddingTop: '0.75rem' }}>
                  <div><strong>Experience:</strong> {t.experience_years} Years Industry Practice</div>
                  <div><strong>Assigned Centre:</strong> {t.centre_name}</div>
                  <div><strong>Schedule Availability:</strong> {t.availability}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ACCREDITED TRAINING CENTRES & REAL-WORLD DISCOVERY */}"""

new_section = """      {/* ACCREDITED TRAINING CENTRES & REAL-WORLD DISCOVERY */}"""

if old_section in content:
    content = content.replace(old_section, new_section)
    print("3. Removed public Trainers section from App.tsx")
else:
    print("3. Could not find old_section")

# 4. Remove footer shortcut link to trainers
old_footer = """                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('courses')}>Explore 100+ Skill Courses</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('programmes')}>Subsidized Training Programmes</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('trainers')}>Master Trainers & Faculty</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('centres')}>Accredited Training Centres</span>"""

new_footer = """                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('courses')}>Explore 100+ Skill Courses</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('programmes')}>Subsidized Training Programmes</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('centres')}>Accredited Training Centres</span>"""

if old_footer in content:
    content = content.replace(old_footer, new_footer)
    print("4. Removed Trainers shortcut from footer")
else:
    print("4. Could not find old_footer")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("App.tsx trainer removal script completed.")
