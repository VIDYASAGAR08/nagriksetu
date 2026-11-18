MODAL_PATH = r"C:\Users\callm\nagriksetu\frontend\src\components\admissions\Stage1AdmissionModal.jsx"

with open(MODAL_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update loadConfig default first/second language
old_init_lang = """            if (res.school_config?.first_languages?.length > 0) {
              setFirstLanguage(res.school_config.first_languages[0])
            }
            if (res.school_config?.second_languages?.length > 0) {
              setSecondLanguage(res.school_config.second_languages[0])
            }"""

new_init_lang = """            setFirstLanguage('Kannada')
            setSecondLanguage('English')"""

assert old_init_lang in content, "old_init_lang not found"
content = content.replace(old_init_lang, new_init_lang, 1)

# 2. Update language inputs in Step 1
old_lang_ui = """                      {/* Language / Medium of Instruction Preferences */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            First Language Preference / Medium *
                          </label>
                          <select
                            value={firstLanguage}
                            onChange={(e) => setFirstLanguage(e.target.value)}
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #CBD5E1',
                              fontSize: '0.875rem',
                              background: '#FFFFFF'
                            }}
                          >
                            {(config?.school_config?.first_languages || ['Kannada', 'English']).map(lang => (
                              <option key={lang} value={lang}>{lang}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Second Language Preference
                          </label>
                          <select
                            value={secondLanguage}
                            onChange={(e) => setSecondLanguage(e.target.value)}
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #CBD5E1',
                              fontSize: '0.875rem',
                              background: '#FFFFFF'
                            }}
                          >
                            {(config?.school_config?.second_languages || ['English', 'Kannada', 'Hindi', 'Sanskrit']).map(lang => (
                              <option key={lang} value={lang}>{lang}</option>
                            ))}
                          </select>
                        </div>
                      </div>"""

new_lang_ui = """                      {/* Language / Medium of Instruction Preferences */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            First Language Preference *
                          </label>
                          <select
                            id="school-first-language-select"
                            value={firstLanguage}
                            onChange={(e) => setFirstLanguage(e.target.value)}
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #CBD5E1',
                              fontSize: '0.875rem',
                              background: '#FFFFFF',
                              fontWeight: 600,
                              color: '#102B46'
                            }}
                          >
                            <option value="Kannada">Kannada</option>
                            <option value="Hindi">Hindi</option>
                            <option value="Sanskrit">Sanskrit</option>
                          </select>
                          <span style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.25rem', display: 'block' }}>
                            Select primary language of instruction
                          </span>
                        </div>

                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Second Language Preference (Compulsory) *
                          </label>
                          <input
                            id="school-second-language-input"
                            type="text"
                            value="English"
                            readOnly
                            disabled
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #E2E8F0',
                              background: '#F1F5F9',
                              fontSize: '0.875rem',
                              color: '#334155',
                              fontWeight: 700,
                              cursor: 'not-allowed',
                              boxSizing: 'border-box'
                            }}
                          />
                          <span style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.25rem', display: 'block' }}>
                            🔒 Fixed standard second language
                          </span>
                        </div>
                      </div>"""

assert old_lang_ui in content, "old_lang_ui not found"
content = content.replace(old_lang_ui, new_lang_ui, 1)

# 3. Update Review & Confirm summary text
old_rev_lang = "{isSchool && `Standard / Class ${standardApplied} (1st Lang: ${firstLanguage})`}"
new_rev_lang = "{isSchool && `Standard / Class ${standardApplied} • 1st Lang: ${firstLanguage} • 2nd Lang: English (Compulsory)`}"

assert old_rev_lang in content, "old_rev_lang not found"
content = content.replace(old_rev_lang, new_rev_lang, 1)

# 4. Update handleSubmit second language
old_sub_lang = "second_language_preference: (isSchool || educationLevel === 'school') ? (secondLanguage || 'English') : null,"
new_sub_lang = "second_language_preference: (isSchool || educationLevel === 'school') ? 'English' : null,"

assert old_sub_lang in content, "old_sub_lang not found"
content = content.replace(old_sub_lang, new_sub_lang, 1)

with open(MODAL_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[+] Successfully updated Stage1AdmissionModal.jsx with fixed language configuration!")
