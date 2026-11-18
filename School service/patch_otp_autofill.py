login_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx"

with open(login_path, "r", encoding="utf-8") as f:
    login_c = f.read()

# 1. Patch Google OTP in LoginPage.jsx
old_google_otp = """                            <input
                              type="text"
                              required
                              maxLength={6}
                              pattern="\\d{6}"
                              placeholder="• • • • • •"
                              value={googleOtp}
                              onChange={(e) => setGoogleOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                              style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d0d5dd',
                                borderRadius: '6px',
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                textAlign: 'center',
                                letterSpacing: '0.35em',
                                backgroundColor: '#ffffff',
                                boxSizing: 'border-box'
                              }}
                            />"""

new_google_otp = """                            <input
                              type="text"
                              name="one-time-code"
                              id="login-google-otp"
                              autoComplete="one-time-code"
                              inputMode="numeric"
                              required
                              maxLength={6}
                              pattern="[0-9]{6}"
                              placeholder="• • • • • •"
                              autoCorrect="off"
                              autoCapitalize="off"
                              spellCheck="false"
                              value={googleOtp}
                              onChange={(e) => setGoogleOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                              style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d0d5dd',
                                borderRadius: '6px',
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                textAlign: 'center',
                                letterSpacing: '0.35em',
                                backgroundColor: '#ffffff',
                                boxSizing: 'border-box'
                              }}
                            />"""

assert old_google_otp in login_c, "old_google_otp not found in LoginPage.jsx"
login_c = login_c.replace(old_google_otp, new_google_otp, 1)

# 2. Patch Mobile OTP in LoginPage.jsx
old_mobile_otp = """                            <input
                              type="text"
                              required
                              maxLength={6}
                              pattern="\\d{6}"
                              placeholder="• • • • • •"
                              value={mobileOtp}
                              onChange={(e) => setMobileOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                              style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d0d5dd',
                                borderRadius: '6px',
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                textAlign: 'center',
                                letterSpacing: '0.35em',
                                backgroundColor: '#ffffff',
                                boxSizing: 'border-box'
                              }}
                            />"""

new_mobile_otp = """                            <input
                              type="text"
                              name="one-time-code"
                              id="login-mobile-otp"
                              autoComplete="one-time-code"
                              inputMode="numeric"
                              required
                              maxLength={6}
                              pattern="[0-9]{6}"
                              placeholder="• • • • • •"
                              autoCorrect="off"
                              autoCapitalize="off"
                              spellCheck="false"
                              value={mobileOtp}
                              onChange={(e) => setMobileOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                              style={{
                                width: '100%',
                                padding: '0.75rem',
                                border: '1px solid #d0d5dd',
                                borderRadius: '6px',
                                fontSize: '1.25rem',
                                fontWeight: 700,
                                textAlign: 'center',
                                letterSpacing: '0.35em',
                                backgroundColor: '#ffffff',
                                boxSizing: 'border-box'
                              }}
                            />"""

assert old_mobile_otp in login_c, "old_mobile_otp not found in LoginPage.jsx"
login_c = login_c.replace(old_mobile_otp, new_mobile_otp, 1)

with open(login_path, "w", encoding="utf-8") as f:
    f.write(login_c)

print("LoginPage.jsx OTP autofill attributes updated!")

# Patch RegisterPage.jsx
reg_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\RegisterPage.jsx"

with open(reg_path, "r", encoding="utf-8") as f:
    reg_c = f.read()

# 3. Patch Google OTP in RegisterPage.jsx
old_reg_google = """                    <input
                      type="text"
                      required
                      maxLength={6}
                      pattern="\\d{6}"
                      placeholder="• • • • • •"
                      value={googleOtp}
                      onChange={(e) => setGoogleOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        textAlign: 'center',
                        letterSpacing: '0.35em',
                        backgroundColor: '#ffffff',
                        boxSizing: 'border-box'
                      }}
                    />"""

new_reg_google = """                    <input
                      type="text"
                      name="one-time-code"
                      id="register-google-otp"
                      autoComplete="one-time-code"
                      inputMode="numeric"
                      required
                      maxLength={6}
                      pattern="[0-9]{6}"
                      placeholder="• • • • • •"
                      autoCorrect="off"
                      autoCapitalize="off"
                      spellCheck="false"
                      value={googleOtp}
                      onChange={(e) => setGoogleOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        textAlign: 'center',
                        letterSpacing: '0.35em',
                        backgroundColor: '#ffffff',
                        boxSizing: 'border-box'
                      }}
                    />"""

assert old_reg_google in reg_c, "old_reg_google not found in RegisterPage.jsx"
reg_c = reg_c.replace(old_reg_google, new_reg_google, 1)

# 4. Patch Mobile OTP in RegisterPage.jsx
old_reg_mobile = """                    <input
                      type="text"
                      required
                      maxLength={6}
                      pattern="\\d{6}"
                      placeholder="• • • • • •"
                      value={mobileOtp}
                      onChange={(e) => setMobileOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        textAlign: 'center',
                        letterSpacing: '0.35em',
                        backgroundColor: '#ffffff',
                        boxSizing: 'border-box'
                      }}
                    />"""

new_reg_mobile = """                    <input
                      type="text"
                      name="one-time-code"
                      id="register-mobile-otp"
                      autoComplete="one-time-code"
                      inputMode="numeric"
                      required
                      maxLength={6}
                      pattern="[0-9]{6}"
                      placeholder="• • • • • •"
                      autoCorrect="off"
                      autoCapitalize="off"
                      spellCheck="false"
                      value={mobileOtp}
                      onChange={(e) => setMobileOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        textAlign: 'center',
                        letterSpacing: '0.35em',
                        backgroundColor: '#ffffff',
                        boxSizing: 'border-box'
                      }}
                    />"""

assert old_reg_mobile in reg_c, "old_reg_mobile not found in RegisterPage.jsx"
reg_c = reg_c.replace(old_reg_mobile, new_reg_mobile, 1)

with open(reg_path, "w", encoding="utf-8") as f:
    f.write(reg_c)

print("RegisterPage.jsx OTP autofill attributes updated!")
