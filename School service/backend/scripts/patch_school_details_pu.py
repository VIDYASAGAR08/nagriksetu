path = r'C:\Users\callm\nagriksetu\frontend\src\pages\public\SchoolDetailsPage.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_seat = '''        {/* SECTION B.1: Live Seat Availability & Quotas */}
        <LiveSeatAvailability
          schoolId={institution.school_id}
          schoolName={institution.school_name}
          onApplyClick={() => setIsApplyModalOpen(true)}
        />'''

new_seat = '''        {/* SECTION B.1: Live Seat Availability & Quotas */}
        <LiveSeatAvailability
          schoolId={institution.school_id}
          schoolName={institution.school_name}
          category={institution.category}
          schoolType={institution.school_type}
          onApplyClick={() => setIsApplyModalOpen(true)}
        />'''

assert old_seat in content, 'old_seat not found'
content = content.replace(old_seat, new_seat)

old_acad = '''        {/* SECTION F: Academic Information & Programmes */}
        <InstitutionAcademics
          programs={programs}
          schoolType={institution.school_type}
        />'''

new_acad = '''        {/* SECTION F: Academic Information & Programmes */}
        <InstitutionAcademics
          programs={programs}
          schoolType={institution.school_type}
          category={institution.category}
        />'''

assert old_acad in content, 'old_acad not found'
content = content.replace(old_acad, new_acad)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SchoolDetailsPage.jsx successfully patched!")
