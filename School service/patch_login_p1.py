import re

login_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx"

with open(login_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update subtitle in header
old_sub = "{selectedCategory === 'parent' && 'Sign in using your Full Name and Mobile or Email OTP.'}"
new_sub = "{selectedCategory === 'parent' && 'Sign in to NagrikSetu using your Google email or mobile number.'}"
assert old_sub in content, "old_sub not found in LoginPage.jsx"
content = content.replace(old_sub, new_sub)

# 2. Update useAuth imports to include getOAuthConfig, sendGoogleOtp, googleLogin
old_use_auth = "const { login, sendOtp, loginWithOtp, sendUnifiedOtp, unifiedLogin } = useAuth()"
new_use_auth = "const { login, sendOtp, loginWithOtp, sendUnifiedOtp, unifiedLogin, getOAuthConfig, sendGoogleOtp, googleLogin } = useAuth()"
assert old_use_auth in content, "old_use_auth not found in LoginPage.jsx"
content = content.replace(old_use_auth, new_use_auth)

# 3. Add Google and Mobile states and effects
old_citizen_states = """  // Citizen Unified Login States
  const [citizenFullName, setCitizenFullName] = useState('')
  const [citizenContact, setCitizenContact] = useState('')
  const [citizenOtp, setCitizenOtp] = useState('')
  const [otpSent, setOtpSent] = useState(false)
  const [otpSending, setOtpSending] = useState(false)
  const [otpVerifying, setOtpVerifying] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)
  const [maskedContact, setMaskedContact] = useState('')
  const [detectedType, setDetectedType] = useState(null)
  const [devOtpInfo, setDevOtpInfo] = useState(null)"""

new_citizen_states = """  // Citizen Authentication Options & States
  const [citizenMethod, setCitizenMethod] = useState(null) // null | 'google' | 'mobile'
  const [oauthConfig, setOauthConfig] = useState({ google_client_id: '', is_google_configured: false, is_sms_development: false })
  
  // Google OTP Flow States
  const [googleIdToken, setGoogleIdToken] = useState('')
  const [googleEmailMasked, setGoogleEmailMasked] = useState('')
  const [googleOtp, setGoogleOtp] = useState('')
  const [googleOtpSent, setGoogleOtpSent] = useState(false)
  const [googleSending, setGoogleSending] = useState(false)
  const [googleVerifying, setGoogleVerifying] = useState(false)
  const [googleCooldown, setGoogleCooldown] = useState(0)
  const [devGoogleEmail, setDevGoogleEmail] = useState('')

  // Mobile SMS OTP Flow States
  const [mobileNumber, setMobileNumber] = useState('')
  const [mobileOtp, setMobileOtp] = useState('')
  const [mobileOtpSent, setMobileOtpSent] = useState(false)
  const [mobileSending, setMobileSending] = useState(false)
  const [mobileVerifying, setMobileVerifying] = useState(false)
  const [mobileCooldown, setMobileCooldown] = useState(0)
  const [mobileMasked, setMobileMasked] = useState('')
  const [mobileDevInfo, setMobileDevInfo] = useState(null)

  // Load OAuth Config
  useEffect(() => {
    if (getOAuthConfig) {
      getOAuthConfig()
        .then(cfg => {
          if (cfg) setOauthConfig(cfg)
        })
        .catch(() => {})
    }
  }, [getOAuthConfig])

  // Cooldown timers
  useEffect(() => {
    if (googleCooldown <= 0) return
    const timer = setInterval(() => setGoogleCooldown(c => Math.max(0, c - 1)), 1000)
    return () => clearInterval(timer)
  }, [googleCooldown])

  useEffect(() => {
    if (mobileCooldown <= 0) return
    const timer = setInterval(() => setMobileCooldown(c => Math.max(0, c - 1)), 1000)
    return () => clearInterval(timer)
  }, [mobileCooldown])"""

assert old_citizen_states in content, "old_citizen_states not found"
content = content.replace(old_citizen_states, new_citizen_states)

# Write updated LoginPage
with open(login_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part 1 of LoginPage.jsx patched successfully.")
