import { Link } from 'react-router-dom'

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="gov-footer" role="contentinfo">
      <div className="container">
        <div className="gov-footer__grid">
          <div className="gov-footer__brand">
            <h3>NagrikSetu</h3>
            <p>
              A citizen-facing school services portal providing public school
              discovery, parent-child record access, and student information
              management for Karnataka schools.
            </p>
            <p style={{ marginTop: '1rem' }}>
              <span className="gov-footer__demo-notice">
                ⚠ Demonstration application · Synthetic data · Not an official government service
              </span>
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
