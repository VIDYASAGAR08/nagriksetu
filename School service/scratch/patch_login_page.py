with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update useEffect to support tab, student_id, auto_lookup
old_use_effect = '''  // Sync category state with URL search param
  useEffect(() => {
    const cat = searchParams.get('category')
    if (['student', 'parent', 'admin'].includes(cat)) {
      setSelectedCategory(cat)
    } else if (!cat) {
      setSelectedCategory(null)
    }
  }, [searchParams])'''

new_use_effect = '''  // Sync category & tab state with URL search param
  useEffect(() => {
    const cat = searchParams.get('category')
    if (['student', 'parent', 'admin'].includes(cat)) {
      setSelectedCategory(cat)
    } else if (!cat) {
      setSelectedCategory(null)
    }
    const tab = searchParams.get('tab')
    if (tab === 'activate') {
      setStudentTab('activate')
    }
    const sid = searchParams.get('student_id')
    if (sid) {
      setStudentIdInput(sid)
      if (searchParams.get('auto_lookup') === 'true') {
        apiPost('/auth/student/lookup', { student_identifier: sid })
          .then(res => {
            setStudentLookupData(res)
            setStudentNameInput(res.official_student_name)
            setStudentConfirmedRecord(true)
          })
          .catch(() => {})
      }
    }
  }, [searchParams])'''

# 2. Clean handleStudentActivate legacy validation
old_activate = '''  // Handle student account registration / activation
  async function handleStudentActivate(e) {
    e.preventDefault()
    if (!studentIdInput.trim() || !studentNameInput.trim() || !studentEmailInput.trim()) {
      setError('Please fill in your Student ID, Full Name, and Email address.')
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

    if (!studentLookupData) {
      setError('Please look up and confirm your official enrolled student record first.')
      return
    }'''

new_activate = '''  // Handle student account registration / activation
  async function handleStudentActivate(e) {
    e.preventDefault()
    if (!studentLookupData) {
      setError('Please look up and confirm your official enrolled student record first.')
      return
    }'''

content_norm = content.replace('\r\n', '\n')
old_eff_norm = old_use_effect.replace('\r\n', '\n')
new_eff_norm = new_use_effect.replace('\r\n', '\n')
old_act_norm = old_activate.replace('\r\n', '\n')
new_act_norm = new_activate.replace('\r\n', '\n')

assert old_eff_norm in content_norm, 'old_use_effect not found'
content_norm = content_norm.replace(old_eff_norm, new_eff_norm, 1)

assert old_act_norm in content_norm, 'old_activate not found'
content_norm = content_norm.replace(old_act_norm, new_act_norm, 1)

with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx', 'w', encoding='utf-8', newline='') as f:
    f.write(content_norm)

print('LoginPage.jsx successfully updated.')
