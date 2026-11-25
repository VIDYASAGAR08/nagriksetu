css_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\style.css'

with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace the header and nav styling blocks with flawless flexbox layout
target_old = """.header-main {
  background: #ffffff;
  border-bottom: 1.5px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  position: relative;
  z-index: 50;
  width: 100%;
}

.header-container {
  width: 100%;
  max-width: 1720px;
  margin: 0 auto;
  padding: 0 1.25rem;
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

/* 1. LEFT BRANDING */
.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  text-decoration: none;
  flex-shrink: 0;
  min-width: max-content;
}

.brand-emblem {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: grid;
  place-items: center;
  color: #0284c7;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.brand-text h1 {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f2444;
  letter-spacing: -0.3px;
  line-height: 1.15;
  margin: 0;
  white-space: nowrap;
}

.brand-text p {
  font-size: 0.65rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin: 2px 0 0 0;
  white-space: nowrap;
}

/* 2. CENTRE NAVIGATION LINKS */
.nav-links {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 4px;
  min-width: 0;
}

.nav-item-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.42rem 0.6rem;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: #475569;
  font-size: 0.77rem;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.15s ease;
  cursor: pointer;
  flex-shrink: 0;
  height: 34px;
  box-sizing: border-box;
}

.nav-item-btn:hover {
  background: #f1f5f9;
  color: #0f2444;
}

.nav-item-btn.active {
  background: #f8fafc;
  color: #0f2444;
  font-weight: 700;
  border-color: #cbd5e1;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

/* Subtle, professional highlight for Student Portal */
.nav-item-btn.nav-student-portal-btn {
  color: #0369a1;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  font-weight: 700;
}

.nav-item-btn.nav-student-portal-btn:hover {
  background-color: #e0f2fe;
  border-color: #7dd3fc;
  color: #0284c7;
}

.nav-item-btn.nav-student-portal-btn.active {
  background-color: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
  box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
}

/* 3. RIGHT ACCOUNT & ACTIONS AREA */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.nav-user-account-wrapper {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.nav-user-badge {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 0.25rem 0.65rem 0.25rem 0.35rem;
  max-width: 220px;
}

.nav-user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.nav-user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
  overflow: hidden;
}

.nav-user-name {
  font-size: 0.74rem;
  font-weight: 700;
  color: #0f2444;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.nav-user-subtag {
  font-size: 0.62rem;
  font-weight: 700;
  color: #0284c7;
  letter-spacing: 0.02em;
}

.btn-logout {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0.35rem 0.65rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #ffffff;
  color: #64748b;
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  height: 32px;
}

.btn-logout:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

.nav-guest-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}"""

replacement_new = """.header-main {
  background: #ffffff;
  border-bottom: 1.5px solid #e2e8f0;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  position: relative;
  z-index: 50;
  width: 100%;
}

.header-container {
  width: 100%;
  max-width: 1760px;
  margin: 0 auto;
  padding: 0 1rem;
  min-height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

/* 1. LEFT BRANDING */
.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  text-decoration: none;
  flex-shrink: 0;
  margin-right: 0.5rem;
}

.brand-emblem {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  display: grid;
  place-items: center;
  color: #0284c7;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  flex-shrink: 0;
}

.brand-text h1 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f2444;
  letter-spacing: -0.3px;
  line-height: 1.15;
  margin: 0;
  white-space: nowrap;
}

.brand-text p {
  font-size: 0.62rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  margin: 1px 0 0 0;
  white-space: nowrap;
}

/* 2. CENTRE NAVIGATION LINKS */
.nav-links {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1 1 auto;
  gap: 3px;
  padding: 0 0.5rem;
}

.nav-item-btn {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 0.38rem 0.5rem;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: #475569;
  font-size: 0.74rem;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.15s ease;
  cursor: pointer;
  flex-shrink: 0;
  height: 32px;
  box-sizing: border-box;
}

.nav-item-btn:hover {
  background: #f1f5f9;
  color: #0f2444;
}

.nav-item-btn.active {
  background: #f8fafc;
  color: #0f2444;
  font-weight: 700;
  border-color: #cbd5e1;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

/* Subtle, professional highlight for Student Portal */
.nav-item-btn.nav-student-portal-btn {
  color: #0369a1;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  font-weight: 700;
}

.nav-item-btn.nav-student-portal-btn:hover {
  background-color: #e0f2fe;
  border-color: #7dd3fc;
  color: #0284c7;
}

.nav-item-btn.nav-student-portal-btn.active {
  background-color: #0284c7;
  color: #ffffff;
  border-color: #0284c7;
  box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2);
}

.mobile-drawer-account-items {
  display: none;
}

/* 3. RIGHT ACCOUNT & ACTIONS AREA */
.nav-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  margin-left: 0.5rem;
}

.nav-user-account-wrapper {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.nav-profile-link {
  font-size: 0.74rem;
}

.nav-user-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 0.2rem 0.55rem 0.2rem 0.3rem;
  max-width: 170px;
}

.nav-user-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e2e8f0;
  color: #475569;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.nav-user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
  overflow: hidden;
}

.nav-user-name {
  font-size: 0.72rem;
  font-weight: 700;
  color: #0f2444;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 110px;
}

.nav-user-subtag {
  font-size: 0.6rem;
  font-weight: 700;
  color: #0284c7;
  letter-spacing: 0.02em;
}

.btn-logout {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 0.3rem 0.55rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #ffffff;
  color: #64748b;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  height: 30px;
}

.btn-logout:hover {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;
}

.nav-guest-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}"""

