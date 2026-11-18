with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\public\HomePage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

target = '      {/* ========================================================\n          SECTION 2: FOUR EDUCATION CATEGORY CARDS'

section_1b = '''      {/* ========================================================
          SECTION 1B: USER PORTAL ENTRY CATEGORIES
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#F8F9FC', borderBottom: '1px solid #EAECF0' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              CITIZEN & STAKEHOLDER PORTALS
            </span>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46', margin: '0.35rem 0 0.5rem 0' }}>
              Choose Your Portal Experience
            </h2>
            <p style={{ color: '#475467', margin: 0, fontSize: '0.95rem', maxWidth: '680px', marginLeft: 'auto', marginRight: 'auto' }}>
              Select your user category below to access public institutional registries or log in to verified educational services.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
            {/* 1. Public / Citizen */}
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #D0D5DD',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 1px 3px rgba(16, 24, 40, 0.05)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#EFF8FF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid #B2DDFF' }}>
                    🌐
                  </div>
                  <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px' }}>
                    Open Public Access
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  Public / Citizen
                </h3>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Browse, search, and discover verified profiles, facilities, curricula, and seat quotas across all 30 Karnataka institutions without authentication.
                </p>
              </div>
              <Link
                to="/schools"
                className="btn btn--secondary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#102B46',
                  borderColor: '#D0D5DD',
                  textDecoration: 'none'
                }}
              >
                Explore Institutions Directory →
              </Link>
            </div>

            {/* 2. Student */}
            <div style={{
              background: '#FFFFFF',
              border: '2px solid #155EEF',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 4px 12px rgba(21, 94, 239, 0.08)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#EEF4FF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid #C7D7FE' }}>
                    🎓
                  </div>
                  <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px' }}>
                    Enrolled Students
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  Student Portal
                </h3>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Dedicated student workspace. Access daily attendance records, examination gradebooks, upcoming timetables, and personal academic standing.
                </p>
              </div>
              <Link
                to="/login?category=student"
                className="btn btn--primary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  background: '#155EEF',
                  color: '#FFFFFF',
                  border: 'none',
                  textDecoration: 'none'
                }}
              >
                Student Sign In & Activation →
              </Link>
            </div>

            {/* 3. Parent / Guardian */}
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #D0D5DD',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 1px 3px rgba(16, 24, 40, 0.05)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#FEF0C7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid #FEDF89' }}>
                    👨‍👩‍👧‍👦
                  </div>
                  <span style={{ background: '#FFFAEB', color: '#B54708', border: '1px solid #FEDF89', fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px' }}>
                    Verified Guardians
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  Parent / Guardian
                </h3>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Apply for Stage 1 admissions, monitor real-time review decisions, inspect linked children's attendance, evaluation cards, and official notices.
                </p>
              </div>
              <Link
                to="/login?category=parent"
                className="btn btn--secondary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#102B46',
                  borderColor: '#D0D5DD',
                  textDecoration: 'none'
                }}
              >
                Parent Portal Sign In →
              </Link>
            </div>

            {/* 4. Administrator & Staff */}
            <div style={{
              background: '#102B46',
              border: '1px solid #0B1E32',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 4px 12px rgba(16, 43, 70, 0.15)',
              color: '#FFFFFF',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.25)' }}>
                    🏛️
                  </div>
                  <span style={{ background: '#FEF08A', color: '#854D0E', fontSize: '0.72rem', fontWeight: 800, padding: '2px 8px', borderRadius: '12px' }}>
                    Official Access Only
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 0.5rem 0' }}>
                  Administrator & Staff
                </h3>
                <p style={{ color: '#E0E7FF', fontSize: '0.85rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Official login gateway for Institution Administrators across 30 institutions, permitted staff workspaces, and Central Platform Administrators.
                </p>
              </div>
              <Link
                to="/login?category=admin"
                className="btn btn--primary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  background: '#155EEF',
                  color: '#FFFFFF',
                  border: 'none',
                  textDecoration: 'none'
                }}
              >
                Admin / Staff Login →
              </Link>
            </div>
          </div>
        </div>
      </section>\n\n'''

if target in text:
    new_text = text.replace(target, section_1b + target)
    with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\public\HomePage.jsx', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Successfully inserted Section 1B into HomePage.jsx")
else:
    print("Target not found!")
