import re

path = r'C:\Users\callm\nagriksetu\frontend\src\pages\public\HomePage.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Subtitle
old_sub = 'Explore schools, PU colleges, diploma institutions and universities across Karnataka in one place.'
new_sub = 'Explore schools, PU colleges, degree colleges, and universities across Karnataka in one place.'
assert old_sub in content, 'old_sub not found'
content = content.replace(old_sub, new_sub)

# 2. Update Category Select Dropdown
old_select = '''                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  style={{
                    width: '100%',
                    border: 'none',
                    outline: 'none',
                    fontSize: '0.9rem',
                    color: '#344054',
                    background: 'transparent',
                    cursor: 'pointer'
                  }}
                >
                  <option value="ALL">All Categories</option>
                  <option value="SCHOOLS">Schools (K-10)</option>
                  <option value="PU">PU Colleges (11-12)</option>
                  <option value="DIPLOMA">Diploma / Polytechnic</option>
                  <option value="UNDERGRADUATE">Degree & Universities</option>
                </select>'''

new_select = '''                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  style={{
                    width: '100%',
                    border: 'none',
                    outline: 'none',
                    fontSize: '0.9rem',
                    color: '#344054',
                    background: 'transparent',
                    cursor: 'pointer'
                  }}
                >
                  <option value="ALL">All Categories</option>
                  <option value="SCHOOLS">Schools (K-10)</option>
                  <option value="PU">PU Colleges (11-12)</option>
                  <option value="DEGREE">Degree Colleges</option>
                  <option value="UNIVERSITY">Universities</option>
                </select>'''
assert old_select in content, 'old_select not found'
content = content.replace(old_select, new_select)

# 3. Update Popular Category Pills
old_pills = '''              {[
                { label: 'Schools (1–10)', cat: 'SCHOOLS' },
                { label: 'PU Colleges (11–12)', cat: 'PU' },
                { label: 'Diploma / Polytechnic', cat: 'DIPLOMA' },
                { label: 'Degree Colleges', cat: 'UNDERGRADUATE' }
              ].map((p, idx) => ('''

new_pills = '''              {[
                { label: 'Schools (K–10)', cat: 'SCHOOLS' },
                { label: 'PU Colleges (11–12)', cat: 'PU' },
                { label: 'Degree Colleges', cat: 'DEGREE' },
                { label: 'Universities', cat: 'UNIVERSITY' }
              ].map((p, idx) => ('''
assert old_pills in content, 'old_pills not found'
content = content.replace(old_pills, new_pills)

# 4. Update Four Cards
old_cards = '''            {/* Card 1: Schools */}
            <Link
              to="/schools?category=SCHOOLS"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#EFF4FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #D1E0FF'
                }}>
                  🏫
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Schools
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#155EEF', marginBottom: '0.6rem' }}>
                  Standards 1 – 10 (K-10)
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Foundational, primary, middle, and secondary schools under KSEAB state syllabus, CBSE, and ICSE.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#155EEF', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 20 Schools →
              </div>
            </Link>

            {/* Card 2: PU Colleges */}
            <Link
              to="/schools?category=PU"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#FDF2FA',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #FCE7F6'
                }}>
                  🔬
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  PU Colleges
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#C11574', marginBottom: '0.6rem' }}>
                  Classes 11 – 12 (Higher Secondary)
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Science (PCMB, PCMC, PCME), Commerce (SEBA, CEBA), and Arts Pre-University programs.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#C11574', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse PU Streams →
              </div>
            </Link>

            {/* Card 3: Diploma / Polytechnic */}
            <Link
              to="/schools?category=DIPLOMA"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#FEF6EE',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #FEE4E2'
                }}>
                  ⚙️
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Diploma / Polytechnic
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#B54708', marginBottom: '0.6rem' }}>
                  3-Year Technical Diplomas
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  DTE-approved polytechnics in Computer Science, Mechanical, Civil, Electrical, and Automobile.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#B54708', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse Polytechnics →
              </div>
            </Link>

            {/* Card 4: Undergraduate */}
            <Link
              to="/schools?category=UNDERGRADUATE"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#ECFDF3',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #D1FADF'
                }}>
                  🎓
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Undergraduate Degrees
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#027A48', marginBottom: '0.6rem' }}>
                  Colleges & Universities
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Premier autonomous engineering institutes, arts, commerce, and science universities (B.E., B.Com, B.Sc., BCA).
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#027A48', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 10 Colleges →
              </div>
            </Link>'''

new_cards = '''            {/* Card 1: Schools */}
            <Link
              to="/schools?category=SCHOOLS"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#EFF4FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #D1E0FF'
                }}>
                  🏫
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Schools (K–10)
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#155EEF', marginBottom: '0.6rem' }}>
                  Standards 1 – 10 (Foundational to High School)
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Foundational, primary, middle, and high schools under KSEAB state syllabus, CBSE, and ICSE.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#155EEF', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 15 Schools →
              </div>
            </Link>

            {/* Card 2: PU Colleges */}
            <Link
              to="/schools?category=PU"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#FDF2FA',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #FCE7F6'
                }}>
                  🔬
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  PU Colleges (11–12)
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#C11574', marginBottom: '0.6rem' }}>
                  Classes 11 – 12 (Higher Secondary)
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Science (PCMB, PCMC, PCME), Commerce (SEBA, CEBA), and Arts Pre-University education.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#C11574', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 5 PU Colleges →
              </div>
            </Link>

            {/* Card 3: Degree Colleges */}
            <Link
              to="/schools?category=DEGREE"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#ECFDF3',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #D1FADF'
                }}>
                  🏛️
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Degree Colleges
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#027A48', marginBottom: '0.6rem' }}>
                  Undergraduate & Engineering
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Premier autonomous engineering institutes and affiliated undergraduate colleges (B.E., B.Com, B.Sc., BCA).
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#027A48', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 5 Degree Colleges →
              </div>
            </Link>

            {/* Card 4: Universities */}
            <Link
              to="/schools?category=UNIVERSITY"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#EEF4FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #C7D7FE'
                }}>
                  🎓
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Universities
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#444CE7', marginBottom: '0.6rem' }}>
                  State & Statutory Universities
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Statutory state and multi-disciplinary universities offering comprehensive undergraduate, postgraduate, and doctoral degrees.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#444CE7', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 5 Universities →
              </div>
            </Link>'''
assert old_cards in content, 'old_cards not found'
content = content.replace(old_cards, new_cards)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('HomePage.jsx patched successfully.')
