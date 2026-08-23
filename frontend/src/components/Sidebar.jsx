import { NavLink } from "react-router-dom";

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="brand">

        <div className="brand-icon">
          ✦
        </div>

        <span>JOBMATCH</span>

      </div>


      <nav className="sidebar-nav">

        <NavLink
          to="/jobs"
          className="nav-item"
        >
          <span>▦</span>
          <small>Jobs</small>
        </NavLink>


        <NavLink
          to="/saved"
          className="nav-item"
        >
          <span>♡</span>
          <small>Saved</small>
        </NavLink>


        <NavLink
          to="/applied"
          className="nav-item"
        >
          <span>✓</span>
          <small>Applied</small>
        </NavLink>


        <NavLink
          to="/resume"
          className="nav-item"
        >
          <span>▤</span>
          <small>Resume</small>
        </NavLink>


        <NavLink
          to="/profile"
          className="nav-item"
        >
          <span>◯</span>
          <small>Profile</small>
        </NavLink>

      </nav>


      <div className="sidebar-bottom">

        <button>?</button>

        <button>↪</button>

      </div>

    </aside>
  );
}

export default Sidebar;