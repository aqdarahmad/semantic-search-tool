import {
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Layout from "./components/Layout";

import Jobs from "./pages/Jobs";
import JobDetails from "./pages/JobDetails";
import SavedJobs from "./pages/SavedJobs";
import AppliedJobs from "./pages/AppliedJobs";
import Resume from "./pages/Resume";
import Profile from "./pages/Profile";

function App() {

  return (
    <Routes>

      <Route element={<Layout />}>

        <Route
          path="/"
          element={
            <Navigate
              to="/jobs"
              replace
            />
          }
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
          path="/saved"
          element={<SavedJobs />}
        />

        <Route
          path="/applied"
          element={<AppliedJobs />}
        />

        <Route
          path="/resume"
          element={<Resume />}
        />

        <Route
          path="/profile"
          element={<Profile />}
        />

      </Route>

    </Routes>
  );
}

export default App;