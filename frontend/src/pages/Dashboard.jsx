function Dashboard({ onNewInterview, onViewHistory }) {
  return (
    <div className="dashboard-page">

      <section className="dashboard-header">
        <div>
          <div className="eyebrow">DASHBOARD</div>

          <h1>Interview workspace</h1>

          <p>
            Practice interviews tailored to your resume and target role.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={onNewInterview}
        >
          + New interview
        </button>
      </section>


      <section className="dashboard-main">

        <div className="welcome-panel">

          <div className="welcome-content">
            <span className="welcome-label">
              READY TO PRACTICE
            </span>

            <h2>
              Start your next interview.
            </h2>

            <p>
              Upload your resume, add the job description,
              and let the AI interviewer handle the rest.
            </p>

            <button
              className="primary-button"
              type="button"
              onClick={onNewInterview}
            >
              Start interview
              <span>→</span>
            </button>
          </div>

          <div className="welcome-mark">
            AI
          </div>

        </div>


        <div className="dashboard-section">

          <div className="section-header">
            <div>
              <h2>Overview</h2>
              <p>Your interview activity.</p>
            </div>
          </div>


          <div className="stats-grid">

            <div className="stat-item">
              <span>INTERVIEWS</span>
              <strong>0</strong>
              <small>Completed</small>
            </div>

            <div className="stat-item">
              <span>AVERAGE SCORE</span>
              <strong>—</strong>
              <small>After first interview</small>
            </div>

            <div className="stat-item">
              <span>LATEST RESULT</span>
              <strong>—</strong>
              <small>No result yet</small>
            </div>

          </div>

        </div>


        <div className="dashboard-section">

          <div className="section-header">
            <div>
              <h2>Recent interviews</h2>
              <p>Your latest sessions will appear here.</p>
            </div>

            <button
              className="text-button"
              type="button"
              onClick={onViewHistory}
            >
              View history →
            </button>
          </div>


          <div className="recent-empty">

            <div className="recent-empty-icon">
              ◷
            </div>

            <div>
              <strong>No interviews yet</strong>

              <p>
                Complete your first interview to see it here.
              </p>
            </div>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;