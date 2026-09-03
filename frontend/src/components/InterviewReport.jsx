
function ScoreBar({ label, score }) {
  const percentage = Math.max(0, Math.min(100, (score / 10) * 100));

  return (
    <div className="report-score-row">
      <div className="report-score-header">
        <span className="report-score-label">
          {label}
        </span>

        <span className="report-score-value">
          {Number(score).toFixed(1)}/10
        </span>
      </div>

      <div className="report-score-track">
        <div
          className="report-score-fill"
          style={{
            width: `${percentage}%`,
          }}
        />
      </div>
    </div>
  );
}

function ScoreCard({ label, score }) {
  return (
    <div className="report-score-card">
      <div className="report-score-card-label">
        {label}
      </div>

      <div className="report-score-card-value">
        {Number(score).toFixed(1)}
      </div>

      <div className="report-score-card-max">
        / 10
      </div>
    </div>
  );
}

function ListSection({
  title,
  items,
  emptyText,
}) {
  return (
    <div className="report-section">
      <h3>{title}</h3>

      {items && items.length > 0 ? (
        <ul className="report-list">
          {items.map((item, index) => (
            <li key={`${item}-${index}`}>
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="report-empty">
          {emptyText}
        </p>
      )}
    </div>
  );
}

function InterviewReport({
  report,
  onRestart,
}) {
  if (!report) {
    return (
      <div className="report-page">
        <div className="report-empty-state">
          <h2>Interview Report Unavailable</h2>

          <p>
            We could not load the final interview report.
          </p>

          <button
            className="report-primary-button"
            onClick={onRestart}
          >
            Start New Interview
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="report-page">

      {/* Header */}
      <div className="report-header">

        <div>
          <p className="report-eyebrow">
            INTERVIEW COMPLETE
          </p>

          <h1>
            Interview Performance Report
          </h1>

          <p className="report-candidate">
            Candidate:{" "}
            <strong>
              {report.candidate_name}
            </strong>
          </p>
        </div>

        <div className="report-overall-score">
          <span className="report-overall-label">
            Overall Score
          </span>

          <span className="report-overall-value">
            {Number(report.overall_score).toFixed(1)}
          </span>

          <span className="report-overall-max">
            / 10
          </span>
        </div>

      </div>

      {/* Summary */}
      <div className="report-summary-card">

        <div>
          <h2>Performance Summary</h2>

          <p>
            {report.summary}
          </p>
        </div>

        <div className="report-recommendation">

          <span className="report-recommendation-label">
            Recommendation
          </span>

          <p>
            {report.recommendation}
          </p>

        </div>

      </div>

      {/* Score Cards */}
      <section className="report-section">

        <div className="report-section-heading">
          <div>
            <p className="report-eyebrow">
              PERFORMANCE
            </p>

            <h2>
              Evaluation Scores
            </h2>
          </div>
        </div>

        <div className="report-score-grid">

          <ScoreCard
            label="Technical"
            score={report.technical_score}
          />

          <ScoreCard
            label="Relevance"
            score={report.relevance_score}
          />

          <ScoreCard
            label="Completeness"
            score={report.completeness_score}
          />

          <ScoreCard
            label="Communication"
            score={report.communication_score}
          />

        </div>

      </section>

      {/* Score Bars */}
      <section className="report-section report-score-bars-section">

        <div className="report-section-heading">
          <div>
            <p className="report-eyebrow">
              SCORE BREAKDOWN
            </p>

            <h2>
              Performance Overview
            </h2>
          </div>
        </div>

        <div className="report-score-bars">

          <ScoreBar
            label="Technical"
            score={report.technical_score}
          />

          <ScoreBar
            label="Relevance"
            score={report.relevance_score}
          />

          <ScoreBar
            label="Completeness"
            score={report.completeness_score}
          />

          <ScoreBar
            label="Communication"
            score={report.communication_score}
          />

        </div>

      </section>

      {/* Strengths and weaknesses */}
      <div className="report-two-column">

        <ListSection
          title="Strengths"
          items={report.strengths}
          emptyText="No major strengths were identified."
        />

        <ListSection
          title="Areas to Improve"
          items={report.weaknesses}
          emptyText="No major weaknesses were identified."
        />

      </div>

      {/* Skill gaps */}
      <section className="report-section">

        <h2>
          Skill Gaps
        </h2>

        {report.skill_gaps &&
        report.skill_gaps.length > 0 ? (
          <div className="report-tags">

            {report.skill_gaps.map(
              (skill, index) => (
                <span
                  className="report-tag"
                  key={`${skill}-${index}`}
                >
                  {skill}
                </span>
              )
            )}

          </div>
        ) : (
          <p className="report-empty">
            No significant skill gaps were identified.
          </p>
        )}

      </section>

      {/* Question Results */}
      <section className="report-section">

        <div className="report-section-heading">

          <div>
            <p className="report-eyebrow">
              DETAILED REVIEW
            </p>

            <h2>
              Question-by-Question Review
            </h2>
          </div>

          <span className="report-question-count">
            {report.answered_questions} /{" "}
            {report.total_questions} answered
          </span>

        </div>

        <div className="report-question-list">

          {report.question_results &&
          report.question_results.length > 0 ? (
            report.question_results.map(
              (result, index) => {

                const evaluation =
                  result.evaluation || {};

                return (
                  <div
                    className="report-question-card"
                    key={
                      result.question_id ||
                      index
                    }
                  >

                    <div className="report-question-top">

                      <span className="report-question-number">
                        Question {index + 1}
                      </span>

                      <span className="report-question-score">
                        {Number(
                          evaluation.overall_score || 0
                        ).toFixed(1)}
                        /10
                      </span>

                    </div>

                    <h3>
                      {result.question}
                    </h3>

                    <div className="report-answer">

                      <span>
                        Candidate Answer
                      </span>

                      <p>
                        {result.answer ||
                          "No answer provided."}
                      </p>

                    </div>

                    {evaluation.feedback && (
                      <div className="report-feedback">

                        <span>
                          Feedback
                        </span>

                        <p>
                          {evaluation.feedback}
                        </p>

                      </div>
                    )}

                  </div>
                );
              }
            )
          ) : (
            <p className="report-empty">
              No question-level results are available.
            </p>
          )}

        </div>

      </section>

      {/* Footer action */}
      <div className="report-actions">

        <button
          className="report-primary-button"
          onClick={onRestart}
        >
          Start New Interview
        </button>

      </div>

    </div>
  );
}

export default InterviewReport;