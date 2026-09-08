import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./ProjectDetail.css";

function ProjectDetail() {
    const navigate = useNavigate();
    const location = useLocation();

    // Project data coming from Search Results
    const project = location.state?.project;

    // Temporary data for UI testing
    // Backend developer can replace this later with API data.
    const projectData = project || {
        id: "PAIMANA-001",
        name: "Delhi–Mumbai Expressway",
        ministry: "Ministry of Road Transport & Highways",
        sector: "Transport",
        location: "Delhi - Mumbai",
        state: "Multiple States",

        originalCost: "₹ 98,000 Cr",
        revisedCost: "₹ 1,05,000 Cr",
        expenditure: "₹ 72,500 Cr",

        physicalProgress: 76,
        financialProgress: 69,

        startDate: "01 Jan 2020",
        expectedCompletion: "31 Dec 2026",

        riskLevel: "Medium",
        riskScore: 58,

        delay: "8 Months",

        contractor: "Example Infrastructure Ltd.",
        nodalOfficer: "Project Director",

        description:
            "This project involves the development of a major expressway connecting Delhi and Mumbai with improved connectivity and reduced travel time."
    };

    const getRiskClass = (risk) => {
        return risk?.toLowerCase().replace(/\s+/g, "-");
    };

    return (
        <div className="project-detail-page">

            {/* HEADER */}
            <header className="project-detail-header">

                <button
                    className="back-button"
                    onClick={() => navigate(-1)}
                >
                    ← Back
                </button>

                <div className="project-title">
                    <span>Project Details</span>
                    <h1>{projectData.name}</h1>
                </div>

                <div
                    className={`risk-badge ${getRiskClass(
                        projectData.riskLevel
                    )}`}
                >
                    {projectData.riskLevel} Risk
                </div>

            </header>


            {/* PROJECT INFORMATION */}
            <main className="project-detail-content">

                <section className="project-info-card">

                    <div className="section-title">
                        <h2>Project Information</h2>
                    </div>

                    <div className="project-info-grid">

                        <div className="info-item">
                            <span>Project ID</span>
                            <strong>{projectData.id}</strong>
                        </div>

                        <div className="info-item">
                            <span>Ministry</span>
                            <strong>{projectData.ministry}</strong>
                        </div>

                        <div className="info-item">
                            <span>Sector</span>
                            <strong>{projectData.sector}</strong>
                        </div>

                        <div className="info-item">
                            <span>Location</span>
                            <strong>{projectData.location}</strong>
                        </div>

                        <div className="info-item">
                            <span>State</span>
                            <strong>{projectData.state}</strong>
                        </div>

                        <div className="info-item">
                            <span>Contractor</span>
                            <strong>{projectData.contractor}</strong>
                        </div>

                    </div>

                </section>


                {/* COST OVERVIEW */}
                <section className="cost-section">

                    <h2>Financial Overview</h2>

                    <div className="cost-cards">

                        <div className="cost-card">
                            <span>Original Cost</span>
                            <h3>{projectData.originalCost}</h3>
                        </div>

                        <div className="cost-card">
                            <span>Latest Revised Cost</span>
                            <h3>{projectData.revisedCost}</h3>
                        </div>

                        <div className="cost-card">
                            <span>Cumulative Expenditure</span>
                            <h3>{projectData.expenditure}</h3>
                        </div>

                    </div>

                </section>


                {/* PROGRESS */}
                <section className="progress-section">

                    <h2>Project Progress</h2>

                    <div className="progress-card">

                        <div className="progress-item">

                            <div className="progress-heading">
                                <span>Physical Progress</span>
                                <strong>
                                    {projectData.physicalProgress}%
                                </strong>
                            </div>

                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${projectData.physicalProgress}%`
                                    }}
                                ></div>
                            </div>

                        </div>


                        <div className="progress-item">

                            <div className="progress-heading">
                                <span>Financial Progress</span>
                                <strong>
                                    {projectData.financialProgress}%
                                </strong>
                            </div>

                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${projectData.financialProgress}%`
                                    }}
                                ></div>
                            </div>

                        </div>

                    </div>

                </section>


                {/* TIMELINE */}
                <section className="timeline-section">

                    <h2>Project Timeline</h2>

                    <div className="timeline-card">

                        <div className="timeline-item">
                            <span>Start Date</span>
                            <strong>{projectData.startDate}</strong>
                        </div>

                        <div className="timeline-line"></div>

                        <div className="timeline-item">
                            <span>Expected Completion</span>
                            <strong>
                                {projectData.expectedCompletion}
                            </strong>
                        </div>

                        <div className="timeline-item delay">
                            <span>Current Delay</span>
                            <strong>{projectData.delay}</strong>
                        </div>

                    </div>

                </section>


                {/* RISK */}
                <section className="risk-section">

                    <h2>Risk Assessment</h2>

                    <div className="risk-card">

                        <div className="risk-score">

                            <span>Risk Score</span>

                            <strong>
                                {projectData.riskScore}
                            </strong>

                            <small>/ 100</small>

                        </div>


                        <div className="risk-details">

                            <div className="risk-status">
                                <span>Risk Level</span>

                                <strong
                                    className={`risk-text ${getRiskClass(
                                        projectData.riskLevel
                                    )}`}
                                >
                                    {projectData.riskLevel}
                                </strong>
                            </div>

                            <div className="risk-status">
                                <span>Delay</span>
                                <strong>{projectData.delay}</strong>
                            </div>

                        </div>

                    </div>

                </section>


                {/* DESCRIPTION */}
                <section className="description-section">

                    <h2>Project Description</h2>

                    <div className="description-card">
                        <p>{projectData.description}</p>
                    </div>

                </section>


                {/* OFFICER */}
                <section className="officer-section">

                    <h2>Project Administration</h2>

                    <div className="officer-card">

                        <div>
                            <span>Nodal Officer</span>
                            <strong>{projectData.nodalOfficer}</strong>
                        </div>

                        <div>
                            <span>Contractor</span>
                            <strong>{projectData.contractor}</strong>
                        </div>

                    </div>

                </section>

            </main>

        </div>
    );
}

export default ProjectDetail;