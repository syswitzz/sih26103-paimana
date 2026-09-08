import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import logo from "../Static/logo.png";
import "./SearchResults.css";
import { getProjects, getSectors, getErrorMessage } from "../services/api";

function SearchResults() {
    const navigate = useNavigate();
    const location = useLocation();

    const [projectData, setProjectData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sectors, setSectors] = useState([]);
    const [filterSector, setFilterSector] = useState(location.state?.sector || "");
    const [searchText, setSearchText] = useState(location.state?.projectName || "");

    // Fetch projects from API
    useEffect(() => {
        const fetchProjects = async () => {
            try {
                setLoading(true);
                setError(null);

                const params = {};
                if (searchText) params.q = searchText;
                if (filterSector) params.sector = filterSector;

                const data = await getProjects(params);
                // Handle both direct array and paginated response
                const projectList = Array.isArray(data) ? data : (data.items || []);
                setProjectData(projectList);
            } catch (err) {
                setError(getErrorMessage(err));
                setProjectData([]);
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, [searchText, filterSector]);

    useEffect(() => {
        getSectors().then(setSectors).catch(() => setSectors([]));
    }, []);

    // Helper to get risk level display name
    const getRiskLevelDisplay = (riskLevel) => {
        if (!riskLevel) return "Unknown";
        return riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1).toLowerCase();
    };

    // Format location from state field
    const getLocationDisplay = (project) => {
        return project.state || project.location || "Unknown";
    };

    const handleSearchKeyDown = (event) => {
        if (event.key === "Enter") event.currentTarget.blur();
    };

    return (
        <section className="searchresultssection">
            <header className="resultstopbar">
                <div className="resultstitle">
                    <Link to="/"><img src={logo} alt="PAIMANA Logo" /></Link>
                    <span>Project Search</span>
                </div>
                <button className="resultsuser" aria-label="Open user account" title="User account">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 8a7 7 0 0 0-14 0" />
                    </svg>
                </button>
            </header>

            <main className="resultsmain">
                <div className="resultscontent">

                    <div className="resultsheader">
                        <div>
                            <h1>Search Results</h1>
                            <br></br>
                            <p>View matching projects and their key details.</p>
                        </div>
                        <br></br>
                        <button
                            className="backhome"
                            onClick={() => navigate("/")}
                        >
                            ← Back to Home
                        </button>
                    </div>

                    {error && (
                        <div style={{
                            backgroundColor: "#fee2e2",
                            color: "#991b1b",
                            padding: "1rem",
                            margin: "1rem 0",
                            borderRadius: "0.5rem"
                        }}>
                            ⚠️ {error}
                        </div>
                    )}

                    {/* SEARCH FILTERS */}
                    <div className="resultsfilters">
                        <div className="resultfilter">
                            <label>Select Sector</label>
                            <select
                                value={filterSector}
                                onChange={(e) => setFilterSector(e.target.value)}
                                id="sector"
                            >
                                <option value="">All Sectors</option>
                                {sectors.map((name) => (
                                    <option key={name} value={name}>{name}</option>
                                ))}
                            </select>
                        </div>

                        <div className="resultfilter">
                            <label>Search Project</label>
                            <input
                                type="text"
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                                onKeyDown={handleSearchKeyDown}
                                id="projectname"
                                placeholder="Search by project name..."
                            />
                        </div>
                    </div>

                    {loading ? (
                        <div className="resultcount" style={{ textAlign: "center", padding: "2rem" }}>
                            Loading projects...
                        </div>
                    ) : (
                        <>
                            {/* COUNT */}
                            <div className="resultcount">
                                <strong>{projectData.length}</strong>
                                {" "}projects found
                            </div>

                            {/* TABLE */}
                            <div className="resultstablewrapper">
                                <table className="resultstable">
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Project Name</th>
                                            <th>Location</th>
                                            <th>Sector</th>
                                            <th>Risk Level</th>
                                            <th>View</th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {projectData.length > 0 ? (
                                            projectData.map((project, index) => (
                                                <tr key={project.project_id || index}>
                                                    <td className="serialnumber">
                                                        {index + 1}
                                                    </td>
                                                    <td className="projectname">
                                                        {project.name}
                                                    </td>
                                                    <td>
                                                        {getLocationDisplay(project)}
                                                    </td>
                                                    <td>
                                                        {project.sector}
                                                    </td>
                                                    <td>
                                                        <span
                                                            className={`riskbadge ${
                                                                project.latest_risk?.risk_level?.toLowerCase() || "unknown"
                                                            }`}
                                                        >
                                                            <span className="riskdot"></span>
                                                            {getRiskLevelDisplay(project.latest_risk?.risk_level) || "No Risk"}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <button
                                                            className="viewproject"
                                                            onClick={() =>
                                                                navigate("/project-detail", {
                                                                    state: { projectId: project.project_id }
                                                                })
                                                            }
                                                        >
                                                            View
                                                            <span>→</span>
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan="6" className="noresults">
                                                    No projects found.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}

                </div>
            </main>
        </section>
    );
}

export default SearchResults;