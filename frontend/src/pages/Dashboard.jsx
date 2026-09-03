function Dashboard({ onNewInterview }) {
  return (
    <div className="dashboard">
      <section className="dashboard-intro">
        <div>
          <p className="eyebrow">
            YOUR WORKSPACE
          </p>

          <h1>
            Prepare with purpose.
          </h1>

          <p className="intro-text">
            Practice realistic interviews tailored to
            the role, job description, and experience
            on your resume.
          </p>
        </div>

        <button
          className="primary-button dashboard-action"
          type="button"
          onClick={onNewInterview}
        >
          <span>+</span>
          Start new interview
        </button>
      </section>

      <section className="overview-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              OVERVIEW
            </p>

            <h2>
              Your interview activity
            </h2>
          </div>
        </div>

        <div className="overview-grid">
          <div className="overview-item">
            <span className="overview-label">
              Interviews completed
            </span>

            <strong>0</strong>

            <span className="overview-note">
              Start your first interview
            </span>
          </div>

          <div className="overview-item">
            <span className="overview-label">
              Average score
            </span>

            <strong>—</strong>

            <span className="overview-note">
              Available after your first interview
            </span>
          </div>

          <div className="overview-item">
            <span className="overview-label">
              Latest result
            </span>

            <strong>—</strong>

            <span className="overview-note">
              No interviews yet
            </span>
          </div>
        </div>
      </section>

      <section className="recent-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">
              RECENT
            </p>

            <h2>
              Interview history
            </h2>
          </div>

          <button
            className="text-button"
            type="button"
            onClick={() =>
              alert(
                "Interview history will be connected next."
              )
            }
          >
            View all
          </button>
        </div>

        <div className="empty-history">
          <div className="empty-history-mark">
            +
          </div>

          <div>
            <h3>
              No interviews yet
            </h3>

            <p>
              Complete your first AI interview and your
              results will appear here.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;