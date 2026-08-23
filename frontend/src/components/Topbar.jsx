import { NavLink } from "react-router-dom";

function Topbar() {
  return (
    <header className="topbar">

      <NavLink to="/jobs" className="topbar-brand">
        <div className="brand-icon">J</div>
        <span>JOBMATCH</span>
      </NavLink>

      <nav className="topbar-nav">

        <NavLink
          to="/jobs"
          className={({ isActive }) =>
            `topbar-link ${isActive ? "active" : ""}`
          }
        >
          Jobs
        </NavLink>

        <NavLink
          to="/resume"
          className={({ isActive }) =>
            `topbar-link ${isActive ? "active" : ""}`
          }
        >
          Resume
        </NavLink>

      </nav>

      <div className="topbar-status">
        <span></span>
        AI Matching
      </div>

    </header>
  );
}

export default Topbar;