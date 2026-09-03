function Header() {
  return (
    <header className="top-header">
      <div className="header-left">
        <span className="header-status-dot"></span>
        <span>Interview workspace</span>
      </div>

      <div className="header-right">
        <button
          className="header-help"
          type="button"
          onClick={() => {
            alert("Help center will be added later.");
          }}
        >
          Help
        </button>

        <div className="header-profile">
          <div className="header-avatar">
            C
          </div>

          <span>Candidate</span>
        </div>
      </div>
    </header>
  );
}

export default Header;