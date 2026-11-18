with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx', 'r', encoding='utf-8') as f:
    c = f.read()

target = "  const [mobileDevInfo, setMobileDevInfo] = useState(null)"
replacement = """  const [mobileDevInfo, setMobileDevInfo] = useState(null)

  // Legacy unified citizen states for helper functions
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

assert target in c, "target not found"
c = c.replace(target, replacement, 1)

with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx', 'w', encoding='utf-8') as f:
    f.write(c)

print('Added legacy citizen states in LoginPage.jsx')
