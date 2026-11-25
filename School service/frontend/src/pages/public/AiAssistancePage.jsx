import NagrikSetuAiChat from '../../components/ai/NagrikSetuAiChat.jsx'

export default function AiAssistancePage() {
  return (
    <div style={{
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '24px 20px 48px',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      {/* Top Banner & Header */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          fontWeight: '600',
          color: '#134074',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          marginBottom: '6px'
        }}>
          <span>🏛️ Government of Karnataka</span>
          <span>•</span>
          <span>School Education & Literacy Services</span>
        </div>

        <h1 style={{
          fontSize: '28px',
          fontWeight: '800',
          color: '#0B2545',
          margin: '0 0 6px 0',
          letterSpacing: '-0.5px'
        }}>
          NagrikSetu AI Assistance
        </h1>

        <p style={{
          fontSize: '14px',
          color: '#475569',
          margin: 0,
          maxWidth: '800px',
          lineHeight: '1.5'
        }}>
          One unified intelligent assistant for citizens, parents, students, teachers, and school administrators.
          Search schools, verify scholarship eligibility, review RTE quota guidelines, track admissions, and access authorized academic records.
        </p>
      </div>

      {/* Main Grid: Chat Window + Information Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) 320px',
        gap: '24px',
        alignItems: 'start'
      }}>
        {/* Chat Interface */}
        <div>
          <NagrikSetuAiChat isFullPage={true} />
        </div>

        {/* Sidebar Info Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Card 1: Features & Scope */}
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '8px',
            border: '1px solid #e2e8f0',
            padding: '18px 20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
          }}>
            <h3 style={{ fontSize: '15px', fontWeight: '700', color: '#0B2545', margin: '0 0 12px 0' }}>
              🎯 Platform Capabilities
            </h3>
            <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '13px', color: '#334155', lineHeight: '1.6' }}>
              <li><strong>School Discovery</strong>: 30 verified institutions across Karnataka with real-time seat ledgers.</li>
              <li><strong>RTE 25% Quota</strong>: Statutory age, income, and neighborhood criteria under Section 12(1)(c).</li>
              <li><strong>SSP Scholarships</strong>: Pre-Matric and Post-Matric schemes, income ceilings, and document requirements.</li>
              <li><strong>Parent Portal</strong>: Stage 1 & Stage 2 admission application tracking and verified child records.</li>
              <li><strong>Student Desk</strong>: Authorized attendance percentages and examination performance.</li>
            </ul>
          </div>

          {/* Card 2: Privacy Safeguards */}
          <div style={{
            backgroundColor: '#f8fafc',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
            padding: '18px 20px'
          }}>
            <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#0B2545', margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>🔒</span> Privacy & Data Isolation
            </h3>
            <p style={{ fontSize: '12px', color: '#475569', margin: '0 0 10px 0', lineHeight: '1.5' }}>
              Public users can discover all public schools and government welfare schemes. Personal student records and admission applications require a verified signed-in session.
            </p>
            <div style={{ fontSize: '11px', color: '#64748b', backgroundColor: '#e2e8f0', padding: '6px 10px', borderRadius: '4px' }}>
              Role-Based Access Control enforced strictly via server-side JWT verification.
            </div>
          </div>

          {/* Card 3: 200 Question Bank Integration */}
          <div style={{
            backgroundColor: '#f0fdf4',
            borderRadius: '8px',
            border: '1px solid #bbf7d0',
            padding: '16px 20px'
          }}>
            <div style={{ fontSize: '13px', fontWeight: '700', color: '#166534', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>✓</span> Connected Question Bank
            </div>
            <div style={{ fontSize: '12px', color: '#15803d', lineHeight: '1.5' }}>
              200 canonical question patterns across 9 categories imported into the central database for instant intent classification and grounded retrieval.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
