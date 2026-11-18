# -*- coding: utf-8 -*-
path = r"C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = """    if (qRef) {
      setFormStudentRef(qRef)
      setActiveTab('new-request')
    }
  }, [searchParams])"""

replacement = """    if (qRef) {
      setFormStudentRef(qRef)
      setActiveTab('new-request')
    }
  }, [searchParams])

  // Automatically open Child Academic Modal if child_psid is provided in URL
  useEffect(() => {
    const qPsid = searchParams.get('child_psid')
    if (qPsid && children.length > 0 && !selectedChild) {
      const match = children.find(c => c.permanent_student_id === qPsid) || children[0]
      if (match) viewRecords(match)
    }
  }, [searchParams, children])"""

if target in text:
    text = text.replace(target, replacement, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Added child_psid auto-open effect to ParentDashboard.jsx!")
else:
    print("Target not found!")
