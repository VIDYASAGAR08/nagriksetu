# Patch LoginPage.jsx
with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx", "r", encoding="utf-8") as f:
    login_c = f.read()

gis_login_effect = """
  // Initialize Google Identity Services
  useEffect(() => {
    if (citizenMethod === 'google' && oauthConfig.is_google_configured) {
      let isRendered = false
      const initGis = () => {
        if (window.google?.accounts?.id) {
          try {
            window.google.accounts.id.initialize({
              client_id: oauthConfig.google_client_id,
              callback: (response) => {
                if (response?.credential) {
                  handleGoogleCredentialResponse(response.credential)
                }
              },
              auto_select: false,
            })
            const btnEl = document.getElementById('googleSignInBtn')
            if (btnEl && !isRendered) {
              btnEl.innerHTML = ''
              window.google.accounts.id.renderButton(btnEl, {
                theme: 'outline',
                size: 'large',
                width: 320,
                text: 'continue_with',
                shape: 'rectangular',
              })
              isRendered = true
            }
            try {
              window.google.accounts.id.prompt()
            } catch (_) {}
          } catch (e) {
            console.warn('GIS error:', e)
          }
        }
      }
      initGis()
      const timer = setInterval(() => {
        if (!isRendered) initGis()
      }, 400)
      return () => clearInterval(timer)
    }
  }, [citizenMethod, oauthConfig])
"""

login_target = "  useEffect(() => {\n    if (mobileCooldown <= 0) return\n    const timer = setInterval(() => setMobileCooldown(c => Math.max(0, c - 1)), 1000)\n    return () => clearInterval(timer)\n  }, [mobileCooldown])"
assert login_target in login_c, "login_target not found"
login_c = login_c.replace(login_target, login_target + "\n" + gis_login_effect, 1)

with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx", "w", encoding="utf-8") as f:
    f.write(login_c)
print("Added GIS effect to LoginPage.jsx")

# Patch RegisterPage.jsx
with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\RegisterPage.jsx", "r", encoding="utf-8") as f:
    reg_c = f.read()

gis_reg_effect = """
  // Initialize Google Identity Services for Registration
  useEffect(() => {
    if (method === 'google' && oauthConfig.is_google_configured) {
      let isRendered = false
      const initGis = () => {
        if (window.google?.accounts?.id) {
          try {
            window.google.accounts.id.initialize({
              client_id: oauthConfig.google_client_id,
              callback: (response) => {
                if (response?.credential) {
                  handleGoogleCredentialResponse(response.credential)
                }
              },
              auto_select: false,
            })
            const btnEl = document.getElementById('googleRegisterBtn')
            if (btnEl && !isRendered) {
              btnEl.innerHTML = ''
              window.google.accounts.id.renderButton(btnEl, {
                theme: 'outline',
                size: 'large',
                width: 320,
                text: 'signup_with',
                shape: 'rectangular',
              })
              isRendered = true
            }
          } catch (e) {
            console.warn('GIS error:', e)
          }
        }
      }
      initGis()
      const timer = setInterval(() => {
        if (!isRendered) initGis()
      }, 400)
      return () => clearInterval(timer)
    }
  }, [method, oauthConfig])
"""

reg_target = "  useEffect(() => {\n    if (mobileCooldown <= 0) return\n    const timer = setInterval(() => setMobileCooldown(c => Math.max(0, c - 1)), 1000)\n    return () => clearInterval(timer)\n  }, [mobileCooldown])"
assert reg_target in reg_c, "reg_target not found"
reg_c = reg_c.replace(reg_target, reg_target + "\n" + gis_reg_effect, 1)

with open(r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\RegisterPage.jsx", "w", encoding="utf-8") as f:
    f.write(reg_c)
print("Added GIS effect to RegisterPage.jsx")
