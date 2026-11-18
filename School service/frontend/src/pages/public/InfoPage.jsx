import { useLocation, Link } from 'react-router-dom'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'

export default function InfoPage() {
  const location = useLocation()
  const path = location.pathname.replace('/', '')

  const contentMap = {
    about: {
      title: 'About NagrikSetu Karnataka',
      crumbs: [{ label: 'Home', href: '/' }, { label: 'About the Service' }],
      body: (
        <>
          <p>
            NagrikSetu (Citizen Bridge) is Karnataka's digital education verification portal. It bridges parents, guardians, and educational institutions by providing privacy-preserving access to verified student academic profiles.
          </p>
          <h3>Core Objectives</h3>
          <ul>
            <li><strong>Digital Citizen Access:</strong> Empower parents with secure access to children's official attendance, marks, and certificates.</li>
            <li><strong>Institutional Verification:</strong> Eliminate fraudulent or accidental student linking through rigorous school staff review.</li>
            <li><strong>Privacy & Safety:</strong> Prohibit public student directory crawling and enforce Argon2id hashing on all authentication credentials.</li>
          </ul>
        </>
      )
    },
    help: {
      title: 'NagrikSetu Citizen Help Centre',
      crumbs: [{ label: 'Home', href: '/' }, { label: 'Help' }],
      body: (
        <>
          <h3>Frequently Asked Questions</h3>
          <div style={{ marginBottom: '1.5rem' }}>
            <strong>Q: How do I create a parent account?</strong>
            <p>Visit the Citizen Registration page, provide your mandatory 10-digit Indian mobile number, full name, and a password containing at least 8 characters.</p>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <strong>Q: How long does student linking take?</strong>
            <p>Linking requests are reviewed by authorized school personnel from your child's assigned school during institutional working hours.</p>
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <strong>Q: Can I edit student attendance or examination marks?</strong>
            <p>No. In accordance with Karnataka State Education Department guidelines, academic records are read-only for guardians and maintained exclusively by school authorities.</p>
          </div>
        </>
      )
    },
    contact: {
      title: 'Contact Karnataka School Services',
      crumbs: [{ label: 'Home', href: '/' }, { label: 'Contact' }],
      body: (
        <>
          <p>For institutional support, portal onboarding, or technical verification queries:</p>
          <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', maxWidth: '500px' }}>
            <p><strong>Department of School Education & Literacy</strong><br />Government of Karnataka, Bengaluru</p>
            <p><strong>Portal Helpdesk:</strong> 1800-425-XXXX (Toll Free, Demo)</p>
            <p><strong>Support Email:</strong> support@nagriksetu.karnataka.gov.in (Demonstration)</p>
          </div>
        </>
      )
    },
    privacy: {
      title: 'Institutional Privacy Policy',
      crumbs: [{ label: 'Home', href: '/' }, { label: 'Privacy Policy' }],
      body: (
        <>
          <p>
            NagrikSetu is committed to safeguarding the privacy and personal data of minors and their guardians under Indian data protection regulations.
          </p>
          <h3>Information Security</h3>
          <p>No student names, standard affiliations, or academic results are exposed to unauthenticated visitors. School staff only access students enrolled within their assigned institution.</p>
        </>
      )
    }
  }

  const page = contentMap[path] || contentMap.about

  return (
    <div>
      <Breadcrumbs crumbs={page.crumbs} />
      <div className="container" style={{ maxWidth: '900px', margin: '2rem auto', padding: '0 1rem' }}>
        <div className="card" style={{ padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff' }}>
          <h1 style={{ fontSize: '1.875rem', color: '#1a3a6b', margin: '0 0 1rem 0' }}>{page.title}</h1>
          <div style={{ color: '#334155', lineHeight: 1.6, fontSize: '0.9375rem' }}>
            {page.body}
          </div>
          <div style={{ marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid #e8eaed' }}>
            <Link to="/" className="btn btn--secondary btn--sm">← Back to Portal Home</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
