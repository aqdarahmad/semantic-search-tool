import {
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Layout from "./components/Layout";

import Jobs from "./pages/Jobs";
import JobDetails from "./pages/JobDetails";
import Resume from "./pages/Resume";

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
          path="/resume"
          element={<Resume />}
        />

      </Route>

    </Routes>
  );
}

export default App;