path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add state for selected programme batches modal
target_state = "  const [centreProgrammes, setCentreProgrammes] = useState<any[]>([]);"
new_state = """  const [centreProgrammes, setCentreProgrammes] = useState<any[]>([]);
  const [centreSelectedProgForBatches, setCentreSelectedProgForBatches] = useState<any | null>(null);"""

if target_state in content:
    content = content.replace(target_state, new_state, 1)
    print("1. Added centreSelectedProgForBatches state")
else:
    print("1. Failed to find target_state")

# 2. Update programme card in centreTab === 'programmes'
target_card = """                  {centreProgrammes.map((p: any) => (
                    <div key={p.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#f8fafc' }}>
                      <span style={{ fontSize: '0.72rem', color: '#0f766e', fontWeight: 700 }}>{p.code} • {p.mode}</span>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginTop: '0.2rem', marginBottom: '0.4rem' }}>{p.title}</h4>
                      <p style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '0.8rem' }}>{p.description}</p>
                      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '0.6rem', fontSize: '0.76rem' }}>
                        <div><strong>Trainer:</strong> {p.trainer_name || 'Assigned Instructor'}</div>
                        <div><strong>Duration:</strong> {p.duration_hours} Hours • <strong>Batches:</strong> {p.batch_count}</div>
                      </div>
                    </div>
                  ))}"""

new_card = """                  {centreProgrammes.map((p: any) => (
                    <div
                      key={p.id}
                      onClick={() => setCentreSelectedProgForBatches(p)}
                      style={{
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        padding: '1.25rem',
                        backgroundColor: '#f8fafc',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#0f766e')}
                      onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
                    >
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                          <span style={{ fontSize: '0.72rem', color: '#0f766e', fontWeight: 700 }}>{p.code} • {p.mode}</span>
                          <span
                            onClick={(e) => {
                              e.stopPropagation();
                              setCentreSelectedProgForBatches(p);
                            }}
                            style={{
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              color: '#0f766e',
                              backgroundColor: '#ccfbf1',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            {p.batch_count} Active Batch{p.batch_count === 1 ? '' : 'es'}
                          </span>
                        </div>
                        <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginTop: '0.2rem', marginBottom: '0.4rem' }}>{p.title}</h4>
                        <p style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '0.8rem' }}>{p.description}</p>
                      </div>

                      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '0.75rem', fontSize: '0.76rem' }}>
                        <div><strong>Trainer:</strong> {p.trainer_name || 'Assigned Instructor'}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.4rem' }}>
                          <span><strong>Duration:</strong> {p.duration_hours} Hours</span>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setCentreSelectedProgForBatches(p);
                            }}
                            style={{
                              backgroundColor: '#0f766e',
                              color: '#ffffff',
                              border: 'none',
                              borderRadius: '5px',
                              padding: '0.35rem 0.75rem',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              cursor: 'pointer'
                            }}
                          >
                            View Batches ({p.batch_count}) →
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}"""

if target_card in content:
    content = content.replace(target_card, new_card, 1)
    print("2. Replaced programme card with interactive View Batches action")
else:
    print("2. Failed to find target_card")

# 3. Add Modal: Dedicated Programme Batches Details
target_modal_end = """          {/* Modal: Explicit Batch Enrolment */}
          {centreEnrolModalApp && (
            <div className="modal-backdrop">
              <div className="modal-content-lg" style={{ maxWidth: '520px' }}>
                <div className="modal-header">
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f766e' }}>
                    Enrol in Batch: {centreEnrolModalApp.citizen_name}
                  </h3>
                  <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setCentreEnrolModalApp(null)}>
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body">
                  <div style={{ backgroundColor: '#f0fdfa', border: '1px solid #99f6e4', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.82rem' }}>
                    <div><strong>Course:</strong> {centreEnrolModalApp.program_title}</div>
                    <div><strong>Application Code:</strong> {centreEnrolModalApp.code}</div>
                    <div><strong>Applicant:</strong> {centreEnrolModalApp.citizen_name} ({centreEnrolModalApp.citizen_email})</div>
                  </div>

                  {centreEnrolError && (
                    <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                      {centreEnrolError}
                    </div>
                  )}

                  <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                      Assign to Active Training Batch:
                    </label>
                    <select
                      className="form-control"
                      value={centreEnrolSelectedBatchId || ''}
                      onChange={(e) => setCentreEnrolSelectedBatchId(Number(e.target.value))}
                    >
                      <option value="">-- Choose Batch --</option>
                      {centreBatches
                        .filter((b: any) => b.program_id === centreEnrolModalApp.program_id)
                        .map((b: any) => (
                          <option key={b.id} value={b.id} disabled={b.available_seats <= 0}>
                            {b.batch_name} ({b.timings} • {b.available_seats} seats left)
                          </option>
                        ))}
                    </select>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                      Internal Batch Allocation Notes:
                    </label>
                    <textarea
                      className="form-control"
                      rows={3}
                      value={centreEnrolInternalNotes}
                      onChange={(e) => setCentreEnrolInternalNotes(e.target.value)}
                      placeholder="e.g., Assigned to morning laboratory session based on learner qualification and attendance commitment."
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <button
                      className="btn-navy-outline"
                      onClick={() => setCentreEnrolModalApp(null)}
                      disabled={centreEnrolSubmitting}
                    >
                      Cancel
                    </button>
                    <button
                      className="btn-primary-orange"
                      onClick={handleCentreEnrolSubmit}
                      disabled={centreEnrolSubmitting || !centreEnrolSelectedBatchId}
                    >
                      {centreEnrolSubmitting ? 'Enrolling...' : 'Confirm Enrolment'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}"""

