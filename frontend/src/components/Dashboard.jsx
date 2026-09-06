import React,{useState} from "react";
import { useNavigate } from "react-router-dom";
import logo from '../Static/logo.png';
import "./Dashboard.css";
function Dashboard(){
    const navigate = useNavigate();

    const [projectName, setProjectName] = useState("");
    const [sector, setSector] = useState("");

    function handleSearch() {

        navigate("/search-results", {
            state: {
                projectName: projectName,
                sector: sector
            }
        });
    }
    return(
        <>
            <nav>
                <img src={logo}alt="PAIMANA Logo"></img>
                <button>☀️</button>
                <button>Login</button>
            </nav>
            <div className="searchbox">
                <label>select Ministry</label>
                <select id="sector"
                    value={sector}
                    onChange={(e) =>setSector(e.target.value)}>
                    <option value="">All Sectors</option>
                    <option value="transport">Transport</option>
                    <option value="energy">Energy</option>
                    <option value="railways">Railways</option>
                    <option value="irrigation">Irrigation</option>
                </select>
                        
                <label>Search project</label>
                <input placeholder="search project here" id="projectname" value={projectName} onChange={(e) =>setProjectName(e.target.value)}></input>
                <button id="search"
                onClick={handleSearch}>🔍</button>
            </div>
            <main>
                <div className="firstsection">
                    <h1>welcome Admin</h1>
                    <div className="Total projects">
                    <div className="project-count">
                        <p>project count :</p>
                        <h1>1775</h1>
                    </div>
                    <h1>📋</h1>

                </div>
                <div className="Revised cost">
                    <div className="total cost">
                        <p>original cost:</p>
                        <h1> ₹ 33,70,138.22</h1>

                    </div>
                    <h1>💰</h1>
                </div>
                <div className="cumulative expenditure">
                    <div className="expenditure">
                        <p>Expenditure(Cumm.) (in Cr.)</p>
                        <h1>₹ 19,26,099.57</h1>
                    </div>
                    <h1>📈</h1>
                </div>
                <div className="Avg physical progress ">
                    <div className="average progress">
                        <p>Latest Revised Cost (in Cr.)</p>
                        <h1>₹ 37,10,641.55</h1>

                    </div>
                    <h1>◔</h1>
                </div>
                </div>
                <div className="chartsection">
                    <div className="progress health overview">
                    <h1> pie chart here !</h1>

                    </div>
                    <div className="liveproject">
                        <h1> india map live project here !</h1>

                    </div>
                </div>
            </main>

        </>
    )


}
export default Dashboard;