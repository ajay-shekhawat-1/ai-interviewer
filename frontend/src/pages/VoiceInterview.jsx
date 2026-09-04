import { useEffect, useRef, useState } from "react";
import "./VoiceInterview.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function VoiceInterview({ interviewData, onFinish }) {

  /*
   * --------------------------------------------------
   * Interview session state
   * --------------------------------------------------
   */

  const initialSession =
    interviewData?.interview?.session || null;

  const [session, setSession] =
    useState(initialSession);

  const [currentQuestion, setCurrentQuestion] =
    useState(null);

  const [questionNumber, setQuestionNumber] =
    useState(1);


  /*
   * --------------------------------------------------
   * Voice state
   * --------------------------------------------------
   */

  const [isSpeaking, setIsSpeaking] =
    useState(false);

  const [isListening, setIsListening] =
    useState(false);

  const [isTranscribing, setIsTranscribing] =
    useState(false);

  const [isProcessing, setIsProcessing] =
    useState(false);


  /*
   * --------------------------------------------------
   * Answer state
   * --------------------------------------------------
   */

  const [transcript, setTranscript] =
    useState("");

  const [evaluation, setEvaluation] =
    useState(null);

  const [decision, setDecision] =
    useState(null);


  /*
   * --------------------------------------------------
   * Final report state
   * --------------------------------------------------
   */

  const [report, setReport] =
    useState(null);

  const [isLoadingReport, setIsLoadingReport] =
    useState(false);


  /*
   * --------------------------------------------------
   * Error state
   * --------------------------------------------------
   */

  const [error, setError] =
    useState("");


  /*
   * --------------------------------------------------
   * Recording refs
   * --------------------------------------------------
   */

  const mediaRecorderRef =
    useRef(null);

  const audioChunksRef =
    useRef([]);

  const microphoneStreamRef =
    useRef(null);


  /*
   * --------------------------------------------------
   * Calculate total questions
   * --------------------------------------------------
   */

  const totalQuestions =
    session?.questions?.length || 0;


  /*
   * --------------------------------------------------
   * Load current question
   * --------------------------------------------------
   */

  useEffect(() => {

    if (!session) {
      setError(
        "Interview session could not be loaded."
      );

      return;
    }

    const index =
      session.current_question_index ?? 0;

    const question =
      session.questions?.[index];

    if (!question) {

      if (
        session.status === "completed"
      ) {
        return;
      }

      setError(
        "No interview question is currently available."
      );

      return;
    }

    setCurrentQuestion(question);

    setQuestionNumber(
      index + 1
    );

  }, [session]);


  /*
   * --------------------------------------------------
   * Speak current question
   * --------------------------------------------------
   */

  useEffect(() => {

    if (!currentQuestion?.question) {
      return;
    }

    const timer =
      setTimeout(() => {

        speakQuestion(
          currentQuestion.question
        );

      }, 300);

    return () => {

      clearTimeout(timer);

      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }

    };

  }, [currentQuestion]);


  /*
   * --------------------------------------------------
   * Browser Text-to-Speech
   * --------------------------------------------------
   */

  const speakQuestion = (text) => {

    if (!window.speechSynthesis) {

      console.warn(
        "Browser SpeechSynthesis is not supported."
      );

      return;
    }

    window.speechSynthesis.cancel();

    const utterance =
      new SpeechSynthesisUtterance(text);

    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = () => {
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(
      utterance
    );
  };


  /*
   * --------------------------------------------------
   * Start recording
   * --------------------------------------------------
   */

  const startRecording = async () => {

    try {

      setError("");
      setTranscript("");
      setEvaluation(null);
      setDecision(null);


      /*
       * Stop question speech.
       */

      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }

      setIsSpeaking(false);


      /*
       * Request microphone.
       */

      const stream =
        await navigator.mediaDevices.getUserMedia(
          {
            audio: true,
          }
        );

      microphoneStreamRef.current =
        stream;


      /*
       * Create recorder.
       */

      const recorder =
        new MediaRecorder(stream);

      mediaRecorderRef.current =
        recorder;

      audioChunksRef.current = [];


      /*
       * Collect audio chunks.
       */

      recorder.ondataavailable = (
        event
      ) => {

        if (event.data.size > 0) {

          audioChunksRef.current.push(
            event.data
          );

        }

      };


      /*
       * Recording started.
       */

      recorder.onstart = () => {

        console.log(
          "Microphone recording started."
        );

        setIsListening(true);

      };


      /*
       * Recording stopped.
       */

      recorder.onstop = async () => {

        console.log(
          "Stopping microphone recording..."
        );

        setIsListening(false);


        /*
         * Stop microphone tracks.
         */

        if (
          microphoneStreamRef.current
        ) {

          microphoneStreamRef.current
            .getTracks()
            .forEach((track) => {
              track.stop();
            });

          microphoneStreamRef.current =
            null;

        }


        /*
         * Build audio Blob.
         */

        const audioBlob =
          new Blob(
            audioChunksRef.current,
            {
              type: "audio/webm",
            }
          );


        console.log(
          "Recording completed."
        );

        console.log(
          "Audio Blob:",
          audioBlob
        );

        console.log(
          "Audio size:",
          audioBlob.size,
          "bytes"
        );

        console.log(
          "Audio type:",
          audioBlob.type
        );


        if (!audioBlob.size) {

          setError(
            "No audio was recorded."
          );

          return;
        }


        /*
         * Send audio to Whisper.
         */

        await transcribeAudio(
          audioBlob
        );

      };


      /*
       * Recorder error.
       */

      recorder.onerror = (event) => {

        console.error(
          "MediaRecorder error:",
          event
        );

        setIsListening(false);

        setError(
          "Microphone recording failed."
        );

      };


      /*
       * Start recording.
       */

      recorder.start();

    } catch (err) {

      console.error(
        "Microphone error:",
        err
      );

      setIsListening(false);

      if (
        err.name ===
        "NotAllowedError"
      ) {

        setError(
          "Microphone permission was denied. Please allow microphone access."
        );

      } else {

        setError(
          err.message ||
          "Unable to access microphone."
        );

      }

    }

  };


  /*
   * --------------------------------------------------
   * Stop recording
   * --------------------------------------------------
   */

  const stopRecording = () => {

    const recorder =
      mediaRecorderRef.current;

    if (!recorder) {
      return;
    }

    if (
      recorder.state ===
      "recording"
    ) {

      console.log(
        "Stopping microphone recording..."
      );

      recorder.stop();

    }

  };


  /*
   * --------------------------------------------------
   * Whisper transcription
   * --------------------------------------------------
   */

  const transcribeAudio =
    async (audioBlob) => {

      try {

        setIsTranscribing(true);
        setError("");


        const formData =
          new FormData();

        formData.append(
          "file",
          audioBlob,
          "answer.webm"
        );


        console.log(
          "Sending recorded audio to Whisper..."
        );


        const response =
          await fetch(
            `${API_BASE_URL}/api/voice/transcribe`,
            {
              method: "POST",
              body: formData,
            }
          );


        const data =
          await response.json();


        console.log(
          "Whisper response:",
          data
        );


        if (!response.ok) {

          throw new Error(
            typeof data.detail ===
              "string"
              ? data.detail
              : "Audio transcription failed."
          );

        }


        /*
         * Whisper may return an empty transcript.
         */

        const transcriptText =
          typeof data.text === "string"
            ? data.text.trim()
            : "";


        setTranscript(
          transcriptText ||
          "[No answer provided]"
        );


        console.log(
          "Transcript:",
          transcriptText ||
          "[No answer provided]"
        );


        /*
         * Send transcript to interview engine.
         */

        await processAnswer(
          transcriptText
        );

      } catch (err) {

        console.error(
          "Transcription error:",
          err
        );

        setError(
          err.message ||
          "Unable to transcribe audio."
        );

      } finally {

        setIsTranscribing(false);

      }

    };


  /*
   * --------------------------------------------------
   * Fetch Final Report
   * --------------------------------------------------
   */

  const fetchFinalReport =
    async (sessionId) => {

      try {

        setIsLoadingReport(true);
        setError("");


        console.log(
          "Fetching final interview report..."
        );


        const response =
          await fetch(
            `${API_BASE_URL}/api/evaluation/report/${sessionId}`
          );


        const data =
          await response.json();


        console.log(
          "Final report response:",
          data
        );


        if (!response.ok) {

          throw new Error(
            typeof data.detail === "string"
              ? data.detail
              : "Unable to generate interview report."
          );

        }


        /*
         * Store report locally.
         */

        setReport(data);


        /*
         * IMPORTANT:
         *
         * Send the report to App.jsx.
         *
         * App.jsx will then switch
         * from the interview page
         * to the final report page.
         */

        onFinish(data);

      } catch (err) {

        console.error(
          "Final report error:",
          err
        );

        setError(
          err.message ||
          "Unable to generate final report."
        );

      } finally {

        setIsLoadingReport(false);

      }

    };


  /*
   * --------------------------------------------------
   * Process candidate answer
   * --------------------------------------------------
   */

  const processAnswer =
    async (answerText) => {

      try {

        const sessionId =
          session?.session_id ||
          interviewData?.sessionId;


        if (!sessionId) {

          throw new Error(
            "Interview session ID is missing."
          );

        }


        setIsProcessing(true);
        setError("");


        console.log(
          "Sending transcript to interview engine..."
        );

        console.log(
          "Session ID:",
          sessionId
        );

        console.log(
          "Answer:",
          answerText ||
          "[No answer provided]"
        );


        /*
         * Send answer to backend.
         */

        const response =
          await fetch(
            `${API_BASE_URL}/api/session/${sessionId}/process-answer`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body: JSON.stringify({
                answer:
                  answerText || "",
              }),
            }
          );


        const data =
          await response.json();


        console.log(
          "Interview processing response:",
          data
        );


        /*
         * Backend error.
         */

        if (!response.ok) {

          const message =
            typeof data.detail ===
              "string"
              ? data.detail
              : "Unable to process your answer.";

          throw new Error(message);

        }


        /*
         * Save updated session.
         */

        if (data.session) {

          setSession(
            data.session
          );

        }


        /*
         * Save evaluation.
         */

        setEvaluation(
          data.evaluation ||
          null
        );


        /*
         * Save adaptive decision.
         */

        setDecision(
          data.decision ||
          null
        );


        /*
         * --------------------------------------------------
         * INTERVIEW COMPLETED
         * --------------------------------------------------
         */

        if (
          data.session?.status ===
            "completed" ||
          !data.next_question
        ) {

          console.log(
            "Interview completed."
          );

          console.log(
            "Fetching final report..."
          );


          await fetchFinalReport(
            sessionId
          );


          return;
        }


        /*
         * --------------------------------------------------
         * MOVE TO NEXT QUESTION
         * --------------------------------------------------
         */

        if (data.next_question) {

          console.log(
            "Moving to next question:",
            data.next_question
          );


          setCurrentQuestion(
            data.next_question
          );


          if (
            typeof data.session
              ?.current_question_index ===
            "number"
          ) {

            setQuestionNumber(
              data.session
                .current_question_index +
              1
            );

          }

        }

      } catch (err) {

        console.error(
          "Answer processing error:",
          err
        );

        setError(
          err.message ||
          "Unable to process your answer."
        );

      } finally {

        setIsProcessing(false);

      }

    };


  /*
   * --------------------------------------------------
   * Manual finish
   * --------------------------------------------------
   *
   * This is still available as a safety option.
   *
   * Normally the final report is opened
   * automatically after the last answer.
   */

  const handleFinish = async () => {
  if (
    isListening ||
    isTranscribing ||
    isProcessing ||
    isLoadingReport
  ) {
    return;
  }

  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  setIsSpeaking(false);

  const sessionId =
    session?.session_id ||
    interviewData?.sessionId;

  if (!sessionId) {
    setError("Interview session ID is missing.");
    return;
  }

  try {
    setIsLoadingReport(true);
    setError("");

    console.log(
      "Finishing interview:",
      sessionId
    );

    // ---------------------------------------------
    // 1. Mark interview as completed
    // ---------------------------------------------

    const finishResponse = await fetch(
      `${API_BASE_URL}/api/session/${sessionId}/finish`,
      {
        method: "POST",
      }
    );

    if (!finishResponse.ok) {
      const errorData =
        await finishResponse.json().catch(
          () => ({})
        );

      throw new Error(
        errorData.detail ||
          "Unable to finish the interview."
      );
    }

    const finishedSession =
      await finishResponse.json();

    console.log(
      "Interview marked as completed:",
      finishedSession
    );

    // ---------------------------------------------
    // 2. Generate final report
    // ---------------------------------------------

    await fetchFinalReport(sessionId);

  } catch (error) {

    console.error(
      "Finish interview error:",
      error
    );

    setError(
      error.message ||
        "Unable to finish the interview."
    );

  } finally {

    setIsLoadingReport(false);
  }
};
  /*
   * --------------------------------------------------
   * Cleanup
   * --------------------------------------------------
   */

  useEffect(() => {

    return () => {

      if (window.speechSynthesis) {

        window.speechSynthesis.cancel();

      }


      if (
        microphoneStreamRef.current
      ) {

        microphoneStreamRef.current
          .getTracks()
          .forEach((track) => {
            track.stop();
          });

      }

    };

  }, []);


  /*
   * --------------------------------------------------
   * Progress
   * --------------------------------------------------
   */

  const progress =
    totalQuestions > 0
      ? Math.min(
          (questionNumber /
            totalQuestions) *
            100,
          100
        )
      : 0;


  /*
   * --------------------------------------------------
   * Evaluation helper
   * --------------------------------------------------
   */

  const getScore = (field) => {

    const value =
      evaluation?.[field];


    if (
      value === undefined ||
      value === null
    ) {

      return "—";

    }


    return `${value}/10`;

  };


  /*
   * --------------------------------------------------
   * UI
   * --------------------------------------------------
   */

  return (

    <div className="voice-interview">

      {/* ==========================================
          HEADER
          ========================================== */}

      <header className="voice-interview__header">

        <div className="voice-interview__brand">

          <div className="voice-interview__brand-mark">
            AI
          </div>

          <div>

            <p className="voice-interview__eyebrow">
              LIVE INTERVIEW
            </p>

            <h1>
              {interviewData?.role ||
                "AI Interview"}
            </h1>

          </div>

        </div>


        <div className="voice-interview__counter">

          <span>
            QUESTION
          </span>

          <strong>
            {questionNumber}

            {totalQuestions > 0
              ? ` / ${totalQuestions}`
              : ""}
          </strong>

        </div>

      </header>


      {/* ==========================================
          PROGRESS
          ========================================== */}

      <div className="voice-interview__progress-wrapper">

        <div className="voice-interview__progress-track">

          <div
            className="voice-interview__progress-bar"
            style={{
              width: `${progress}%`,
            }}
          />

        </div>

      </div>


      {/* ==========================================
          MAIN CONTENT
          ========================================== */}

      <main className="voice-interview__content">

        {report ? (

          /*
           * Normally this section will only appear
           * briefly because onFinish(data) sends the
           * report to App.jsx immediately.
           */

          <section className="interview-card report-card">

            <div className="card-heading">

              <span className="section-label">
                INTERVIEW COMPLETED
              </span>

              <span className="card-heading__status">
                FINAL REPORT
              </span>

            </div>


            <h2 className="report-card__title">
              Interview completed successfully.
            </h2>


            <div
              className="overall-score large-score"
            >

              <strong>
                {report.overall_score ??
                  report.score ??
                  "—"}
              </strong>

              <span>
                / 10
              </span>

            </div>


            <p>
              Preparing your final report...
            </p>

          </section>

        ) : isLoadingReport ? (

          <section
            className="interview-card loading-card"
            style={{
              textAlign: "center",
              padding: "40px",
            }}
          >

            <span
              className="spinner"
              style={{
                display: "inline-block",
                width: "32px",
                height: "32px",
                marginBottom: "16px",
              }}
            />

            <h3>
              Generating your final interview report...
            </h3>

            <p>
              Please wait while our AI compiles
              your evaluation metrics.
            </p>

          </section>

        ) : (

          <>

            {/* ------------------------------------------
                QUESTION
                ------------------------------------------ */}

            <section className="interview-card question-card">

              <div className="question-card__header">

                <div>

                  <span className="section-label">
                    AI INTERVIEWER
                  </span>

                  {currentQuestion?.section && (
                    <span className="question-card__section">
                      {currentQuestion.section}
                    </span>
                  )}

                </div>


                {currentQuestion?.difficulty && (
                  <span className="difficulty-badge">
                    {currentQuestion.difficulty}
                  </span>
                )}

              </div>


              {currentQuestion?.question_type ===
                "follow_up" && (

                <div className="follow-up-label">
                  FOLLOW-UP QUESTION
                </div>

              )}


              <h2 className="question-card__question">

                {currentQuestion?.question ||
                  "Loading interview question..."}

              </h2>


              <div className="question-card__voice-status">

                <span
                  className={
                    isSpeaking
                      ? "voice-indicator voice-indicator--active"
                      : "voice-indicator"
                  }
                >

                  {isSpeaking
                    ? "🔊"
                    : "◉"}

                </span>


                <span>

                  {isSpeaking
                    ? "AI is speaking"
                    : "Listen to the question, then answer when ready"}

                </span>

              </div>

            </section>


            {/* ------------------------------------------
                ADAPTIVE INFO
                ------------------------------------------ */}

            {decision?.focus_topic && (

              <div className="adaptive-notice">

                <span className="adaptive-notice__icon">
                  ✦
                </span>


                <div>

                  <strong>
                    Interview adapted
                  </strong>


                  <p>

                    The next question is focusing on{" "}

                    <strong>
                      {decision.focus_topic}
                    </strong>

                    .

                  </p>

                </div>

              </div>

            )}


            {/* ------------------------------------------
                VOICE CONTROL
                ------------------------------------------ */}

            <section className="voice-control">

              <div className="voice-control__status">

                {isListening && (
                  <>
                    <span className="recording-dot" />

                    Listening to your answer
                  </>
                )}


                {isTranscribing && (
                  <>
                    <span className="spinner" />

                    Converting your answer to text
                  </>
                )}


                {isProcessing && (
                  <>
                    <span className="spinner" />

                    Evaluating your answer
                  </>
                )}


                {!isListening &&
                  !isTranscribing &&
                  !isProcessing &&
                  !isSpeaking && (
                    <>
                      <span className="ready-dot" />

                      Ready for your answer
                    </>
                  )}


                {isSpeaking && (
                  <>
                    <span className="speaker-dot" />

                    AI is speaking
                  </>
                )}

              </div>


              {!isListening ? (

                <button
                  type="button"
                  className="record-button"
                  onClick={
                    startRecording
                  }
                  disabled={
                    isSpeaking ||
                    isTranscribing ||
                    isProcessing ||
                    !currentQuestion
                  }
                >

                  <span className="record-button__icon">
                    🎤
                  </span>

                  <span>
                    Start Answer
                  </span>

                </button>

              ) : (

                <button
                  type="button"
                  className="record-button record-button--stop"
                  onClick={
                    stopRecording
                  }
                >

                  <span className="record-button__icon">
                    ■
                  </span>

                  <span>
                    Stop Answer
                  </span>

                </button>

              )}

            </section>


            {/* ------------------------------------------
                TRANSCRIPT
                ------------------------------------------ */}

            {transcript && (

              <section className="interview-card transcript-card">

                <div className="card-heading">

                  <span className="section-label">
                    YOUR ANSWER
                  </span>

                  <span className="card-heading__status">
                    TRANSCRIBED
                  </span>

                </div>


                <p className="transcript-card__text">
                  {transcript}
                </p>

              </section>

            )}


            {/* ------------------------------------------
                EVALUATION
                ------------------------------------------ */}

            {evaluation && (

              <section className="interview-card evaluation-card">

                <div className="evaluation-card__header">

                  <div>

                    <span className="section-label">
                      ANSWER EVALUATION
                    </span>

                    <h3>
                      How your answer performed
                    </h3>

                  </div>


                  <div className="overall-score">

                    <strong>
                      {evaluation.overall_score ??
                        "—"}
                    </strong>

                    <span>
                      / 10
                    </span>

                  </div>

                </div>


                {/* Score grid */}

                <div className="score-grid">

                  <div className="score-item">

                    <span>
                      Technical
                    </span>

                    <strong>
                      {getScore(
                        "technical_score"
                      )}
                    </strong>

                  </div>


                  <div className="score-item">

                    <span>
                      Relevance
                    </span>

                    <strong>
                      {getScore(
                        "relevance_score"
                      )}
                    </strong>

                  </div>


                  <div className="score-item">

                    <span>
                      Completeness
                    </span>

                    <strong>
                      {getScore(
                        "completeness_score"
                      )}
                    </strong>

                  </div>


                  <div className="score-item">

                    <span>
                      Communication
                    </span>

                    <strong>
                      {getScore(
                        "communication_score"
                      )}
                    </strong>

                  </div>

                </div>


                {/* Feedback */}

                {evaluation.feedback && (

                  <div className="evaluation-section">

                    <h4>
                      Feedback
                    </h4>

                    <p>
                      {evaluation.feedback}
                    </p>

                  </div>

                )}


                {/* Strengths */}

                {evaluation.strengths?.length >
                  0 && (

                  <div className="evaluation-section">

                    <h4>
                      Strengths
                    </h4>


                    <ul className="evaluation-list evaluation-list--positive">

                      {evaluation.strengths.map(
                        (item, index) => (

                          <li key={index}>
                            {item}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}


                {/* Weaknesses */}

                {evaluation.weaknesses?.length >
                  0 && (

                  <div className="evaluation-section">

                    <h4>
                      Areas to improve
                    </h4>


                    <ul className="evaluation-list">

                      {evaluation.weaknesses.map(
                        (item, index) => (

                          <li key={index}>
                            {item}
                          </li>

                        )
                      )}

                    </ul>

                  </div>

                )}

              </section>

            )}

          </>

        )}


        {/* ------------------------------------------
            ERROR
            ------------------------------------------ */}

        {error && (

          <div className="interview-error">

            <strong>
              Something went wrong
            </strong>

            <span>
              {error}
            </span>

          </div>

        )}


        {/* ------------------------------------------
            MANUAL FINISH
            ------------------------------------------ */}

        {!report &&
          !isLoadingReport && (

          <div className="finish-section">

            <button
              type="button"
              className="finish-button"
              onClick={
                handleFinish
              }
              disabled={
                isListening ||
                isTranscribing ||
                isProcessing
              }
            >
              Finish Interview
            </button>

          </div>

        )}

      </main>

    </div>

  );
}

export default VoiceInterview;