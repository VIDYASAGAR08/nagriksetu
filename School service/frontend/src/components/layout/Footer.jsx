import { Link } from 'react-router-dom'

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="gov-footer" role="contentinfo" style={{ background: '#081c33', color: '#f8fafc', borderTop: 'none' }}>
      {/* Tricolor Ribbon */}
      <div style={{ height: '4px', width: '100%', background: 'linear-gradient(to right, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%)' }} />
      <div className="container" style={{ paddingTop: '2.5rem', paddingBottom: '2.5rem' }}>
        <div className="gov-footer__grid">
          <div className="gov-footer__brand">
            <h3 style={{ color: '#ffffff', fontSize: '1.4rem', fontWeight: 800 }}>
              नागरिक सेतु <span style={{ color: '#FF9933' }}>· NagrikSetu</span>
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.82rem', lineHeight: 1.6 }}>
              Unified Citizen School Services Network providing public school
              discovery, student enrolment verification, and parent services for Karnataka institutions.
            </p>
            <p style={{ marginTop: '1rem' }}>
              <a
                href="http://localhost:5173"
                style={{
                  color: '#FF9933',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  textDecoration: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                }}
              >
                ← Return to NagrikSetu Central Portal (localhost:5173)
              </a>
            </p>
          </div>

          <div className="gov-footer__col">
            <h4>School Services</h4>
            <ul>
              <li><Link to="/schools">Search Schools</Link></li>
              <li><Link to="/about">About the Service</Link></li>
              <li><Link to="/register">Create Account</Link></li>
              <li><Link to="/login">Parent Login</Link></li>
            </ul>
          </div>

          <div className="gov-footer__col">
            <h4>Help</h4>
            <ul>
              <li><Link to="/help">Help Centre</Link></li>
              <li><Link to="/help#faq">FAQs</Link></li>
              <li><Link to="/help#linking">Linking a Child</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </div>

          <div className="gov-footer__col">
            <h4>Legal</h4>
            <ul>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Use</Link></li>
              <li><Link to="/accessibility">Accessibility</Link></li>
              <li><Link to="/sitemap">Sitemap</Link></li>
            </ul>
          </div>
        </div>

        <div className="gov-footer__bottom">
          <span>© {year} NagrikSetu · School Service · Karnataka · Demonstration only</span>
          <span>FastAPI · SQLite · React · Not an official government service</span>
        </div>
      </div>
    </footer>
  )
}
