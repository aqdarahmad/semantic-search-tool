import {
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Layout from "./components/Layout";

import Jobs from "./pages/Jobs";
import JobDetails from "./pages/JobDetails";
import Resume from "./pages/Resume";

// First visit: go straight to the upload page.
// After a resume was analyzed: show the saved matches.
function HomeRedirect() {
  let hasResults;

  try {
    hasResults = Boolean(
      localStorage.getItem("resumeMatchResults")
    );
  } catch {
    hasResults = false;
  }

  return (
    <Navigate
      to={hasResults ? "/jobs" : "/resume"}
      replace
    />
  );
}

function App() {
  return (
    <Routes>

      <Route element={<Layout />}>

        <Route
          path="/"
          element={<HomeRedirect />}
        />

        <Route
          path="/jobs"
          element={<Jobs />}
        />

        <Route
          path="/jobs/:jobId"
          element={<JobDetails />}
        />

        <Route
          path="/resume"
          element={<Resume />}
        />

      </Route>

    </Routes>
  );
}

export default App;