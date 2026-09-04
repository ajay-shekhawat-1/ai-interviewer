function Header() {
  return (
    <header className="header">
      <div className="header-left">
        <h2 className="header-title">
          Interview Workspace
        </h2>

        <p className="header-subtitle">
          Prepare, practice, and improve your interview performance.
        </p>
      </div>

      <div className="header-right">
        <div className="header-status">
          <span className="header-status-dot"></span>
          <span>Workspace ready</span>
        </div>
      </div>
    </header>
  );
}

export default Header;