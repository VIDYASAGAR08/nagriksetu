import sys

file_path = r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update State
target_state = '''  const [linkingCodeIssued, setLinkingCodeIssued] = useState(false)
  const [issuedCodeDisplay, setIssuedCodeDisplay] = useState('')
  const [verificationCodeInput, setVerificationCodeInput] = useState('')'''

replace_state = '''  const [linkingCodeIssued, setLinkingCodeIssued] = useState(false)
  const [verificationCodeInput, setVerificationCodeInput] = useState('')
  const [resendCooldown, setResendCooldown] = useState(0)

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return
    const timer = setInterval(() => {
      setResendCooldown((prev) => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(timer)
  }, [resendCooldown])'''

assert target_state in text, "target_state not found in ParentDashboard.jsx"
text = text.replace(target_state, replace_state, 1)

# 2. Update handleRequestLinkingCode
target_req = '''  // Request Institution-Issued Verification Code
  async function handleRequestLinkingCode() {
    if (!lookupChildResult?.student_id) return
    setIsRequestingCode(true)
    setVerificationError('')
    try {
      const res = await apiPost('/parent/request-linking-code', { student_id: lookupChildResult.student_id }, token)
      setLinkingCodeIssued(true)
      setIssuedCodeDisplay(res.verification_code || '')
      setVerificationCodeInput(res.verification_code || '')
    } catch (err) {
      setVerificationError(err.message || 'Failed to generate institution verification code.')
    } finally {
      setIsRequestingCode(false)
    }
  }'''

replace_req = '''  // Request Institution-Issued Verification Code
  async function handleRequestLinkingCode() {
    if (!lookupChildResult?.student_id) return
    setIsRequestingCode(true)
    setVerificationError('')
    try {
      await apiPost('/parent/request-linking-code', {
        student_id: lookupChildResult.student_id,
        relationship_type: linkRelationship
      }, token)
      setLinkingCodeIssued(true)
      setVerificationCodeInput('')
      setResendCooldown(30)
    } catch (err) {
      setVerificationError(err.message || 'Failed to request institution verification code.')
    } finally {
      setIsRequestingCode(false)
    }
  }'''

assert target_req in text, "target_req not found in ParentDashboard.jsx"
text = text.replace(target_req, replace_req, 1)

# 3. Update handleResetLookup & handleVerifyAndLinkChild
target_reset = '''      // Reset form
      setLookupChildResult(null)
      setLinkStudentIdInput('')
      setLinkingCodeIssued(false)
      setIssuedCodeDisplay('')
      setVerificationCodeInput('')'''

replace_reset = '''      // Reset form
      setLookupChildResult(null)
      setLinkStudentIdInput('')
      setLinkingCodeIssued(false)
      setVerificationCodeInput('')
      setResendCooldown(0)'''

assert target_reset in text, "target_reset not found in ParentDashboard.jsx"
text = text.replace(target_reset, replace_reset, 1)

# 4. Update Step 3 JSX
# Find the STEP 3 block
step3_start = "{/* STEP 3: Parent-Child Verification (Expiring Code) */}"
assert step3_start in text, "step3_start not found"

# Let's locate the whole block up to "{/* Tab 2: New Linking Request Form"
end_marker = "{/* Tab 2: New Linking Request Form"
assert end_marker in text, "end_marker not found"

idx_start = text.find(step3_start)
idx_end = text.find(end_marker)

old_block = text[idx_start:idx_end]

new_block = '''{/* STEP 3: Parent-Child Verification (Expiring Code) */}
                {linkingCodeIssued && !lookupChildResult.is_already_linked && (
                  <div style={{ marginTop: '1.5rem', background: '#FFFFFF', border: '1px solid #CBD5E1', borderRadius: '8px', padding: '1.5rem', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                      <span style={{ fontSize: '1.3rem' }}>🔒</span>
                      <div>
                        <h4 style={{ margin: 0, color: '#0F172A', fontSize: '1.05rem', fontWeight: 700 }}>
                          Institution Authorization Verification
                        </h4>
                        <div style={{ fontSize: '0.8rem', color: '#64748B' }}>
                          Expiring 6-digit access code · 15 minutes validity · Max 5 attempts
                        </div>
                      </div>
                    </div>

                    {/* Official institution notification banner */}
                    <div style={{ background: '#F0F9FF', border: '1px solid #BAE6FD', borderRadius: '8px', padding: '1rem 1.25rem', marginBottom: '1.25rem', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                      <span style={{ fontSize: '1.3rem', lineHeight: 1 }}>ℹ️</span>
                      <div>
                        <div style={{ fontWeight: 700, color: '#0369A1', fontSize: '0.925rem', marginBottom: '0.25rem' }}>
                          Institution Authorization In Progress
                        </div>
                        <div style={{ color: '#0C4A6E', fontSize: '0.85rem', lineHeight: 1.5 }}>
                          Your child-linking request has been submitted to <strong>{lookupChildResult.institution_name}</strong>. Please complete the verification process using the instructions sent to your registered contact.
                        </div>
                        <div style={{ fontSize: '0.775rem', color: '#0284C7', marginTop: '0.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                          <span>⏱️ Code valid for 15 minutes</span>
                          <span>🛡️ Maximum 5 verification attempts</span>
                          <span>🏫 Official institution authorization</span>
                        </div>
                      </div>
                    </div>

                    {verificationError && (
                      <div style={{ background: '#FEF2F2', border: '1px solid #FCA5A5', color: '#991B1B', borderRadius: '6px', padding: '0.75rem 1rem', marginBottom: '1rem', fontSize: '0.875rem' }}>
                        ⚠️ {verificationError}
                      </div>
                    )}

                    <form onSubmit={handleVerifyAndLinkChild}>
                      <div style={{ marginBottom: '1.25rem' }}>
                        <label style={{ display: 'block', fontWeight: 600, color: '#1E293B', marginBottom: '0.4rem', fontSize: '0.875rem' }}>
                          Enter 6-Digit Verification Code:
                        </label>
                        <input
                          type="text"
                          maxLength={6}
                          value={verificationCodeInput}
                          onChange={(e) => {
                            setVerificationCodeInput(e.target.value.replace(/[^0-9]/g, ''))
                            setVerificationError('')
                          }}
                          placeholder="e.g. 230548"
                          style={{ maxWidth: '220px', padding: '0.65rem 0.85rem', fontSize: '1.2rem', fontFamily: 'monospace', fontWeight: 700, letterSpacing: '4px', textAlign: 'center', border: '2px solid #155EEF', borderRadius: '6px' }}
                          disabled={isSubmittingLink}
                          autoComplete="off"
                        />
                        <div style={{ fontSize: '0.775rem', color: '#64748B', marginTop: '0.35rem' }}>
                          Enter the official 6-digit numeric authorization code.
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                        <button
                          type="submit"
                          className="btn btn--success"
                          disabled={isSubmittingLink || !verificationCodeInput.trim() || verificationCodeInput.trim().length !== 6}
                          style={{ fontWeight: 700, minWidth: '160px' }}
                        >
                          {isSubmittingLink ? 'Verifying...' : 'Verify & Link Child ✓'}
                        </button>
                        <button
                          type="button"
                          onClick={handleRequestLinkingCode}
                          disabled={isRequestingCode || resendCooldown > 0}
                          className="btn btn--secondary btn--sm"
                        >
                          {resendCooldown > 0 ? `Resend Code (${resendCooldown}s)` : 'Resend Code'}
                        </button>
                        <button
                          type="button"
                          onClick={handleResetLookup}
                          className="btn btn--secondary btn--sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        '''

text = text[:idx_start] + new_block + text[idx_end:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("ParentDashboard.jsx patched successfully!")
