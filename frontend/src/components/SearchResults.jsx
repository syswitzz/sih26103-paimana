import { useNavigate, useLocation } from "react-router-dom";
import "./SearchResults.css";

function SearchResults({ projects = [] }) {
    const navigate = useNavigate();
    const location = useLocation();

    const projectName = location.state?.projectName || "";
    const sector = location.state?.sector || "";

    // Temporary dummy data
    const dummyProjects = [
        {
            id: 1,
            name: "Delhi–Meerut Expressway",
            location: "Uttar Pradesh",
            sector: "Roads",
            riskLevel: "High"
        },
        {
            id: 2,
            name: "Bengaluru–Mysuru Expressway",
            location: "Karnataka",
            sector: "Roads",
            riskLevel: "Medium"
        },
        {
            id: 3,
            name: "Mumbai–Nagpur Expressway",
            location: "Maharashtra",
            sector: "Roads",
            riskLevel: "High"
        },
        {
            id: 4,
            name: "Agra–Gwalior Expressway",
            location: "Uttar Pradesh",
            sector: "Roads",
            riskLevel: "Low"
        },
        {
            id: 5,
            name: "Amritsar–Jamnagar Expressway",
            location: "Multiple States",
            sector: "Roads",
            riskLevel: "Medium"
        }
    ];

    // Use backend data later.
    // For now use dummy data.
    const projectData = projects.length > 0 ? projects : dummyProjects;

    // Match project according to search text
    const searchText = projectName.toLowerCase();

    const filteredProjects = projectData.filter((project) => {
        const matchesName =
            project.name.toLowerCase().includes(searchText);

        const matchesSector =
            !sector ||
            project.sector.toLowerCase() === sector.toLowerCase();

        return matchesName && matchesSector;
    });

    // Open project detail page
    const handleViewProject = (project) => {
        navigate("/project-detail", {
            state: {
                project: project
            }
        });
    };

    return (
        <section className="searchresultssection">
            <header className="resultstopbar">

                    <div className="resultstitle">
                        <strong>PAIMANA</strong>
                        <span> a stronger infrastructure tomorrow</span>
                    </div>

                    <div className="resultsuser">
                        ♙
                    </div>

            </header>

            


            {/* MAIN AREA */}
            <main className="resultsmain">

                {/* TOP BAR */}
                


                {/* CONTENT */}
                <div className="resultscontent">

                    <div className="resultsheader">

                        <div>
                            <h1>Search Results</h1>
                            <br></br>
                            <p>
                                View matching projects and their key details.
                            </p>
                        </div>
                        <br></br>
                        <button
                            className="backhome"
                            onClick={() => navigate("/")}
                        >
                            ← Back to Home
                        </button>

                    </div>


                    {/* SEARCH FILTERS */}
                    <div className="resultsfilters">

                        <div className="resultfilter">

                            <label>Select Ministry</label>

                            <select defaultValue={sector} id="sector">

                                <option value="">
                                    All Ministries
                                </option>

                                <option value="transport">
                                    Ministry of Road Transport & Highways
                                </option>

                                <option value="railways">
                                    Ministry of Railways
                                </option>

                                <option value="energy">
                                    Ministry of Energy
                                </option>

                                <option value="irrigation">
                                    Ministry of Irrigation
                                </option>

                            </select>

                        </div>


                        <div className="resultfilter">

                            <label>Search Project</label>

                            <input
                                type="text"
                                defaultValue={projectName}
                                id="projectname"
                                placeholder="Search by project name, ID or keyword..."
                            />

                        </div>


                        <button className="resultsearchbtn">
                            Search
                        </button>

                    </div>


                    {/* COUNT */}
                    <div className="resultcount">

                        <strong>
                            {filteredProjects.length}
                        </strong>

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

                                {filteredProjects.length > 0 ? (

                                    filteredProjects.map((project, index) => (

                                        <tr key={project.id || index}>

                                            <td className="serialnumber">
                                                {index + 1}
                                            </td>

                                            <td className="projectname">
                                                {project.name}
                                            </td>

                                            <td>
                                                {project.location}
                                            </td>

                                            <td>
                                                {project.sector}
                                            </td>

                                            <td>

                                                <span
                                                    className={`riskbadge ${project.riskLevel.toLowerCase()}`}
                                                >

                                                    <span className="riskdot"></span>

                                                    {project.riskLevel}

                                                </span>

                                            </td>

                                            <td>

                                                <button
                                                    className="viewproject"
                                                    onClick={() =>
                                                        handleViewProject(project)
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

                                        <td
                                            colSpan="6"
                                            className="noresults"
                                        >
                                            No projects found.
                                        </td>

                                    </tr>

                                )}

                            </tbody>

                        </table>

                    </div>

                </div>

            </main>

        </section>
    );
}

export default SearchResults;