assert target_old in css, "target_old not found in style.css"
css = css.replace(target_old, replacement_new, 1)

# Now update the responsive queries section:
# Switch desktop -> collapsible drawer at 1340px to ensure plenty of breathing room at 1280px / 1024px / 768px!
old_resp_block = """/* Tablet & Smaller Laptops: Switch to clean drawer/collapsible menu (< 1200px) */
@media (max-width: 1200px) {
  .mobile-menu-toggle {
    display: inline-flex;
  }

  .header-container {
    min-height: 60px;
    position: relative;
  }

  .nav-links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    border-bottom: 3px solid #0f2444;
    box-shadow: 0 15px 30px rgba(15, 23, 42, 0.12);
    flex-direction: column;
    align-items: stretch;
    padding: 0.75rem 1rem;
    gap: 0.35rem;
    max-height: 80vh;
    overflow-y: auto;
    z-index: 100;
  }

  .nav-links.nav-open {
    display: flex;
  }

  .nav-item-btn {
    padding: 0.65rem 0.85rem;
    font-size: 0.84rem;
    border-radius: 6px;
    justify-content: flex-start;
    height: auto;
    border: 1px solid transparent;
  }

  .nav-item-btn.active {
    background: #eff6ff;
    color: #0284c7;
    border-color: #bfdbfe;
  }

  .nav-user-badge {
    max-width: 150px;
  }
  .nav-user-name {
    max-width: 85px;
  }
}

@media (max-width: 768px) {
  .nav-user-name {
    display: none;
  }
  .btn-logout span {
    display: none;
  }
  .nav-user-badge {
    padding: 0.2rem;
    border-radius: 50%;
  }
}"""

new_resp_block = """/* Tablet & Compact Desktops: Switch to collapsible drawer below 1360px */
@media (max-width: 1360px) {
  .mobile-menu-toggle {
    display: inline-flex;
  }

  .header-container {
    min-height: 58px;
    position: relative;
  }

  .nav-links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    border-bottom: 3px solid #0f2444;
    box-shadow: 0 15px 30px rgba(15, 23, 42, 0.12);
    flex-direction: column;
    align-items: stretch;
    padding: 0.75rem 1rem;
    gap: 0.35rem;
    max-height: 80vh;
    overflow-y: auto;
    z-index: 100;
  }

  .nav-links.nav-open {
    display: flex;
  }

  .nav-item-btn {
    padding: 0.65rem 0.85rem;
    font-size: 0.84rem;
    border-radius: 6px;
    justify-content: flex-start;
    height: auto;
    border: 1px solid transparent;
  }

  .nav-item-btn.active {
    background: #eff6ff;
    color: #0284c7;
    border-color: #bfdbfe;
  }

  .mobile-drawer-account-items {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    border-top: 1px dashed #cbd5e1;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
  }

  .mobile-logout-item {
    color: #dc2626 !important;
  }

  .mobile-logout-item:hover {
    background: #fef2f2 !important;
  }

  .nav-user-badge {
    max-width: 140px;
  }
  .nav-user-name {
    max-width: 75px;
  }
}

/* Compact screens & Mobile */
@media (max-width: 768px) {
  .nav-profile-link {
    display: none !important;
  }
  .nav-user-name {
    display: none;
  }
  .btn-logout {
    display: none !important;
  }
  .nav-user-badge {
    padding: 0.2rem;
    border-radius: 50%;
    max-width: 28px;
  }
}"""

assert old_resp_block in css, "old_resp_block not found in style.css"
css = css.replace(old_resp_block, new_resp_block, 1)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print("SUCCESS: style.css updated with bulletproof 1360px drawer breakpoint and mobile account menu!")
