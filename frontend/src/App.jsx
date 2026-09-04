import { useState } from "react";

import AppShell from "./components/AppShell";
import InterviewReport from "./components/InterviewReport";

import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import InterviewResult from "./pages/InterviewResult";
import InterviewSetup from "./pages/InterviewSetup";
import Performance from "./pages/Performance";
import VoiceInterview from "./pages/VoiceInterview";

function App() {
  const [page, setPage] = useState("dashboard");

  const [interviewData, setInterviewData] = useState({
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

  // =========================================================
  // START NEW INTERVIEW
  // =========================================================

  const startInterview = (data) => {
    console.log("Interview started:", data);

    setInterviewData(data);
    setFinalReport(null);
    setPage("interview");
  };

  // =========================================================
  // FINISH CURRENT INTERVIEW
  // =========================================================

  const finishInterview = (report) => {
    console.log("Final interview report:", report);

    setFinalReport(report);
    setPage("report");
  };

  // =========================================================
  // OPEN SAVED INTERVIEW REPORT
  // =========================================================

  const openInterviewReport = (sessionId, report) => {
    console.log(
      "Opening saved interview report:",
      sessionId,
      report
    );

    if (!report) {
      window.alert(
        "Unable to load interview report."
      );
      return;
    }

    setFinalReport(report);

    setInterviewData((previous) => ({
      ...previous,
      sessionId,
    }));

    setPage("report");
  };

  // =========================================================
  // RESTART / NEW INTERVIEW
  // =========================================================

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

  // =========================================================
  // PAGE ROUTING
  // =========================================================

  const renderPage = () => {
    switch (page) {

      // -----------------------------------------------------
      // DASHBOARD
      // -----------------------------------------------------

      case "dashboard":
        return (
          <Dashboard
            onNewInterview={() =>
              navigate("setup")
            }
            onViewHistory={() =>
              navigate("history")
            }
          />
        );


      // -----------------------------------------------------
      // INTERVIEW SETUP
      // -----------------------------------------------------

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


      // -----------------------------------------------------
      // HISTORY
      // -----------------------------------------------------

      case "history":
        return (
          <History
            onBack={() =>
              navigate("dashboard")
            }
            onNewInterview={() =>
              navigate("setup")
            }
            onViewReport={
              openInterviewReport
            }
          />
        );


      // -----------------------------------------------------
      // PERFORMANCE
      // -----------------------------------------------------

      case "performance":
        return (
          <Performance
            onBack={() =>
              navigate("dashboard")
            }
            onNewInterview={() =>
              navigate("setup")
            }
          />
        );


      // -----------------------------------------------------
      // VOICE INTERVIEW
      // -----------------------------------------------------

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


      // -----------------------------------------------------
      // INTERVIEW RESULT
      // -----------------------------------------------------

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


      // -----------------------------------------------------
      // FINAL REPORT
      // -----------------------------------------------------

      case "report":
        return (
          <InterviewReport
            report={finalReport}
            onRestart={
              restartInterview
            }
          />
        );


      // -----------------------------------------------------
      // DEFAULT
      // -----------------------------------------------------

      default:
        return (
          <Dashboard
            onNewInterview={() =>
              navigate("setup")
            }
            onViewHistory={() =>
              navigate("history")
            }
          />
        );
    }
  };


  // =========================================================
  // INTERVIEW SCREEN
  // =========================================================
  // Keep the interview screen distraction-free.
  // =========================================================

  if (page === "interview") {
    return renderPage();
  }


  // =========================================================
  // NORMAL APP SHELL
  // =========================================================

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