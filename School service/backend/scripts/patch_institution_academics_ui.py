path = r'C:\Users\callm\nagriksetu\frontend\src\components\institution\InstitutionAcademics.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update component signature & isPU logic
old_sig = 'export default function InstitutionAcademics({ programs, schoolType }) {'
new_sig = '''export default function InstitutionAcademics({ programs, schoolType, category }) {
  const isPUInst = category === 'PU Colleges (11-12)' ||
                   schoolType === 'PU College' ||
                   (programs && programs.length > 0 && programs.every(p => p.education_level === 'higher_secondary'))'''

assert old_sig in content, 'old_sig not found'
content = content.replace(old_sig, new_sig)

# 2. Update levelLabels
old_labels = '''  const levelLabels = {
    school: 'Standard Tier 1: School Education (Classes 1–10)',
    higher_secondary: 'Standard Tier 2: Composite Pre-University / PU (Classes 11–12)',
    diploma: 'Standard Tier 3: Technical Diploma / Polytechnic (3-Year DTE)',
    undergraduate: 'Standard Tier 4: Professional Undergraduate Degrees (3–4 Year AICTE/UGC)'
  }'''

new_labels = '''  const levelLabels = {
    school: 'Standard Tier 1: School Education (Classes 1–10)',
    higher_secondary: isPUInst 
      ? 'Pre-University Education Curricula (1st PUC & 2nd PUC — Classes 11–12)' 
      : 'Standard Tier 2: Composite Pre-University / PU (Classes 11–12)',
    diploma: 'Standard Tier 3: Technical Diploma / Polytechnic (3-Year DTE)',
    undergraduate: 'Standard Tier 4: Professional Undergraduate Degrees (3–4 Year AICTE/UGC)'
  }'''

assert old_labels in content, 'old_labels not found'
content = content.replace(old_labels, new_labels)

# 3. Update Header & Subtitle
old_header = '''            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Academic Structure & Programme Curricula
            </h2>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
              Recognized state curricula across school (K-10), PU streams, polytechnic diplomas, and undergraduate degrees
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            padding: '0.35rem 0.8rem',
            borderRadius: '20px',
            background: '#EFF4FF',
            color: '#155EEF',
            border: '1px solid #B2CCFF'
          }}>
            {programs?.length || 0} Academic Programmes Registered
          </span>'''

new_header = '''            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              {isPUInst ? 'Pre-University Academic Streams & Combinations' : 'Academic Structure & Programme Curricula'}
            </h2>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
              {isPUInst 
                ? 'Department of Pre-University Education (DPUE) approved combinations across Science, Commerce, Arts, and Vocational streams.' 
                : 'Recognized state curricula across school (K-10), PU streams, polytechnic diplomas, and undergraduate degrees'}
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            padding: '0.35rem 0.8rem',
            borderRadius: '20px',
            background: isPUInst ? '#FDF2FA' : '#EFF4FF',
            color: isPUInst ? '#C11574' : '#155EEF',
            border: `1px solid ${isPUInst ? '#FCE7F6' : '#B2CCFF'}`
          }}>
            {programs?.length || 0} {isPUInst ? 'PU Combinations Registered' : 'Academic Programmes Registered'}
          </span>'''

assert old_header in content, 'old_header not found'
content = content.replace(old_header, new_header)

# 4. Update Scope Notice
old_scope = '''        <span>
          <strong>Platform Scope Notice:</strong> NagrikSetu manages public admissions exclusively across K-10 Schools, Pre-University (11-12), Polytechnic Diplomas, and Undergraduate Degrees. Postgraduate programmes are outside the current platform scope.
        </span>'''

new_scope = '''        <span>
          <strong>Platform Scope Notice:</strong> {isPUInst 
            ? 'NagrikSetu facilitates 1st PUC initial admissions for approved subject combinations (PCMB, PCMC, CEBA, etc.) under the Department of Pre-University Education (DPUE).' 
            : 'NagrikSetu manages public admissions exclusively across K-10 Schools, Pre-University (11-12), Polytechnic Diplomas, and Undergraduate Degrees. Postgraduate programmes are outside the current platform scope.'}
        </span>'''

assert old_scope in content, 'old_scope not found'
content = content.replace(old_scope, new_scope)

# 5. Update PU card details
old_pucard = '''                        {isPU && (
                          <div style={{ fontSize: '0.8rem', color: '#475467', lineHeight: 1.5, marginBottom: '0.6rem' }}>
                            <div>🏛️ <strong>Curriculum Board:</strong> Department of Pre-University Education</div>
                            <div>📖 <strong>Years:</strong> 1st PU (Std 11) & 2nd PU (Std 12)</div>
                          </div>
                        )}'''

new_pucard = '''                        {isPU && (
                          <div style={{ fontSize: '0.8rem', color: '#475467', lineHeight: 1.5, marginBottom: '0.6rem' }}>
                            <div>🏛️ <strong>Curriculum Board:</strong> Department of Pre-University Education (DPUE)</div>
                            <div>📖 <strong>Academic Levels:</strong> 1st PUC (Std 11) & 2nd PUC (Std 12)</div>
                            <div>🏷️ <strong>Stream:</strong> {p.discipline_or_stream}</div>
                            {p.combination_code && <div>📝 <strong>Subjects:</strong> {p.combination_code} (Core + Electives)</div>}
                          </div>
                        )}'''

assert old_pucard in content, 'old_pucard not found'
content = content.replace(old_pucard, new_pucard)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("InstitutionAcademics.jsx successfully patched!")
