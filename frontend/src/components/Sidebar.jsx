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
  ];

  return (
    <aside
      className={`sidebar ${
        collapsed ? "sidebar-collapsed" : ""
      }`}
    >
      <div className="sidebar-top">
        <div className="sidebar-brand">
          {!collapsed && (
            <div>
              <div className="brand-name">
                AI Interviewer
              </div>

              <div className="brand-subtitle">
                Interview practice
              </div>
            </div>
          )}

          {collapsed && (
            <div className="brand-mark">
              AI
            </div>
          )}
        </div>

        <button
          className="sidebar-toggle"
          onClick={() => setCollapsed(!collapsed)}
          type="button"
          aria-label="Toggle sidebar"
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-label">
          {!collapsed && "WORKSPACE"}
        </div>

        {navigation.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-item ${
              currentPage === item.id
                ? "nav-item-active"
                : ""
            }`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">
              {item.icon}
            </span>

            {!collapsed && (
              <span>{item.label}</span>
            )}
          </button>
        ))}

        <button
          type="button"
          className="nav-item"
          onClick={() =>
            alert(
              "Interview history will be connected next."
            )
          }
        >
          <span className="nav-icon">◷</span>

          {!collapsed && <span>History</span>}
        </button>

        <button
          type="button"
          className="nav-item"
          onClick={() =>
            alert(
              "Performance analytics will be connected later."
            )
          }
        >
          <span className="nav-icon">↗</span>

          {!collapsed && <span>Performance</span>}
        </button>
      </nav>

      {!collapsed && (
        <div className="sidebar-bottom">
          <button
            type="button"
            className="nav-item"
            onClick={() =>
              alert("Settings will be added later.")
            }
          >
            <span className="nav-icon">⚙</span>
            <span>Settings</span>
          </button>

          <div className="sidebar-divider"></div>

          <div className="candidate-mini">
            <div className="candidate-avatar">
              C
            </div>

            <div className="candidate-info">
              <strong>Candidate</strong>
              <span>Interview workspace</span>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;