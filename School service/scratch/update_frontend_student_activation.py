login_path = 'C:/Users/callm/nagriksetu/frontend/src/pages/auth/LoginPage.jsx'
with open(login_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add state variables for lookup and DOB verification around line 35
old_state = """  const [studentPasswordInput, setStudentPasswordInput] = useState('')
  const [studentConfirmPasswordInput, setStudentConfirmPasswordInput] = useState('')
  const [studentActLoading, setStudentActLoading] = useState(false)"""

new_state = """  const [studentPasswordInput, setStudentPasswordInput] = useState('')
  const [studentConfirmPasswordInput, setStudentConfirmPasswordInput] = useState('')
  const [studentActLoading, setStudentActLoading] = useState(false)

  // Verified Identity Activation States
  const [studentLookupData, setStudentLookupData] = useState(null)
  const [studentLookupLoading, setStudentLookupLoading] = useState(false)
  const [studentDobInput, setStudentDobInput] = useState('')
  const [studentConfirmedRecord, setStudentConfirmedRecord] = useState(false)"""

# 2. Add handleStudentLookup, handleStudentResetLookup, and update handleStudentActivate around line 140
old_act_handlers = """    try {
      setStudentActLoading(true)
      setError('')
      const payload = {
        student_identifier: studentIdInput.trim(),
        full_name: studentNameInput.trim(),
        email: studentEmailInput.trim(),
        phone: studentPhoneInput.trim() || null,
        password: studentPasswordInput,
        confirm_password: studentConfirmPasswordInput,
      }
      const res = await apiPost('/auth/student/register', payload)
      setSuccess(res.message || 'Student account activated successfully! You can now sign in.')
      setIdentifier(studentIdInput.trim())
      setPassword(studentPasswordInput)
      setStudentTab('login')
    } catch (err) {
      if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
        setError('Unable to connect to NagrikSetu authentication server. Please verify network connectivity and backend service status.')
      } else {
        setError(err.message || 'Failed to activate student account. Please verify your details.')
      }
    } finally {
      setStudentActLoading(false)
    }
  }"""

new_act_handlers = """    if (!studentLookupData) {
      setError('Please look up and confirm your official enrolled student record first.')
      return
    }

    if (!studentDobInput.trim()) {
      setError('Please provide your official Date of Birth for identity verification.')
      return
    }

    if (!studentConfirmedRecord) {
      setError('Please confirm that the displayed institution record belongs to you.')
      return
    }

    if (studentPasswordInput.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    if (studentPasswordInput !== studentConfirmPasswordInput) {
      setError('Passwords do not match.')
      return
    }

    try {
      setStudentActLoading(true)
      setError('')
      const payload = {
        student_identifier: studentLookupData.permanent_student_id || studentLookupData.student_id || studentIdInput.trim(),
        date_of_birth: studentDobInput.trim(),
        email: studentEmailInput.trim() || null,
        phone: studentPhoneInput.trim() || null,
        password: studentPasswordInput,
        confirm_password: studentConfirmPasswordInput,
      }
      const res = await apiPost('/auth/student/register', payload)
      setSuccess(res.message || `Student account for ${studentLookupData.official_student_name} activated successfully! You can now sign in.`)
      setIdentifier(studentLookupData.permanent_student_id || studentLookupData.student_id || studentIdInput.trim())
      setPassword(studentPasswordInput)
      // Reset activation form state
      setStudentLookupData(null)
      setStudentDobInput('')
      setStudentConfirmedRecord(false)
      setStudentTab('login')
    } catch (err) {
      if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
        setError('Unable to connect to NagrikSetu authentication server. Please verify network connectivity and backend service status.')
      } else {
        setError(err.message || 'Failed to activate student account. Please verify your details.')
      }
    } finally {
      setStudentActLoading(false)
    }
  }

  // Handle Initial Lookup by Student ID / Permanent SATS ID
  async function handleStudentLookup(e) {
    e.preventDefault()
    if (!studentIdInput.trim()) {
      setError('Please enter your Student ID or Permanent SATS ID.')
      return
    }

    try {
      setStudentLookupLoading(true)
      setError('')
      setSuccess('')
      const res = await apiPost('/auth/student/lookup', {
        student_identifier: studentIdInput.trim()
      })
      setStudentLookupData(res)
      setStudentNameInput(res.official_student_name)
      setStudentConfirmedRecord(true)
    } catch (err) {
      setStudentLookupData(null)
      setError(err.message || 'Student ID not found. Please verify the ID or contact your school.')
    } finally {
      setStudentLookupLoading(false)
    }
  }

  // Reset Student Lookup to search again
  function handleStudentResetLookup() {
    setStudentLookupData(null)
    setStudentConfirmedRecord(false)
    setStudentDobInput('')
    setError('')
  }"""

# 3. Replace activation form JSX around line 608
old_form_jsx = """                ) : (
                  <form onSubmit={handleStudentActivate}>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#102B46', marginBottom: '0.3rem' }}>
                        Student ID or Permanent SATS ID *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. SCH001-STD01-002"
                        value={studentIdInput}
                        onChange={e => setStudentIdInput(e.target.value)}
                        style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#102B46', marginBottom: '0.3rem' }}>
                        Student Full Name (As per records) *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Kiran Kumar"
                        value={studentNameInput}
                        onChange={e => setStudentNameInput(e.target.value)}
                        style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#102B46', marginBottom: '0.3rem' }}>
                          Email Address *
                        </label>
                        <input
                          type="email"
                          required
                          placeholder="student@example.com"
                          value={studentEmailInput}
                          onChange={e => setStudentEmailInput(e.target.value)}
                          style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#102B46', marginBottom: '0.3rem' }}>
                          Phone (Optional)
                        </label>
                        <input
                          type="tel"
                          placeholder="10-digit mobile"
                          value={studentPhoneInput}
                          onChange={e => setStudentPhoneInput(e.target.value)}
                          style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                        />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1.25rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#102B46', marginBottom: '0.3rem' }}>
                          Create Password *
                        </label>
                        <input
                          type="password"
                          required
                          minLength={8}
                          placeholder="Min 8 characters"
                          value={studentPasswordInput}
                          onChange={e => setStudentPasswordInput(e.target.value)}
                          style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#102B46', marginBottom: '0.3rem' }}>
                          Confirm Password *
                        </label>
                        <input
                          type="password"
                          required
                          minLength={8}
                          placeholder="Min 8 characters"
                          value={studentConfirmPasswordInput}
                          onChange={e => setStudentConfirmPasswordInput(e.target.value)}
                          style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={studentActLoading}
                      className="btn btn--primary btn--full"
                      style={{ background: '#155EEF', fontWeight: 700 }}
                    >
                      {studentActLoading ? <LoadingSpinner size="sm" /> : 'Activate Student Account'}
                    </button>
                  </form>
                )}"""

new_form_jsx = """                ) : (
                  <div>
                    {!studentLookupData ? (
                      /* STEP 1: INITIAL STUDENT ID LOOKUP */
                      <form onSubmit={handleStudentLookup}>
                        <div style={{ background: '#EFF8FF', border: '1px solid #B2DDFF', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem', fontSize: '0.825rem', color: '#175CD3' }}>
                          ℹ️ <strong>Database-Verified Activation:</strong> Enter your Student ID or Permanent SATS ID. The system will look up your official enrolled profile directly from the Karnataka Education database.
                        </div>

                        <div style={{ marginBottom: '1rem' }}>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
                            Student ID or Permanent SATS ID <span style={{ color: '#D92D20' }}>*</span>
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="e.g. NS-SCH019-STD06-166"
                            value={studentIdInput}
                            onChange={e => setStudentIdInput(e.target.value)}
                            style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '6px', fontSize: '0.9rem', fontFamily: 'monospace' }}
                          />
                          <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.25rem' }}>
                            Accepted: SATS Permanent Student ID (e.g. NS-SCH019-STD06-166) or Institutional Roll ID (e.g. SCH19956).
                          </div>
                        </div>

                        <button
                          type="submit"
                          disabled={studentLookupLoading || !studentIdInput.trim()}
                          className="btn btn--primary btn--full"
                          style={{ background: '#155EEF', fontWeight: 700, padding: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem' }}
                        >
                          {studentLookupLoading ? <LoadingSpinner size="sm" /> : '🔍 Look Up Official Student Record →'}
                        </button>

                        {/* Demo Helper for Ishaan Verma */}
                        <div style={{ marginTop: '1rem', padding: '0.75rem', background: '#F8F9FA', borderRadius: '6px', border: '1px dashed #D0D5DD' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475467', marginBottom: '0.35rem', textTransform: 'uppercase' }}>
                            DEMO STUDENT LOOKUP (BALLARI EDUCATION SCHOOL)
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              setStudentIdInput('NS-SCH019-STD06-166')
                              setError('')
                            }}
                            className="btn btn--ghost btn--sm"
                            style={{ width: '100%', background: '#FFFFFF', border: '1px solid #D0D5DD', color: '#155EEF', fontWeight: 600, fontSize: '0.8rem' }}
                          >
                            ⚡ Fill Ishaan Verma (NS-SCH019-STD06-166)
                          </button>
                        </div>
                      </form>
                    ) : (
                      /* STEP 2: CONFIRMED RECORD DISPLAY & IDENTITY VERIFICATION */
                      <form onSubmit={handleStudentActivate}>
                        {/* Retrieved Official Record Card */}
                        <div style={{ background: '#F8FAFC', border: '1px solid #B2DDFF', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#027A48', fontWeight: 700, fontSize: '0.85rem' }}>
                              <span>✓</span> Database Record Found
                            </div>
                            <button
                              type="button"
                              onClick={handleStudentResetLookup}
                              style={{ background: 'none', border: 'none', color: '#155EEF', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline' }}
                            >
                              ← Change Student ID
                            </button>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: '110px 1fr', gap: '0.4rem', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
                            <span style={{ color: '#667085', fontWeight: 600 }}>Official Name:</span>
                            <strong style={{ color: '#102B46', fontSize: '0.95rem' }}>
                              {studentLookupData.official_student_name}
                            </strong>

                            <span style={{ color: '#667085', fontWeight: 600 }}>Institution:</span>
                            <span style={{ color: '#102B46' }}>
                              {studentLookupData.institution_name} ({studentLookupData.institution_id})
                            </span>

                            <span style={{ color: '#667085', fontWeight: 600 }}>Standard/Sec:</span>
                            <span style={{ color: '#102B46' }}>
                              {studentLookupData.standard_display}, {studentLookupData.section_display}
                            </span>

                            <span style={{ color: '#667085', fontWeight: 600 }}>Permanent ID:</span>
                            <span style={{ fontFamily: 'monospace', color: '#155EEF', fontWeight: 700 }}>
                              {studentLookupData.permanent_student_id}
                            </span>

                            <span style={{ color: '#667085', fontWeight: 600 }}>Status:</span>
                            <span>
                              <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.15rem 0.5rem', borderRadius: '10px', fontSize: '0.72rem', fontWeight: 700 }}>
                                ✓ Actively Enrolled
                              </span>
                            </span>
                          </div>

                          {/* Read-Only Populated Student Name Input */}
                          <div style={{ marginTop: '0.5rem' }}>
                            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>
                              Official Student Name (Read-Only from Database)
                            </label>
                            <input
                              type="text"
                              readOnly
                              value={studentLookupData.official_student_name}
                              style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #D0D5DD', borderRadius: '4px', fontSize: '0.875rem', background: '#F2F4F7', color: '#102B46', fontWeight: 700 }}
                            />
                          </div>

                          {/* Confirmation Checkbox */}
                          <div style={{ marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid #E2E8F0' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.825rem', color: '#102B46', fontWeight: 600, cursor: 'pointer' }}>
                              <input
                                type="checkbox"
                                checked={studentConfirmedRecord}
                                onChange={e => setStudentConfirmedRecord(e.target.checked)}
                              />
                              I confirm this is my official enrolled student profile
                            </label>
                          </div>
                        </div>

                        {/* IDENTITY VERIFICATION SECTION */}
                        <div style={{ marginBottom: '1rem', background: '#FFFFFF', padding: '1rem', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
                          <div style={{ fontWeight: 700, color: '#102B46', fontSize: '0.875rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <span>🔒</span> Identity Verification Credentials
                          </div>
                          <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.78rem', color: '#667085' }}>
                            For security, enter your official Date of Birth recorded in the school admission register. (Email is not used as identity proof).
                          </p>

                          <div style={{ marginBottom: '0.85rem' }}>
                            <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#102B46', marginBottom: '0.3rem' }}>
                              Official Date of Birth (DOB) <span style={{ color: '#D92D20' }}>*</span>
                            </label>
                            <input
                              type="date"
                              required
                              value={studentDobInput}
                              onChange={e => setStudentDobInput(e.target.value)}
                              style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                            />
                            <div style={{ fontSize: '0.72rem', color: '#667085', marginTop: '0.25rem' }}>
                              Must match the official admission record (YYYY-MM-DD).
                            </div>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '0.85rem' }}>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#475467', marginBottom: '0.25rem' }}>
                                Email (Optional)
                              </label>
                              <input
                                type="email"
                                placeholder="For notifications only"
                                value={studentEmailInput}
                                onChange={e => setStudentEmailInput(e.target.value)}
                                style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#475467', marginBottom: '0.25rem' }}>
                                Mobile (Optional)
                              </label>
                              <input
                                type="tel"
                                placeholder="10-digit phone"
                                value={studentPhoneInput}
                                onChange={e => setStudentPhoneInput(e.target.value)}
                                style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
                              />
                            </div>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '0.25rem' }}>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#102B46', marginBottom: '0.25rem' }}>
                                Create Password <span style={{ color: '#D92D20' }}>*</span>
                              </label>
                              <input
                                type="password"
                                required
                                minLength={8}
                                placeholder="Min 8 characters"
                                value={studentPasswordInput}
                                onChange={e => setStudentPasswordInput(e.target.value)}
                                style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#102B46', marginBottom: '0.25rem' }}>
                                Confirm Password <span style={{ color: '#D92D20' }}>*</span>
                              </label>
                              <input
                                type="password"
                                required
                                minLength={8}
                                placeholder="Min 8 characters"
                                value={studentConfirmPasswordInput}
                                onChange={e => setStudentConfirmPasswordInput(e.target.value)}
                                style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
                              />
                            </div>
                          </div>
                        </div>

                        <button
                          type="submit"
                          disabled={studentActLoading || !studentConfirmedRecord || !studentDobInput}
                          className="btn btn--primary btn--full"
                          style={{ background: '#12B76A', fontWeight: 700, padding: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                        >
                          {studentActLoading ? <LoadingSpinner size="sm" /> : '✓ Verify Identity & Activate Student Account'}
                        </button>
                      </form>
                    )}
                  </div>
                )}"""

for old, new, label in [
    (old_state, new_state, "state variables"),
    (old_act_handlers, new_act_handlers, "handlers"),
    (old_form_jsx, new_form_jsx, "form JSX")
]:
    old_crlf = old.replace('\n', '\r\n')
    new_crlf = new.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf, 1)
        print(f"Replaced CRLF: {label}")
    elif old in text:
        text = text.replace(old, new, 1)
        print(f"Replaced LF: {label}")
    else:
        print(f"FAILED to find: {label}")

with open(login_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated LoginPage.jsx successfully.")
