import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../Static/logo.jpeg";
import "./Dashboard.css";
import IndiaRiskMap from "./IndiaRiskMap";
import { Doughnut } from "react-chartjs-2";
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend
} from "chart.js";
import { getDashboardSummary, getSectors, getErrorMessage, predictAllRisks, predictRiskStatus } from "../services/api";

// Register Chart.js components
ChartJS.register(
    ArcElement,
    Tooltip,
    Legend
);

function Dashboard() {
    const navigate = useNavigate();

    const [projectName, setProjectName] = useState("");
    const [sector, setSector] = useState("");
    const [sectors, setSectors] = useState([]);
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [predicting, setPredicting] = useState(false);
    const [predictConfirming, setPredictConfirming] = useState(false);
    const [predictStatus, setPredictStatus] = useState(null);

    // Fetch dashboard data on component mount
    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await getDashboardSummary();
                setDashboardData(data);
            } catch (err) {
                setError(getErrorMessage(err));
                // Use placeholder data if API fails
                setDashboardData({
                    total_projects: 0,
                    high_risk_projects: 0,
                    medium_risk_projects: 0,
                    low_risk_projects: 0,
                    open_alerts: 0,
                });
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, []);

    useEffect(() => {
        getSectors().then(setSectors).catch(() => setSectors([]));
    }, []);

    function handleSearch() {
        navigate("/search-results", {
            state: {
                projectName: projectName,
                sector: sector
            }
        });
    }

    function handleSearchKeyDown(event) {
        if (event.key === "Enter") event.currentTarget.form?.requestSubmit();
    }

    async function startPredictRisk() {
        setPredicting(true);
        setPredictStatus(null);
        try {
            await predictAllRisks();
            pollPredictStatus();
        } catch (err) {
            if (err.status === 409) {
                // A run is already in progress on the server — follow along.
                pollPredictStatus();
            } else {
                setPredicting(false);
                setPredictStatus({ type: "error", text: getErrorMessage(err) });
            }
        }
    }

    function pollPredictStatus(tries = 0) {
        const poll = async () => {
            try {
                const job = await predictRiskStatus();
                if (job.status === "running" || job.status === "idle") {
                    setPredictStatus(job.total
                        ? { type: "info", text: `Computing risk scores… (${job.updated} of ${job.total} done)` }
                        : { type: "info", text: "Computing risk scores in the background…" });
                    if (tries < 60) setTimeout(() => pollPredictStatus(tries + 1), 1500);
                    else {
                        setPredicting(false);
                        setPredictStatus({ type: "info", text: "Computation is still running in the background. Refresh later to see the results." });
                    }
                    return;
                }
                setPredicting(false);
                if (job.status === "done") {
                    const summary = await getDashboardSummary();
                    setDashboardData(summary);
                    setPredictStatus(job.updated > 0
                        ? { type: "success", text: `Risk predictions computed for ${job.updated ?? 0} project${job.updated === 1 ? "" : "s"}.` }
                        : { type: "info", text: "All projects already have risk predictions." });
                } else {
                    setPredictStatus({ type: "error", text: job.error || "Prediction failed in the background." });
                }
            } catch {
                if (tries < 60) setTimeout(() => pollPredictStatus(tries + 1), 1500);
                else {
                    setPredicting(false);
                    setPredictStatus({ type: "error", text: "Could not check the prediction status." });
                }
            }
        };
        poll();
    }

    function handlePredictRisk() {
        if (predicting) return;
        if (!predictConfirming) {
            setPredictConfirming(true);
            setPredictStatus({
                type: "warn",
                text: "This will compute AI risk scores only for projects that don't have one yet (e.g. newly added projects), not recompute the whole dataset. Click “+ Predict Risk” again to confirm."
            });
            return;
        }
        setPredictConfirming(false);
        startPredictRisk();
    }

    // Build risk distribution chart from API data
    const riskData = {
        labels: ["High Risk", "Medium Risk", "Low Risk"],
        datasets: [
            {
                data: dashboardData ? [
                    dashboardData.high_risk_projects || 0,
                    dashboardData.medium_risk_projects || 0,
                    dashboardData.low_risk_projects || 0
                ] : [0, 0, 0],
                backgroundColor: [
                    "#ef4444", // High (red)
                    "#f59e0b", // Medium (amber)
                    "#22c55e"  // Low (green)
                ],
                borderWidth: 0
            }
        ]
    };

    const riskOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "bottom"
            }
        },
        cutout: "65%"
    };

    if (loading && !dashboardData) {
        return (
            <>
                <nav>
                    <Link to="/"><img src={logo} alt="PAIMANA Logo"></img></Link>
                    <button id="riskbtn" onClick={handlePredictRisk} disabled={predicting}>
                        <strong>{predicting ? "+ Predicting…" : "+ Predict Risk"}</strong>
                    </button>
                    <button className="header-icon-button" aria-label="Open user account" title="User account">
                        <svg viewBox="0 0 24 24" aria-hidden="true">
                            <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 8a7 7 0 0 0-14 0" />
                        </svg>
                    </button>
                </nav>
                <main>
                    <p style={{ textAlign: "center", margin: "2rem" }}>Loading dashboard...</p>
                </main>
            </>
        );
    }

    return (
        <>
            <nav>
                <Link to="/"><img src={logo} alt="PAIMANA Logo"></img></Link>
                <button id="riskbtn" onClick={handlePredictRisk} disabled={predicting}>
                    <strong>{predicting ? "+ Predicting…" : "+ Predict Risk"}</strong>
                </button>
                <button className="header-icon-button" aria-label="Open user account" title="User account">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 8a7 7 0 0 0-14 0" />
                    </svg>
                </button>
            </nav>

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

            {predictStatus && (
                <div style={{
                    backgroundColor: predictStatus.type === "success"
                        ? "#dcfce7"
                        : predictStatus.type === "warn"
                            ? "#fef3c7"
                            : "#fee2e2",
                    color: predictStatus.type === "success"
                        ? "#166534"
                        : predictStatus.type === "warn"
                            ? "#92400e"
                            : "#991b1b",
                    padding: "1rem",
                    margin: "1rem",
                    borderRadius: "0.5rem"
                }}>
                    {predictStatus.type === "success" ? "✅"
                        : predictStatus.type === "warn" ? "⚠️"
                            : predictStatus.type === "info" ? "⏳"
                                : "⚠️"} {predictStatus.text}
                </div>
            )}

            <form className="searchbox" onSubmit={(event) => {
                event.preventDefault();
                handleSearch();
            }}>
                <label>Select Sector</label>
                <select id="sector"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}>
                    <option value="">All Sectors</option>
                    {sectors.map((name) => (
                        <option key={name} value={name}>{name}</option>
                    ))}
                </select>

                <label>Search project</label>
                <input
                    placeholder="Search projects here"
                    id="projectname"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    onKeyDown={handleSearchKeyDown}>
                </input>
                <button id="search" type="submit">🔍</button>
            </form>

            <main>
                <div className="firstsection">
                    <h1>Welcome, Admin</h1>
                    <div className="Total projects">
                        <div className="project-count">
                            <p>Project Count</p>
                            <h1>{dashboardData?.total_projects || 0}</h1>
                        </div>
                        <h1>📋</h1>
                    </div>

                    <div className="Revised cost">
                        <div className="total cost">
                            <p>Total Cost (Sanctioned):</p>
                            <h1>₹ {dashboardData?.total_sanctioned_cost ? Number(dashboardData.total_sanctioned_cost).toFixed(2) : 0} Cr</h1>
                        </div>
                        <h1>💰</h1>
                    </div>

                    <div className="cumulative expenditure">
                        <div className="expenditure">
                            <p>Total Cost (Revised):</p>
                            <h1>₹ {dashboardData?.total_revised_cost ? Number(dashboardData.total_revised_cost).toFixed(2) : 0} Cr</h1>
                        </div>
                        <h1>📈</h1>
                    </div>

                    <div className="Avg physical progress">
                        <div className="average progress">
                            <p>Avg Physical Progress:</p>
                            <h1>{dashboardData?.average_physical_progress ? Number(dashboardData.average_physical_progress).toFixed(1) : 0}%</h1>
                        </div>
                        <h1>◔</h1>
                    </div>
                </div>

                <div className="chartsection">
                    <div className="progress health overview">
                        <h2>Risk Distribution</h2>
                        <div className="risk-chart">
                            {!loading ? (
                                <Doughnut
                                    data={riskData}
                                    options={riskOptions}
                                />
                            ) : (
                                <p>Loading chart...</p>
                            )}
                        </div>
                    </div>
                    <div className="liveproject">
                        <IndiaRiskMap />
                    </div>
                </div>
            </main>
        </>
    );
}

export default Dashboard;