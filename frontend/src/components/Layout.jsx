import { Outlet } from "react-router-dom";
import Topbar from "./Topbar";

function Layout() {
  return (
    <div className="app">

      <Topbar />

      <main className="main">
        <Outlet />
      </main>

    </div>
  );
}

export default Layout;