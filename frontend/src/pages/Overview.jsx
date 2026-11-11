
export default function Overview({ t }) {
  return (
    <>
      {/* Overview statistics */}
      <div className="section-title">
        <h2>{t.overview}</h2>
        <span>PHASE 01</span>
      </div>

      <div className="metric-grid">
        <article className="metric-card">
          <span>{t.sourceCount}</span>
          <strong>0</strong>
          <small>—</small>
        </article>

        <article className="metric-card">
          <span>{t.taskCount || t.runCount}</span>
          <strong>0</strong>
          <small>—</small>
        </article>

        <article className="metric-card">
          <span>{t.successCount}</span>
          <strong>0</strong>
          <small>—</small>
        </article>
      </div>

      {/* Current development phase and next steps */}
      <div className="panel-grid">
        <section className="panel">
          <div className="panel-kicker">IN PROGRESS</div>

          <h3>{t.phaseText}</h3>

          <p>{t.note}</p>

          <div className="progress-track">
            <span />
          </div>

          <div className="progress-caption">
            <span>Foundation setup</span>
            <span>Phase 1 / 5</span>
          </div>
        </section>

        <section className="panel">
          <div className="panel-kicker">{t.next}</div>

          <h3>{t.nextText}</h3>

          <div className="empty-state">
            <span>⌘</span>
            <p>{t.empty}</p>
          </div>
        </section>
      </div>

      <footer>
        WEB DATA LAB <span>·</span> LEARN · COLLECT · UNDERSTAND
      </footer>
    </>
  );
}
