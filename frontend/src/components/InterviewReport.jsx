function formatScore(score) {
  const value = Number(score);

  if (Number.isNaN(value)) {
    return "0.0";
  }

  return Math.max(0, Math.min(10, value)).toFixed(1);
}

function getScorePercentage(score) {
  const value = Number(score);

  if (Number.isNaN(value)) {
    return 0;
  }

  return Math.max(0, Math.min(100, (value / 10) * 100));
}

function getScoreLabel(score) {
  const value = Number(score);

  if (Number.isNaN(value)) {
    return "Not rated";
  }

  if (value >= 8) {
    return "Excellent";
  }

  if (value >= 6) {
    return "Good";
  }

  if (value >= 4) {
    return "Moderate";
  }

  return "Needs improvement";
}

function getInitials(name) {
  if (!name) {
    return "C";
  }

  const parts = name
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }

  return (
    parts[0][0] +
    parts[parts.length - 1][0]
  ).toUpperCase();
}

function ScoreBar({ label, score }) {
  const percentage = getScorePercentage(score);

  return (
    <div className="report-score-row">
      <div className="report-score-header">
        <span className="report-score-label">
          {label}
        </span>

        <span className="report-score-value">
          {formatScore(score)}
          <span>/10</span>
        </span>
      </div>

      <div
        className="report-score-track"
        aria-label={`${label} score`}
      >
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
  const numericScore =
    Number(score) || 0;

  return (
    <div className="report-score-card">
      <div className="report-score-card-top">
        <span className="report-score-card-label">
          {label}
        </span>

        <span className="report-score-card-dot" />
      </div>

      <div className="report-score-card-number">
        <strong>
          {formatScore(score)}
        </strong>

        <span>/10</span>
      </div>

      <span className="report-score-card-status">
        {getScoreLabel(numericScore)}
      </span>
    </div>
  );
}

function ListSection({
  title,
  description,
  items,
  emptyText,
  variant = "default",
}) {
  const validItems = Array.isArray(items)
    ? items.filter(Boolean)
    : [];

  const isStrengths =
    variant === "strengths";

  return (
    <section
      className={`report-section report-list-section report-list-section-${variant}`}
    >
      <div className="report-section-heading">
        <div>
          <p className="report-eyebrow">
            {isStrengths
              ? "WHAT WENT WELL"
              : "DEVELOPMENT AREAS"}
          </p>

          <h2>{title}</h2>

          {description && (
            <p className="report-section-description">
              {description}
            </p>
          )}
        </div>

        {validItems.length > 0 && (
          <span className="report-item-count">
            {validItems.length}
          </span>
        )}
      </div>

      {validItems.length > 0 ? (
        <ul className="report-list">
          {validItems.map(
            (item, index) => (
              <li
                key={`${item}-${index}`}
              >
                <span className="report-list-marker">
                  {isStrengths ? "✓" : "↗"}
                </span>

                <span>{item}</span>
              </li>
            )
          )}
        </ul>
      ) : (
        <p className="report-empty">
          {emptyText}
        </p>
      )}
    </section>
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
          <div className="report-empty-icon">
            !
          </div>

          <p className="report-eyebrow">
            REPORT UNAVAILABLE
          </p>

          <h1>
            Interview Report Unavailable
          </h1>

          <p>
            We could not load the final
            interview report. You can
            start a new interview and
            try again.
          </p>

          <button
            className="report-primary-button"
            type="button"
            onClick={onRestart}
          >
            Start New Interview
            <span>→</span>
          </button>
        </div>
      </div>
    );
  }

  const totalQuestions =
    Number(report.total_questions) || 0;

  const answeredQuestions =
    Number(report.answered_questions) || 0;

  const overallScore =
    Number(report.overall_score) || 0;

  const completionPercentage =
    totalQuestions > 0
      ? Math.min(
          100,
          (answeredQuestions /
            totalQuestions) *
            100
        )
      : 0;

  const candidateName =
    report.candidate_name ||
    "Candidate";

  const overallPercentage =
    getScorePercentage(overallScore);

  return (
    <div className="report-page">
      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <div className="report-topbar">
        <div className="report-topbar-left">
          <div className="report-topbar-mark">
            AI
          </div>

          <div>
            <span className="report-topbar-title">
              Interview assessment
            </span>

            <span className="report-topbar-subtitle">
              Final performance report
            </span>
          </div>
        </div>

        <div className="report-completed-badge">
          <span className="report-completed-dot" />
          Interview completed
        </div>
      </div>

      {/* =====================================================
          REPORT HERO
      ===================================================== */}

      <header className="report-hero">
        <div className="report-hero-main">
          <div className="report-candidate-row">
            <div className="report-candidate-avatar">
              {getInitials(candidateName)}
            </div>

            <div>
              <p className="report-eyebrow">
                FINAL ASSESSMENT
              </p>

              <h1>
                Interview Performance
              </h1>

              <p className="report-candidate">
                Candidate{" "}
                <strong>
                  {candidateName}
                </strong>
              </p>
            </div>
          </div>

          <p className="report-hero-description">
            A structured assessment of your
            technical knowledge, answer quality,
            relevance, completeness, and
            communication throughout the interview.
          </p>
        </div>

        <div className="report-overall-panel">
          <div className="report-overall-panel-top">
            <span>
              OVERALL SCORE
            </span>

            <span className="report-overall-status">
              {getScoreLabel(overallScore)}
            </span>
          </div>

          <div className="report-overall-score">
            <strong>
              {formatScore(overallScore)}
            </strong>

            <span>/10</span>
          </div>

          <div className="report-overall-track">
            <div
              className="report-overall-fill"
              style={{
                width: `${overallPercentage}%`,
              }}
            />
          </div>

          <p>
            Overall interview performance
          </p>
        </div>
      </header>

      {/* =====================================================
          EXECUTIVE SUMMARY
      ===================================================== */}

      <section className="report-summary-card">
        <div className="report-summary-main">
          <p className="report-eyebrow">
            EXECUTIVE SUMMARY
          </p>

          <h2>
            Performance at a glance
          </h2>

          <p className="report-summary-text">
            {report.summary ||
              "No performance summary is available."}
          </p>
        </div>

        <div className="report-recommendation">
          <div className="report-recommendation-icon">
            →
          </div>

          <div>
            <span className="report-recommendation-label">
              RECOMMENDATION
            </span>

            <p>
              {report.recommendation ||
                "No recommendation is available."}
            </p>
          </div>
        </div>
      </section>

      {/* =====================================================
          INTERVIEW STATS
      ===================================================== */}

      <section className="report-stats-strip">
        <div className="report-stat">
          <span>QUESTIONS</span>

          <strong>
            {totalQuestions}
          </strong>

          <small>
            Total asked
          </small>
        </div>

        <div className="report-stat">
          <span>ANSWERED</span>

          <strong>
            {answeredQuestions}
          </strong>

          <small>
            Completed
          </small>
        </div>

        <div className="report-stat">
          <span>COMPLETION</span>

          <strong>
            {Math.round(
              completionPercentage
            )}
            %
          </strong>

          <small>
            Interview progress
          </small>
        </div>

        <div className="report-stat">
          <span>OVERALL</span>

          <strong>
            {formatScore(overallScore)}
          </strong>

          <small>
            Out of 10
          </small>
        </div>
      </section>

      {/* =====================================================
          EVALUATION SCORES
      ===================================================== */}

      <section className="report-section report-evaluation-section">
        <div className="report-section-heading">
          <div>
            <p className="report-eyebrow">
              PERFORMANCE
            </p>

            <h2>
              Evaluation scores
            </h2>

            <p className="report-section-description">
              Your performance across the four
              core interview evaluation dimensions.
            </p>
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

      {/* =====================================================
          SCORE BREAKDOWN
      ===================================================== */}

      <section className="report-score-breakdown">
        <div className="report-score-breakdown-header">
          <div>
            <p className="report-eyebrow">
              SCORE BREAKDOWN
            </p>

            <h2>
              Performance overview
            </h2>
          </div>

          <span>
            Higher score = stronger performance
          </span>
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

      {/* =====================================================
          STRENGTHS + IMPROVEMENTS
      ===================================================== */}

      <div className="report-two-column">
        <ListSection
          title="Strengths"
          items={report.strengths}
          description="Areas where your interview performance stood out."
          emptyText="No major strengths were identified."
          variant="strengths"
        />

        <ListSection
          title="Areas to improve"
          items={report.weaknesses}
          description="Focus areas that can improve your next interview."
          emptyText="No major improvement areas were identified."
          variant="improvements"
        />
      </div>

      {/* =====================================================
          SKILL GAPS
      ===================================================== */}

      <section className="report-section report-skill-section">
        <div className="report-section-heading">
          <div>
            <p className="report-eyebrow">
              DEVELOPMENT
            </p>

            <h2>
              Skill gaps
            </h2>

            <p className="report-section-description">
              Topics that could be strengthened
              before your next interview.
            </p>
          </div>

          {Array.isArray(
            report.skill_gaps
          ) &&
            report.skill_gaps.length > 0 && (
              <span className="report-item-count">
                {report.skill_gaps.length}
              </span>
            )}
        </div>

        {Array.isArray(
          report.skill_gaps
        ) &&
        report.skill_gaps.length > 0 ? (
          <div className="report-tags">
            {report.skill_gaps.map(
              (skill, index) => (
                <span
                  className="report-tag"
                  key={`${skill}-${index}`}
                >
                  <span>+</span>
                  {skill}
                </span>
              )
            )}
          </div>
        ) : (
          <div className="report-no-gaps">
            <span>✓</span>

            <p>
              No significant skill gaps were
              identified from this interview.
            </p>
          </div>
        )}
      </section>

      {/* =====================================================
          QUESTION REVIEW
      ===================================================== */}

      <section className="report-section report-question-section">
        <div className="report-section-heading">
          <div>
            <p className="report-eyebrow">
              DETAILED REVIEW
            </p>

            <h2>
              Question-by-question review
            </h2>

            <p className="report-section-description">
              Review each response and the feedback
              generated by the AI interviewer.
            </p>
          </div>

          <span className="report-question-count">
            {answeredQuestions} /{" "}
            {totalQuestions} answered
          </span>
        </div>

        <div className="report-question-list">
          {Array.isArray(
            report.question_results
          ) &&
          report.question_results.length >
            0 ? (
            report.question_results.map(
              (result, index) => {
                const evaluation =
                  result.evaluation || {};

                const questionScore =
                  Number(
                    evaluation.overall_score
                  ) || 0;

                return (
                  <article
                    className="report-question-card"
                    key={
                      result.question_id ||
                      `question-${index}`
                    }
                  >
                    <div className="report-question-top">
                      <div className="report-question-index">
                        <span>
                          {String(
                            index + 1
                          ).padStart(2, "0")}
                        </span>

                        <span>
                          QUESTION
                        </span>
                      </div>

                      <div className="report-question-score">
                        <strong>
                          {formatScore(
                            questionScore
                          )}
                        </strong>

                        <span>
                          /10
                        </span>
                      </div>
                    </div>

                    <h3>
                      {result.question ||
                        "Question unavailable."}
                    </h3>

                    <div className="report-answer-block">
                      <span className="report-detail-label">
                        CANDIDATE ANSWER
                      </span>

                      <p>
                        {result.answer ||
                          "No answer provided."}
                      </p>
                    </div>

                    {evaluation.feedback && (
                      <div className="report-feedback-block">
                        <div className="report-feedback-heading">
                          <span className="report-feedback-icon">
                            AI
                          </span>

                          <span className="report-detail-label">
                            AI FEEDBACK
                          </span>
                        </div>

                        <p>
                          {evaluation.feedback}
                        </p>
                      </div>
                    )}

                    <div className="report-question-scores">
                      <div>
                        <span>
                          Technical
                        </span>

                        <strong>
                          {formatScore(
                            evaluation.technical_score
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Relevance
                        </span>

                        <strong>
                          {formatScore(
                            evaluation.relevance_score
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Completeness
                        </span>

                        <strong>
                          {formatScore(
                            evaluation.completeness_score
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Communication
                        </span>

                        <strong>
                          {formatScore(
                            evaluation.communication_score
                          )}
                        </strong>
                      </div>
                    </div>
                  </article>
                );
              }
            )
          ) : (
            <div className="report-question-empty">
              <span>—</span>

              <p>
                No question-level results are
                available.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* =====================================================
          FINAL ACTION
      ===================================================== */}

      <footer className="report-actions">
        <div className="report-actions-text">
          <p className="report-eyebrow">
            KEEP PRACTICING
          </p>

          <h3>
            Ready for another round?
          </h3>

          <p>
            Practice again and use this report
            to improve your interview performance.
          </p>
        </div>

        <button
          className="report-primary-button"
          type="button"
          onClick={onRestart}
        >
          Start New Interview
          <span>→</span>
        </button>
      </footer>
    </div>
  );
}

export default InterviewReport;