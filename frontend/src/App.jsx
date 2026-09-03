import { useState } from "react";

import AppShell from "./components/AppShell";
import InterviewReport from "./components/InterviewReport";
import Dashboard from "./pages/Dashboard";
import InterviewResult from "./pages/InterviewResult";
import InterviewSetup from "./pages/InterviewSetup";
import VoiceInterview from "./pages/VoiceInterview";

function App() {
  const [page, setPage] = useState("dashboard");

  const [interviewData, setInterviewData] =
    useState({
      candidateId: null,
      jobDescriptionId: null,
      sessionId: null,
      role: "",
      jobDescription: "",
      interview: null,
    });

  const [finalReport, setFinalReport] = useState(null);

  const navigate = (nextPage) => {
    setPage(nextPage);
  };

  const startInterview = (data) => {
    console.log(
      "Interview started:",
      data
    );

    setInterviewData(data);

    setFinalReport(null);

    setPage("interview");
  };

  /*
   * Receive the final report from VoiceInterview
   * and open the report page.
   */
  const finishInterview = (report) => {
    console.log(
      "Final interview report:",
      report
    );

    setFinalReport(report);

    setPage("report");
  };

  /*
   * Start a completely new interview.
   */
  const restartInterview = () => {
    setFinalReport(null);

    setInterviewData({
      candidateId: null,
      jobDescriptionId: null,
      sessionId: null,
      role: "",
      jobDescription: "",
      interview: null,
    });

    setPage("dashboard");
  };

  const renderPage = () => {
    switch (page) {

      /*
       * ------------------------------------------
       * DASHBOARD
       * ------------------------------------------
       */

      case "dashboard":
        return (
          <Dashboard
            onNewInterview={() =>
              navigate("setup")
            }
          />
        );


      /*
       * ------------------------------------------
       * INTERVIEW SETUP
       * ------------------------------------------
       */

      case "setup":
        return (
          <InterviewSetup
            onStartInterview={
              startInterview
            }
            onBack={() =>
              navigate("dashboard")
            }
          />
        );


      /*
       * ------------------------------------------
       * VOICE INTERVIEW
       * ------------------------------------------
       */

      case "interview":
        return (
          <VoiceInterview
            interviewData={
              interviewData
            }
            onFinish={
              finishInterview
            }
          />
        );


      /*
       * ------------------------------------------
       * OLD RESULT PAGE
       * ------------------------------------------
       *
       * Keep this for now.
       * We may remove it later if the new
       * InterviewReport completely replaces it.
       */

      case "result":
        return (
          <InterviewResult
            sessionId={
              interviewData.sessionId
            }
            onBackToDashboard={() =>
              navigate("dashboard")
            }
          />
        );


      /*
       * ------------------------------------------
       * FINAL INTERVIEW REPORT
       * ------------------------------------------
       */

      case "report":
        return (
          <InterviewReport
            report={finalReport}
            onRestart={
              restartInterview
            }
          />
        );


      /*
       * ------------------------------------------
       * DEFAULT
       * ------------------------------------------
       */

      default:
        return (
          <Dashboard
            onNewInterview={() =>
              navigate("setup")
            }
          />
        );
    }
  };


  /*
   * Voice interview should be distraction-free.
   * Therefore it does not use the dashboard sidebar.
   */

  if (page === "interview") {
    return renderPage();
  }


  return (
    <AppShell
      currentPage={page}
      onNavigate={navigate}
    >
      {renderPage()}
    </AppShell>
  );
}

export default App;