new_modal_block = target_modal_end + """

          {/* Modal: View Programme Batches Details */}
          {centreSelectedProgForBatches && (
            <div className="modal-backdrop">
              <div className="modal-content-lg" style={{ maxWidth: '680px' }}>
                <div className="modal-header">
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '2px 8px', borderRadius: '4px' }}>
                      {centreSelectedProgForBatches.code}
                    </span>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444', margin: '4px 0 0 0' }}>
                      {centreSelectedProgForBatches.title}
                    </h3>
                  </div>
                  <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setCentreSelectedProgForBatches(null)}>
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body">
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', backgroundColor: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.25rem', fontSize: '0.8rem' }}>
                    <div><strong>Assigned Trainer:</strong> {centreSelectedProgForBatches.trainer_name || 'Assigned Instructor'}</div>
                    <div><strong>Duration:</strong> {centreSelectedProgForBatches.duration_hours} Training Hours</div>
                    <div><strong>Delivery Mode:</strong> {centreSelectedProgForBatches.mode}</div>
                    <div><strong>Course Fee:</strong> {centreSelectedProgForBatches.fee > 0 ? `₹${centreSelectedProgForBatches.fee}` : 'Fully Government Subsidized (₹0)'}</div>
                  </div>

                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Active Training Batches ({centreBatches.filter((b: any) => b.program_id === centreSelectedProgForBatches.id).length})</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>Assigned Training Centre: {centreProfile?.name || 'Current Centre'}</span>
                  </h4>

                  {(() => {
                    const progBatches = centreBatches.filter((b: any) => b.program_id === centreSelectedProgForBatches.id);
                    if (progBatches.length === 0) {
                      return (
                        <div style={{ textAlign: 'center', padding: '2rem 1rem', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', color: '#64748b', fontSize: '0.85rem' }}>
                          No active training batches are currently scheduled for this programme at your centre.
                        </div>
                      );
                    }
                    return (
                      <div style={{ display: 'grid', gap: '0.85rem' }}>
                        {progBatches.map((b: any) => (
                          <div
                            key={b.id}
                            style={{
                              backgroundColor: '#ffffff',
                              border: '1px solid #e2e8f0',
                              borderRadius: '8px',
                              padding: '1rem',
                              boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                              <div>
                                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#f0fdfa', padding: '2px 6px', borderRadius: '4px', border: '1px solid #ccfbf1' }}>
                                  {b.code}
                                </span>
                                <h5 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', margin: '4px 0 0 0' }}>
                                  {b.batch_name}
                                </h5>
                              </div>
                              <span style={{ fontSize: '0.7rem', backgroundColor: '#dcfce7', color: '#166534', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
                                {b.status || 'ACTIVE'}
                              </span>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.4rem', fontSize: '0.78rem', color: '#475569', marginTop: '0.6rem', borderTop: '1px solid #f1f5f9', paddingTop: '0.6rem' }}>
                              <div><strong>Batch ID:</strong> #{b.id}</div>
                              <div><strong>Delivery Mode:</strong> {b.mode}</div>
                              <div><strong>Daily Timings:</strong> {b.timings}</div>
                              <div><strong>Weekly Schedule:</strong> {b.training_schedule}</div>
                              <div><strong>Assigned Trainer:</strong> {centreSelectedProgForBatches.trainer_name || 'Assigned Instructor'}</div>
                              <div>
                                <strong>Seat Capacity:</strong>{' '}
                                <span style={{ fontWeight: 700, color: '#0f172a' }}>
                                  {b.enrolled_count} / {b.total_seats}
                                </span>{' '}
                                (<span style={{ color: b.available_seats > 0 ? '#16a34a' : '#dc2626', fontWeight: 600 }}>{b.available_seats} Available</span>)
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  })()}

                  <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
                    <button
                      className="btn-navy-outline"
                      onClick={() => setCentreSelectedProgForBatches(null)}
                      style={{ padding: '0.5rem 1.25rem', fontSize: '0.85rem' }}
                    >
                      Close Batch Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}"""

if target_modal_end in content:
    content = content.replace(target_modal_end, new_modal_block, 1)
    print("3. Appended View Programme Batches Modal")
else:
    print("3. Failed to find target_modal_end")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("App.tsx updated successfully.")
