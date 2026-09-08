import React, { useState, useEffect } from "react";
import { useNavigate, useLocation, useSearchParams } from "react-router-dom";
import "./ProjectDetail.css";
import { getProject, getMilestones, getProgress, getRisk, getErrorMessage } from "../services/api";

function ProjectDetail() {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchParams] = useSearchParams();

    // Support both search navigation state and directly loaded query URLs.
    const projectId = location.state?.projectId || searchParams.get("id");
    const [projectData, setProjectData] = useState(null);
    const [milestones, setMilestones] = useState([]);
    const [progressData, setProgressData] = useState(null);
    const [riskData, setRiskData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [notFound, setNotFound] = useState(false);

    // Fetch all project-related data
    useEffect(() => {
        if (!projectId) {
            setNotFound(true);
            setLoading(false);
            return;
        }

        const fetchProjectDetail = async () => {
            try {
                setLoading(true);
                setError(null);
                setNotFound(false);

                const [project, milestonesResult, progressResult, riskResult] = await Promise.all([
                    getProject(projectId),
                    getMilestones(projectId),
                    getProgress(projectId),
                    getRisk(projectId).catch(() => null),
                ]);

                setProjectData(project);
                setMilestones(Array.isArray(milestonesResult) ? milestonesResult : []);
                setProgressData(Array.isArray(progressResult) ? progressResult[0] || null : null);
                setRiskData(riskResult);
            } catch (err) {
                if (err.status === 404) {
                    setNotFound(true);
                } else {
                    setError(getErrorMessage(err));
                }
            } finally {
                setLoading(false);
            }
        };

        fetchProjectDetail();
    }, [projectId]);

    const getRiskClass = (risk) => {
        if (!risk) return "unknown";
        return risk?.toLowerCase().replace(/\s+/g, "-");
    };

    const formatCurrency = (value) => {
        if (!value) return "N/A";
        return `₹ ${Number(value).toFixed(2)} Cr`;
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return "N/A";
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString("en-IN", {
                year: "numeric",
                month: "short",
                day: "numeric"
            });
        } catch {
            return dateStr;
        }
    };

    if (loading) {
        return (
            <div className="project-detail-page">
                <header className="project-detail-header">
                    <button className="back-button" onClick={() => navigate(-1)}>
                        ← Back
                    </button>
                </header>
                <main className="project-detail-content" style={{ textAlign: "center", padding: "2rem" }}>
                    <p>Loading project details...</p>
                </main>
            </div>
        );
    }

    if (notFound || !projectData) {
        return (
            <div className="project-detail-page">
                <header className="project-detail-header">
                    <button className="back-button" onClick={() => navigate(-1)}>
                        ← Back
                    </button>
                </header>
                <main className="project-detail-content" style={{ textAlign: "center", padding: "2rem" }}>
                    <h2>Project Not Found</h2>
                    <p>The requested project could not be found.</p>
                    <button onClick={() => navigate("/")} style={{ marginTop: "1rem", padding: "0.5rem 1rem", cursor: "pointer" }}>
                        Return to Home
                    </button>
                </main>
            </div>
        );
    }

    const physicalProgress = Number(progressData?.physical_progress_pct || 0);
    const financialProgress = projectData?.revised_cost && projectData?.sanctioned_cost
        ? Math.min((Number(projectData.sanctioned_cost) / Number(projectData.revised_cost)) * 100, 100)
        : 0;

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

                {riskData && (
                    <div className={`risk-badge ${getRiskClass(riskData.risk_level)}`}>
                        {riskData.risk_level} Risk
                    </div>
                )}

            </header>

            {error && (
                <div style={{
                    backgroundColor: "#fee2e2",
                    color: "#991b1b",
                    padding: "1rem",
                    margin: "1rem",
                    borderRadius: "0.5rem"
                }}>
                    ⚠️ {error}
                </div>
            )}


            {/* PROJECT INFORMATION */}
            <main className="project-detail-content">

                <section className="project-info-card">

                    <div className="section-title">
                        <h2>Project Information</h2>
                    </div>

                    <div className="project-info-grid">

                        <div className="info-item">
                            <span>Project ID</span>
                            <strong>{projectData.project_id}</strong>
                        </div>

                        <div className="info-item">
                            <span>Ministry</span>
                            <strong>{projectData.ministry || "N/A"}</strong>
                        </div>

                        <div className="info-item">
                            <span>Sector</span>
                            <strong>{projectData.sector || "N/A"}</strong>
                        </div>

                        <div className="info-item">
                            <span>Location</span>
                            <strong>{projectData.district || "N/A"}</strong>
                        </div>

                        <div className="info-item">
                            <span>State</span>
                            <strong>{projectData.state || "N/A"}</strong>
                        </div>

                        <div className="info-item">
                            <span>Implementing Agency</span>
                            <strong>{projectData.implementing_agency || "N/A"}</strong>
                        </div>

                    </div>

                </section>


                {/* COST OVERVIEW */}
                <section className="cost-section">

                    <h2>Financial Overview</h2>

                    <div className="cost-cards">

                        <div className="cost-card">
                            <span>Sanctioned Cost</span>
                            <h3>{formatCurrency(projectData.sanctioned_cost)}</h3>
                        </div>

                        <div className="cost-card">
                            <span>Latest Revised Cost</span>
                            <h3>{formatCurrency(projectData.revised_cost || projectData.sanctioned_cost)}</h3>
                        </div>

                        <div className="cost-card">
                            <span>Cumulative Expenditure</span>
                            <h3>{formatCurrency(progressData?.expenditure_cumulative)}</h3>
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
                                    {physicalProgress.toFixed(1)}%
                                </strong>
                            </div>

                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${Math.min(physicalProgress, 100)}%`
                                    }}
                                ></div>
                            </div>

                        </div>


                        <div className="progress-item">

                            <div className="progress-heading">
                                <span>Financial Progress (Cost Ratio)</span>
                                <strong>
                                    {financialProgress.toFixed(1)}%
                                </strong>
                            </div>

                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{
                                        width: `${Math.min(financialProgress, 100)}%`
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
                            <strong>{formatDate(projectData.start_date)}</strong>
                        </div>

                        <div className="timeline-line"></div>

                        <div className="timeline-item">
                            <span>Expected Completion</span>
                            <strong>
                                {formatDate(projectData.planned_end_date)}
                            </strong>
                        </div>

                        <div className="timeline-item" style={{ color: projectData.current_status === "DELAYED" ? "#dc2626" : "#16a34a" }}>
                            <span>Current Status</span>
                            <strong>{projectData.current_status || "N/A"}</strong>
                        </div>

                    </div>

                </section>


                {/* AI INTELLIGENCE */}
                <section className="ai-intelligence-section">
                    <div className="ai-section-heading">
                        <div>
                            <span className="ai-eyebrow">PAIMANA Intelligence</span>
                            <h2>AI Project Intelligence</h2>
                            <p>Model-backed signals generated from this project's latest data.</p>
                        </div>
                        {riskData && (
                            <span className={`ai-status ${getRiskClass(riskData.risk_level)}`}>
                                {riskData.risk_level} Risk
                            </span>
                        )}
                    </div>

                    {riskData ? (
                        <div className="ai-intelligence-card">
                            <div className="ai-summary">
                                <span>Overall Risk Score</span>
                                <strong>{Number(riskData.risk_score).toFixed(1)}<small>/100</small></strong>
                                <p>
                                    {riskData.risk_level === "HIGH"
                                        ? "The current model output places this project in the high-risk band."
                                        : riskData.risk_level === "MEDIUM"
                                            ? "The current model output places this project in the medium-risk band."
                                            : "The current model output places this project in the low-risk band."}
                                </p>
                            </div>

                            <div className="ai-metrics">
                                <div className="ai-metric">
                                    <span>Health Score</span>
                                    <strong>{Number(riskData.health_score).toFixed(1)}<small>/100</small></strong>
                                </div>
                                <div className="ai-metric">
                                    <span>Delay Probability</span>
                                    <strong>{(Number(riskData.delay_probability) * 100).toFixed(0)}%</strong>
                                </div>
                                <div className="ai-metric">
                                    <span>Cost-Overrun Probability</span>
                                    <strong>{(Number(riskData.cost_overrun_probability) * 100).toFixed(0)}%</strong>
                                </div>
                                <div className="ai-metric">
                                    <span>Cost-Overrun Estimate</span>
                                    <strong>{formatCurrency(riskData.cost_overrun_estimate)}</strong>
                                </div>
                            </div>

                            <div className="ai-breakdown">
                                <div className="ai-breakdown-header">
                                    <span>Risk Signal Breakdown</span>
                                    <small>Model: {riskData.model_version}</small>
                                </div>
                                {Object.entries(riskData.component_breakdown || {}).map(([name, value]) => (
                                    <div className="ai-breakdown-row" key={name}>
                                        <span>{name.replace(/[_-]/g, " ")}</span>
                                        <div className="ai-breakdown-track">
                                            <div className="ai-breakdown-fill" style={{ width: `${Math.min(Number(value) * 100, 100)}%` }}></div>
                                        </div>
                                        <strong>{(Number(value) * 100).toFixed(0)}%</strong>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="ai-unavailable">
                            <strong>Prediction unavailable</strong>
                            <span>No persisted model result is available for this project yet.</span>
                        </div>
                    )}
                </section>

                {/* RISK */}
                {riskData && (
                    <section className="risk-section">

                        <h2>Risk Assessment</h2>

                        <div className="risk-card">

                            <div className="risk-score">

                                <span>Risk Score</span>

                                <strong>
                                    {Number(riskData.risk_score).toFixed(1)}
                                </strong>

                                <small>/ 100</small>

                            </div>


                            <div className="risk-details">

                                <div className="risk-status">
                                    <span>Risk Level</span>

                                    <strong
                                        className={`risk-text ${getRiskClass(
                                            riskData.risk_level
                                        )}`}
                                    >
                                        {riskData.risk_level}
                                    </strong>
                                </div>

                                <div className="risk-status">
                                    <span>Delay Probability</span>
                                    <strong>{(Number(riskData.delay_probability) * 100).toFixed(0)}%</strong>
                                </div>

                                <div className="risk-status">
                                    <span>Cost Overrun Probability</span>
                                    <strong>{(Number(riskData.cost_overrun_probability) * 100).toFixed(0)}%</strong>
                                </div>

                            </div>

                        </div>

                    </section>
                )}


                {/* MILESTONES */}
                {milestones.length > 0 && (
                    <section className="description-section">

                        <h2>Milestones</h2>

                        <div className="description-card">
                            <table style={{ width: "100%", borderCollapse: "collapse" }}>
                                <thead>
                                    <tr>
                                        <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: "0.5rem" }}>Milestone</th>
                                        <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: "0.5rem" }}>Planned Date</th>
                                        <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: "0.5rem" }}>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {milestones.map((milestone) => (
                                        <tr key={milestone.milestone_id}>
                                            <td style={{ borderBottom: "1px solid #eee", padding: "0.5rem" }}>{milestone.name}</td>
                                            <td style={{ borderBottom: "1px solid #eee", padding: "0.5rem" }}>{formatDate(milestone.planned_date)}</td>
                                            <td style={{ borderBottom: "1px solid #eee", padding: "0.5rem" }}>
                                                <span style={{
                                                    backgroundColor: milestone.status === "COMPLETED" ? "#dcfce7" : "#fef3c7",
                                                    color: milestone.status === "COMPLETED" ? "#166534" : "#92400e",
                                                    padding: "0.25rem 0.5rem",
                                                    borderRadius: "0.25rem",
                                                    fontSize: "0.875rem"
                                                }}>
                                                    {milestone.status}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                    </section>
                )}

            </main>

        </div>
    );
}

export default ProjectDetail;