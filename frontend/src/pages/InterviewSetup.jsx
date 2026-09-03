import { useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

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

      // ==================================================
      // STEP 1: Upload resume + job description
      // ==================================================

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

      console.log(
        "Uploading resume with job description..."
      );

      const resumeResponse = await fetch(
        `${API_BASE_URL}/api/candidate-profile/upload-resume`,
        {
          method: "POST",
          body: resumeFormData,
        }
      );

      const resumeData =
        await resumeResponse.json();

      console.log(
        "Resume response:",
        resumeData
      );

      if (!resumeResponse.ok) {
        throw new Error(
          resumeData.detail ||
            "Failed to upload resume."
        );
      }

      const candidateId =
        resumeData.candidate_id;

      if (!candidateId) {
        throw new Error(
          "Resume uploaded, but candidate ID was not returned."
        );
      }

      console.log(
        "Candidate ID:",
        candidateId
      );

      // ==================================================
      // STEP 2: Create Job Description
      // ==================================================

      const jdResponse = await fetch(
        `${API_BASE_URL}/api/jd/create`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title:
              role.trim() ||
              "Job Position",

            raw_text:
              jobDescription,
          }),
        }
      );

      const jdData =
        await jdResponse.json();

      console.log(
        "Job description response:",
        jdData
      );

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

      console.log(
        "Job Description ID:",
        jobDescriptionId
      );

      // ==================================================
      // STEP 3: Start interview
      // ==================================================

      const interviewResponse =
        await fetch(
          `${API_BASE_URL}/api/interview/start`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              candidate_id:
                candidateId,

              job_description_id:
                jobDescriptionId,
            }),
          }
        );

      const interviewData =
        await interviewResponse.json();

      console.log(
        "Interview start response:",
        interviewData
      );

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

      console.log(
        "Interview Session ID:",
        sessionId
      );

      // ==================================================
      // STEP 4: Send data to App.jsx
      // ==================================================

      onStartInterview({
        candidateId,
        jobDescriptionId,
        sessionId,

        role,
        jobDescription,

        github,
        instructions,

        interview:
          interviewData,
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
      <div className="setup-container">

        <button
          className="back-button"
          type="button"
          onClick={onBack}
          disabled={loading}
        >
          ← Back to overview
        </button>

        <div className="setup-heading">
          <p className="eyebrow">
            NEW INTERVIEW
          </p>

          <h1>
            Set up your interview.
          </h1>

          <p>
            Give the interviewer some context so the
            questions can be tailored to you.
          </p>
        </div>

        <form
          className="setup-form"
          onSubmit={handleSubmit}
        >

          {/* ROLE */}

          <div className="form-section">

            <div className="form-section-title">
              Role
            </div>

            <div className="form-group">

              <label htmlFor="role">
                Target role
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

          </div>

          {/* JOB DESCRIPTION */}

          <div className="form-section">

            <div className="form-section-title">
              Job details
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
                  setJobDescription(
                    event.target.value
                  )
                }
                rows={8}
                disabled={loading}
                required
              ></textarea>

              <span className="field-hint">
                The job description helps determine which
                skills and topics should be tested.
              </span>

            </div>

          </div>

          {/* RESUME */}

          <div className="form-section">

            <div className="form-section-title">
              Your background
            </div>

            <div className="form-group">

              <label>
                Resume
              </label>

              <label
                className={`resume-upload ${
                  loading
                    ? "upload-disabled"
                    : ""
                }`}
              >

                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(event) =>
                    setResume(
                      event.target.files?.[0] ||
                        null
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
                      : "Upload your resume"}
                  </strong>

                  <span>
                    PDF or DOCX
                  </span>

                </div>

                <span className="upload-action">
                  Browse
                </span>

              </label>

            </div>

            {/* GITHUB */}

            <div className="form-group">

              <label htmlFor="github">
                GitHub profile
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

          </div>

          {/* EXTRA INSTRUCTIONS */}

          <div className="form-section">

            <div className="form-section-title">
              Interview preferences
            </div>

            <div className="form-group">

              <label htmlFor="instructions">
                Additional instructions
                <span className="optional">
                  Optional
                </span>
              </label>

              <textarea
                id="instructions"
                placeholder="For example: focus more on machine learning and SQL."
                value={instructions}
                onChange={(event) =>
                  setInstructions(
                    event.target.value
                  )
                }
                rows={4}
                disabled={loading}
              ></textarea>

            </div>

          </div>

          {/* ERROR */}

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

          {/* SUBMIT */}

          <div className="setup-submit">

            <div>

              <strong>
                {loading
                  ? "Preparing your interview..."
                  : "Ready when you are."}
              </strong>

              <span>
                {loading
                  ? "Analyzing your resume and generating questions."
                  : "The interview will adapt to your answers."}
              </span>

            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >

              {loading
                ? "Preparing..."
                : "Start interview"}

              {!loading && (
                <span>→</span>
              )}

            </button>

          </div>

        </form>

      </div>
    </div>
  );
}

export default InterviewSetup;