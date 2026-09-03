import Header from "./Header";
import Sidebar from "./Sidebar";

function AppShell({ children, currentPage, onNavigate }) {
  return (
    <div className="app-shell">
      <Sidebar
        currentPage={currentPage}
        onNavigate={onNavigate}
      />

      <div className="app-main">
        <Header />

        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppShell;