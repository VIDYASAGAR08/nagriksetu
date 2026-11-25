path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                    <button
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

replacement = """                    <button
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
          )}

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

if target in content:
    content = content.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Modal successfully appended.")
else:
    print("Could not find target block.")
