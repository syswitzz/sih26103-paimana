import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import logo from '../Static/logo.png';
import "./Dashboard.css";
import IndiaRiskMap from "./IndiaRiskMap";
import { Doughnut } from "react-chartjs-2";
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend
} from "chart.js";
import { getDashboardSummary, getErrorMessage } from "../services/api";

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
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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
                    <img src={logo} alt="PAIMANA Logo"></img>
                    <button id="riskbtn"><strong>+ Predict Risk</strong></button>
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
                <img src={logo} alt="PAIMANA Logo"></img>
                <button id="riskbtn"><strong>+ Predict Risk</strong></button>
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

            <form className="searchbox" onSubmit={(event) => {
                event.preventDefault();
                handleSearch();
            }}>
                <label>Select Sector</label>
                <select id="sector"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}>
                    <option value="">All Sectors</option>
                    <option value="Roads">Roads</option>
                    <option value="Power">Power</option>
                    <option value="Railways">Railways</option>
                    <option value="Irrigation">Irrigation</option>
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