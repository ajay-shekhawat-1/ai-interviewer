import { useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

function InterviewSetup({ onStartInterview, onBack }) {
  const [role, setRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState(null);
  const [github, setGithub] = useState("");
  const [instructions, setInstructions] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      if (!resume) {
        throw new Error("Please upload your resume.");
      }

      if (!jobDescription.trim()) {
        throw new Error("Please enter the job description.");
      }

      /* Upload resume */

      const resumeFormData = new FormData();

      resumeFormData.append(
        "candidate_name",
        "Candidate"
      );

      resumeFormData.append(
        "job_description",
        jobDescription
      );

      resumeFormData.append(
        "file",
        resume
      );

      const resumeResponse = await fetch(
        `${API_BASE_URL}/api/candidate-profile/upload-resume`,
        {
          method: "POST",
          body: resumeFormData,
        }
      );

      const resumeData = await resumeResponse.json();

      if (!resumeResponse.ok) {
        throw new Error(
          resumeData.detail ||
            "Failed to upload resume."
        );
      }

      const candidateId = resumeData.candidate_id;

      if (!candidateId) {
        throw new Error(
          "Resume uploaded, but candidate ID was not returned."
        );
      }


      /* Create job description */

      const jdResponse = await fetch(
        `${API_BASE_URL}/api/jd/create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: role.trim() || "Job Position",
            raw_text: jobDescription,
          }),
        }
      );

      const jdData = await jdResponse.json();

      if (!jdResponse.ok) {
        throw new Error(
          jdData.detail ||
            "Failed to create job description."
        );
      }

      const jobDescriptionId =
        jdData.id ||
        jdData.job_description_id;

      if (!jobDescriptionId) {
        throw new Error(
          "Job description created, but ID was not returned."
        );
      }


      /* Start interview */

      const interviewResponse = await fetch(
        `${API_BASE_URL}/api/interview/start`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            candidate_id: candidateId,
            job_description_id: jobDescriptionId,
          }),
        }
      );

      const interviewData =
        await interviewResponse.json();

      if (!interviewResponse.ok) {
        throw new Error(
          interviewData.detail ||
            "Failed to start interview."
        );
      }

      const sessionId =
        interviewData.session?.session_id;

      if (!sessionId) {
        throw new Error(
          "Interview started, but session ID was not returned."
        );
      }


      onStartInterview({
        candidateId,
        jobDescriptionId,
        sessionId,
        role,
        jobDescription,
        github,
        instructions,
        interview: interviewData,
      });

    } catch (err) {
      console.error(
        "Interview setup error:",
        err
      );

      setError(
        err.message ||
          "Something went wrong while starting the interview."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="setup-page">

      <button
        className="back-button"
        type="button"
        onClick={onBack}
        disabled={loading}
      >
        ← Back
      </button>


      <div className="setup-heading">

        <div className="eyebrow">
          NEW INTERVIEW
        </div>

        <h1>Set up your interview</h1>

        <p>
          Add the role, job description, and resume.
        </p>

      </div>


      <form
        className="setup-form"
        onSubmit={handleSubmit}
      >

        <section className="setup-section">

          <div className="setup-section-heading">
            <span>01</span>

            <div>
              <h2>Target role</h2>
              <p>The position you are preparing for.</p>
            </div>
          </div>

          <div className="form-group">

            <label htmlFor="role">
              Role
            </label>

            <input
              id="role"
              type="text"
              placeholder="e.g. Data Scientist"
              value={role}
              onChange={(event) =>
                setRole(event.target.value)
              }
              disabled={loading}
              required
            />

          </div>

        </section>


        <section className="setup-section">

          <div className="setup-section-heading">
            <span>02</span>

            <div>
              <h2>Job description</h2>
              <p>Used to create relevant questions.</p>
            </div>
          </div>

          <div className="form-group">

            <label htmlFor="jobDescription">
              Job description
            </label>

            <textarea
              id="jobDescription"
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(event) =>
                setJobDescription(event.target.value)
              }
              rows={7}
              disabled={loading}
              required
            />

          </div>

        </section>


        <section className="setup-section">

          <div className="setup-section-heading">
            <span>03</span>

            <div>
              <h2>Your resume</h2>
              <p>Used to personalize your interview.</p>
            </div>
          </div>

          <div className="form-group">

            <label>
              Resume
            </label>

            <label
              className={`resume-upload ${
                loading ? "upload-disabled" : ""
              }`}
            >

              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(event) =>
                  setResume(
                    event.target.files?.[0] || null
                  )
                }
                disabled={loading}
                required
              />

              <div className="upload-symbol">
                ↑
              </div>

              <div className="upload-content">

                <strong>
                  {resume
                    ? resume.name
                    : "Choose your resume"}
                </strong>

                <span>
                  {resume
                    ? "Ready to upload"
                    : "PDF or DOCX · Max 5 MB"}
                </span>

              </div>

              <span className="upload-action">
                Browse
              </span>

            </label>

          </div>


          <div className="form-group">

            <label htmlFor="github">
              GitHub
              <span className="optional">
                Optional
              </span>
            </label>

            <input
              id="github"
              type="url"
              placeholder="https://github.com/username"
              value={github}
              onChange={(event) =>
                setGithub(event.target.value)
              }
              disabled={loading}
            />

          </div>

        </section>


        <section className="setup-section setup-section-last">

          <div className="setup-section-heading">
            <span>04</span>

            <div>
              <h2>Preferences</h2>
              <p>Optional instructions for the interviewer.</p>
            </div>
          </div>

          <div className="form-group">

            <label htmlFor="instructions">
              Instructions
              <span className="optional">
                Optional
              </span>
            </label>

            <textarea
              id="instructions"
              placeholder="e.g. Focus more on SQL and machine learning."
              value={instructions}
              onChange={(event) =>
                setInstructions(event.target.value)
              }
              rows={4}
              disabled={loading}
            />

          </div>

        </section>


        {error && (
          <div className="setup-error">

            <strong>
              Unable to start interview
            </strong>

            <span>
              {error}
            </span>

          </div>
        )}


        <div className="setup-submit">

          <div>
            <strong>
              {loading
                ? "Preparing interview..."
                : "Ready to begin?"}
            </strong>

            {!loading && (
              <span>
                Your questions will adapt to your answers.
              </span>
            )}

          </div>

          <button
            type="submit"
            className="primary-button"
            disabled={loading}
          >
            {loading
              ? "Preparing..."
              : "Start interview →"}
          </button>

        </div>

      </form>

    </div>
  );
}

export default InterviewSetup;