import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./Components/Dashboard";
import SearchResults from "./Components/SearchResults";
import ProjectDetail from "./Components/ProjectDetail";

function App() {
    return (
        <BrowserRouter>
            <Routes>

                {/* Default page */}
                <Route path="/" element={<Dashboard />} />

                {/* Search results page */}
                <Route
                    path="/search-results"
                    element={<SearchResults />}
                />
                <Route
                    path="/project-detail"
                    element={<ProjectDetail />}
                />

            </Routes>
        </BrowserRouter>
    );
}

export default App;