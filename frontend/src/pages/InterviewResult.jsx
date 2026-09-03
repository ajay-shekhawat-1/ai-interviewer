function InterviewResult({ onBackToDashboard }) {
  return (
    <div className="result-page">
      <div className="result-container">
        <header className="result-heading">
          <p className="eyebrow">
            INTERVIEW COMPLETE
          </p>

          <h1>
            Here's how you performed.
          </h1>

          <p>
            Your interview has been evaluated across
            the areas that matter for this role.
          </p>
        </header>

        <section className="result-score">
          <div className="score-number">
            82
          </div>

          <div className="score-denominator">
            / 100
          </div>

          <div className="result-status">
            PASS
          </div>

          <p>
            Recommended for the next round
          </p>
        </section>

        <section className="result-metrics">
          <Metric
            label="Technical knowledge"
            score={85}
          />

          <Metric
            label="Problem solving"
            score={78}
          />

          <Metric
            label="Project knowledge"
            score={88}
          />

          <Metric
            label="Communication"
            score={80}
          />
        </section>

        <section className="result-feedback">
          <div className="feedback-column">
            <p className="eyebrow">
              STRENGTHS
            </p>

            <ul>
              <li>
                Good machine learning fundamentals
              </li>

              <li>
                Strong project explanation
              </li>

              <li>
                Clear technical reasoning
              </li>
            </ul>
          </div>

          <div className="feedback-column">
            <p className="eyebrow">
              AREAS TO IMPROVE
            </p>

            <ul>
              <li>
                SQL query optimization
              </li>

              <li>
                Model evaluation metrics
              </li>
            </ul>
          </div>
        </section>

        <div className="result-actions">
          <button
            className="primary-button"
            type="button"
            onClick={onBackToDashboard}
          >
            Back to overview
          </button>

          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              window.location.reload();
            }}
          >
            Practice again
          </button>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, score }) {
  return (
    <div className="metric">
      <div className="metric-top">
        <span>{label}</span>

        <strong>{score}</strong>
      </div>

      <div className="metric-track">
        <div
          className="metric-fill"
          style={{
            width: `${score}%`,
          }}
        ></div>
      </div>
    </div>
  );
}

export default InterviewResult;