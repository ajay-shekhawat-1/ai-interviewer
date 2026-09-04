import { useEffect, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

function History({
  onBack,
  onNewInterview,
  onViewReport,
}) {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [openingReport, setOpeningReport] = useState(null);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/api/session/history`
      );

      if (!response.ok) {
        let message =
          "Unable to load interview history.";

        try {
          const data = await response.json();

          if (data?.detail) {
            message = data.detail;
          }
        } catch {
          // Ignore invalid error response.
        }

        throw new Error(message);
      }

      const data = await response.json();

      setInterviews(
        Array.isArray(data?.interviews)
          ? data.interviews
          : []
      );

    } catch (error) {
      console.error(
        "History error:",
        error
      );

      setError(
        error.message ||
          "Unable to load interview history."
      );

    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = async (sessionId) => {
    if (!sessionId) {
      setError(
        "Interview session ID is missing."
      );
      return;
    }

    try {
      setOpeningReport(sessionId);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/api/evaluation/report/${sessionId}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            "Unable to retrieve the interview report."
        );
      }

      console.log(
        "Retrieved interview report:",
        data
      );

      onViewReport(sessionId, data);

    } catch (error) {
      console.error(
        "Report retrieval error:",
        error
      );

      setError(
        error.message ||
          "Unable to retrieve the interview report."
      );

    } finally {
      setOpeningReport(null);
    }
  };

  const formatDate = (value) => {
    if (!value) {
      return "Unknown date";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleDateString(
      undefined,
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
  };

  const formatScore = (score) => {
    if (
      score === null ||
      score === undefined ||
      score === ""
    ) {
      return "—";
    }

    const numericScore = Number(score);

    if (Number.isNaN(numericScore)) {
      return "—";
    }

    return numericScore.toFixed(1);
  };

  return (
    <div className="history-page">

      {/* =========================================
          PAGE HEADER
      ========================================= */}

      <div className="history-header">

        <div>

          <div className="eyebrow">
            INTERVIEW HISTORY
          </div>

          <h1>
            Your interview history
          </h1>

          <p className="history-description">
            Review your previous interviews,
            scores, and detailed reports.
          </p>

        </div>

        <button
          type="button"
          className="primary-button"
          onClick={onNewInterview}
        >
          <span>
            +
          </span>

          New interview
        </button>

      </div>


      {/* =========================================
          BACK
      ========================================= */}

      <button
        type="button"
        className="back-button history-back"
        onClick={onBack}
      >
        <span>
          ←
        </span>

        Back to dashboard
      </button>


      {/* =========================================
          ERROR
      ========================================= */}

      {!loading && error && (
        <div className="history-error-banner">

          <span>
            !
          </span>

          <p>
            {error}
          </p>

          <button
            type="button"
            onClick={() => setError("")}
          >
            Dismiss
          </button>

        </div>
      )}


      {/* =========================================
          LOADING
      ========================================= */}

      {loading && (
        <div className="history-state">

          <div className="history-state-icon">
            ◷
          </div>

          <h2>
            Loading your interviews...
          </h2>

          <p>
            Fetching your interview history.
          </p>

        </div>
      )}


      {/* =========================================
          EMPTY
      ========================================= */}

      {!loading &&
        interviews.length === 0 && (
          <div className="history-empty">

            <div className="history-empty-icon">
              ◷
            </div>

            <div>

              <div className="eyebrow">
                NO ACTIVITY
              </div>

              <h2>
                No interviews yet
              </h2>

              <p>
                Complete your first AI interview
                and your results will appear here.
              </p>

              <button
                type="button"
                className="primary-button"
                onClick={onNewInterview}
              >
                Start your first interview

                <span>
                  →
                </span>
              </button>

            </div>

          </div>
        )}


      {/* =========================================
          INTERVIEW LIST
      ========================================= */}

      {!loading &&
        interviews.length > 0 && (

          <div className="history-list">

            {interviews.map((interview) => {

              const isCompleted =
                interview.status ===
                "completed";

              const isOpening =
                openingReport ===
                interview.session_id;

              return (
                <article
                  className="history-card"
                  key={interview.session_id}
                >

                  {/* =================================
                      MAIN INFORMATION
                  ================================= */}

                  <div className="history-card-main">

                    <div className="history-card-top">

                      <div>

                        <h2>
                          {interview.job_title ||
                            "Interview"}
                        </h2>

                        <p>
                          {interview.candidate_name ||
                            "Candidate"}
                        </p>

                      </div>

                      <span
                        className={`history-status ${
                          isCompleted
                            ? "history-status-completed"
                            : "history-status-active"
                        }`}
                      >
                        {isCompleted
                          ? "Completed"
                          : "In progress"}
                      </span>

                    </div>


                    {/* =================================
                        META INFORMATION
                    ================================= */}

                    <div className="history-meta">

                      <div className="history-meta-item">

                        <span>
                          Date
                        </span>

                        <strong>
                          {formatDate(
                            interview.created_at
                          )}
                        </strong>

                      </div>


                      <div className="history-meta-item">

                        <span>
                          Questions
                        </span>

                        <strong>
                          {interview.answered_questions ??
                            0}

                          {" / "}

                          {interview.total_questions ??
                            0}
                        </strong>

                      </div>


                      <div className="history-meta-item">

                        <span>
                          Overall score
                        </span>

                        <strong>
                          {formatScore(
                            interview.overall_score
                          )}

                          <small>
                            /10
                          </small>
                        </strong>

                      </div>

                    </div>

                  </div>


                  {/* =================================
                      ACTION
                  ================================= */}

                  <div className="history-card-action">

                    {isCompleted ? (

                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          handleViewReport(
                            interview.session_id
                          )
                        }
                        disabled={isOpening}
                      >

                        {isOpening
                          ? "Loading report..."
                          : "View report"}

                        {!isOpening && (
                          <span>
                            →
                          </span>
                        )}

                      </button>

                    ) : (

                      <button
                        type="button"
                        className="secondary-button"
                        onClick={() =>
                          handleViewReport(
                            interview.session_id
                          )
                        }
                        disabled={isOpening}
                      >

                        {isOpening
                          ? "Loading report..."
                          : "View partial report"}

                        {!isOpening && (
                          <span>
                            →
                          </span>
                        )}

                      </button>

                    )}

                  </div>

                </article>
              );
            })}

          </div>
        )}

    </div>
  );
}

export default History;