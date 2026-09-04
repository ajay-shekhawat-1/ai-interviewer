import { useState } from "react";

function Sidebar({ currentPage, onNavigate }) {
  const [collapsed, setCollapsed] = useState(false);

  const navigation = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: "⌂",
    },
    {
      id: "setup",
      label: "New Interview",
      icon: "＋",
    },
    {
      id: "history",
      label: "History",
      icon: "◷",
    },
    {
      id: "performance",
      label: "Performance",
      icon: "↗",
    },
  ];

  const handleNavigation = (page) => {
    if (typeof onNavigate === "function") {
      onNavigate(page);
    }
  };

  return (
    <aside
      className={`sidebar ${
        collapsed ? "sidebar-collapsed" : ""
      }`}
    >
      {/* ================================
          SIDEBAR HEADER
      ================================= */}

      <div className="sidebar-top">
        <div className="sidebar-brand">
          {!collapsed ? (
            <div className="sidebar-brand-content">
              <div className="brand-name">
                AI Interviewer
              </div>

              <div className="brand-subtitle">
                Interview practice
              </div>
            </div>
          ) : (
            <div className="brand-mark">
              AI
            </div>
          )}
        </div>

        <button
          className="sidebar-toggle"
          type="button"
          onClick={() =>
            setCollapsed((value) => !value)
          }
          aria-label={
            collapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
          title={
            collapsed
              ? "Expand sidebar"
              : "Collapse sidebar"
          }
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>

      {/* ================================
          NAVIGATION
      ================================= */}

      <nav
        className="sidebar-nav"
        aria-label="Main navigation"
      >
        {!collapsed && (
          <div className="nav-label">
            WORKSPACE
          </div>
        )}

        {navigation.map((item) => {
          const isActive =
            currentPage === item.id;

          return (
            <button
              key={item.id}
              type="button"
              className={`nav-item ${
                isActive
                  ? "nav-item-active"
                  : ""
              }`}
              onClick={() =>
                handleNavigation(item.id)
              }
              aria-current={
                isActive ? "page" : undefined
              }
              title={
                collapsed
                  ? item.label
                  : undefined
              }
            >
              <span
                className="nav-icon"
                aria-hidden="true"
              >
                {item.icon}
              </span>

              {!collapsed && (
                <span className="nav-item-label">
                  {item.label}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* ================================
          SIDEBAR FOOTER
      ================================= */}

      <div className="sidebar-bottom">
        {!collapsed && (
          <>
            <div className="sidebar-divider" />

            <div className="candidate-mini">
              <div className="candidate-avatar">
                C
              </div>

              <div className="candidate-info">
                <strong>Candidate</strong>

                <span>
                  Interview workspace
                </span>
              </div>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}

export default Sidebar;