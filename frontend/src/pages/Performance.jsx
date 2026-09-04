import {
  useEffect,
  useMemo,
  useState,
} from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

function Performance({
  onBack,
  onNewInterview,
}) {
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadPerformance();
  }, []);

  const loadPerformance = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/api/session/history`
      );

      if (!response.ok) {
        let message =
          "Unable to load performance data.";

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
        "Performance error:",
        error
      );

      setError(
        error.message ||
          "Unable to load performance data."
      );

    } finally {
      setLoading(false);
    }
  };

  const stats = useMemo(() => {
    const completed =
      interviews.filter(
        (item) =>
          item.status === "completed"
      );

    if (completed.length === 0) {
      return {
        completed: 0,
        average: null,
        best: null,
        averageTechnical: null,
        averageRelevance: null,
        averageCompleteness: null,
        averageCommunication: null,
      };
    }

    const average = (field) => {
      const values = completed
        .map((item) => Number(item[field]))
        .filter(
          (value) =>
            !Number.isNaN(value)
        );

      if (values.length === 0) {
        return null;
      }

      return (
        values.reduce(
          (sum, value) =>
            sum + value,
          0
        ) / values.length
      );
    };

    const overallScores = completed
      .map((item) =>
        Number(item.overall_score)
      )
      .filter(
        (value) =>
          !Number.isNaN(value)
      );

    return {
      completed:
        completed.length,

      average:
        average("overall_score"),

      best:
        overallScores.length > 0
          ? Math.max(...overallScores)
          : null,

      averageTechnical:
        average("technical_score"),

      averageRelevance:
        average("relevance_score"),

      averageCompleteness:
        average("completeness_score"),

      averageCommunication:
        average("communication_score"),
    };
  }, [interviews]);

  const formatScore = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return "—";
    }

    const numericValue = Number(value);

    if (Number.isNaN(numericValue)) {
      return "—";
    }

    return numericValue.toFixed(1);
  };

  const scoreWidth = (value) => {
    if (
      value === null ||
      value === undefined
    ) {
      return 0;
    }

    return Math.max(
      0,
      Math.min(
        100,
        Number(value) * 10
      )
    );
  };

  return (
    <div className="performance-page">

      {/* =========================================
          PAGE HEADER
      ========================================= */}

      <div className="performance-header">

        <div>

          <div className="eyebrow">
            PERFORMANCE
          </div>

          <h1>
            Track your progress
          </h1>

          <p className="performance-description">
            See how your interview performance
            changes over time.
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
        className="back-button performance-back"
        onClick={onBack}
      >
        <span>
          ←
        </span>

        Back to dashboard
      </button>


      {/* =========================================
          LOADING
      ========================================= */}

      {loading && (
        <div className="performance-state">

          <div className="performance-state-icon">
            ↗
          </div>

          <h2>
            Loading performance
          </h2>

          <p>
            Calculating your interview results.
          </p>

        </div>
      )}


      {/* =========================================
          ERROR
      ========================================= */}

      {!loading && error && (
        <div className="performance-state">

          <div className="performance-state-icon">
            !
          </div>

          <h2>
            Unable to load performance
          </h2>

          <p>
            {error}
          </p>

          <button
            type="button"
            className="secondary-button"
            onClick={loadPerformance}
          >
            Try again
          </button>

        </div>
      )}


      {/* =========================================
          PERFORMANCE CONTENT
      ========================================= */}

      {!loading && !error && (
        <>

          {/* SUMMARY */}

          <section className="performance-summary-grid">

            <div className="performance-summary-card">

              <span>
                Interviews completed
              </span>

              <strong>
                {stats.completed}
              </strong>

              <small>
                Completed sessions
              </small>

            </div>


            <div className="performance-summary-card">

              <span>
                Average score
              </span>

              <strong>
                {formatScore(
                  stats.average
                )}

                <small>
                  /10
                </small>
              </strong>

              <small>
                Across completed interviews
              </small>

            </div>


            <div className="performance-summary-card">

              <span>
                Best score
              </span>

              <strong>
                {formatScore(
                  stats.best
                )}

                <small>
                  /10
                </small>
              </strong>

              <small>
                Highest overall result
              </small>

            </div>

          </section>


          {/* EMPTY STATE */}

          {stats.completed === 0 ? (

            <div className="performance-empty">

              <div className="performance-empty-icon">
                ↗
              </div>

              <div>

                <div className="eyebrow">
                  START TRACKING
                </div>

                <h2>
                  Your performance data will
                  appear here
                </h2>

                <p>
                  Complete an interview to start
                  tracking your technical,
                  relevance, completeness,
                  and communication scores.
                </p>

                <button
                  type="button"
                  className="primary-button"
                  onClick={onNewInterview}
                >
                  Start an interview
                  <span>
                    →
                  </span>
                </button>

              </div>

            </div>

          ) : (

            <section className="performance-section">

              <div className="performance-section-header">

                <div>

                  <div className="eyebrow">
                    SCORE BREAKDOWN
                  </div>

                  <h2>
                    Average interview performance
                  </h2>

                  <p>
                    See how you perform across
                    the main interview evaluation areas.
                  </p>

                </div>

              </div>


              <div className="performance-bars">

                <PerformanceBar
                  label="Technical"
                  value={
                    stats.averageTechnical
                  }
                  width={scoreWidth(
                    stats.averageTechnical
                  )}
                />

                <PerformanceBar
                  label="Relevance"
                  value={
                    stats.averageRelevance
                  }
                  width={scoreWidth(
                    stats.averageRelevance
                  )}
                />

                <PerformanceBar
                  label="Completeness"
                  value={
                    stats.averageCompleteness
                  }
                  width={scoreWidth(
                    stats.averageCompleteness
                  )}
                />

                <PerformanceBar
                  label="Communication"
                  value={
                    stats.averageCommunication
                  }
                  width={scoreWidth(
                    stats.averageCommunication
                  )}
                />

              </div>

            </section>

          )}

        </>
      )}

    </div>
  );
}


/* =========================================
   PERFORMANCE BAR
========================================= */

function PerformanceBar({
  label,
  value,
  width,
}) {
  const formattedValue =
    value === null ||
    value === undefined
      ? "—"
      : `${Number(value).toFixed(1)}/10`;

  return (
    <div className="performance-bar-row">

      <div className="performance-bar-header">

        <span>
          {label}
        </span>

        <strong>
          {formattedValue}
        </strong>

      </div>


      <div className="performance-bar-track">

        <div
          className="performance-bar-fill"
          style={{
            width: `${width}%`,
          }}
        />

      </div>

    </div>
  );
}

export default Performance;