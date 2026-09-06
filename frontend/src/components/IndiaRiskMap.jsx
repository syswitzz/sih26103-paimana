import { useState } from "react";
import IndiaMap from "@react-map/india";
import "./IndiaRiskMap.css";

function IndiaRiskMap() {

    const [selectedState, setSelectedState] = useState(null);

    // Dummy data for now
    const riskData = {
        Maharashtra: "high",
        Gujarat: "medium",
        Rajasthan: "low",
        Karnataka: "high",
        TamilNadu: "medium",
        Kerala: "low",
        Telangana: "high",
        AndhraPradesh: "medium",
        Odisha: "high",
        WestBengal: "medium",
        Bihar: "high",
        UttarPradesh: "high",
        Punjab: "low",
        Haryana: "medium",
        MadhyaPradesh: "high",
        Chhattisgarh: "medium",
        Jharkhand: "high",
        Assam: "low",
        Delhi: "medium"
    };

    const getRiskClass = (state) => {
        return riskData[state] || "no-data";
    };

    const handleStateHover = (state) => {
        setSelectedState(state);
    };

    const handleStateLeave = () => {
        setSelectedState(null);
    };

    return (
        <div className="indiariskmap">

            <div className="indiariskmapheader">
                <div>
                    <h2>Project Risk by State</h2>
                    <p>State-wise infrastructure project risk</p>
                </div>

                <div className="risklegend">

                    <span>
                        <i className="high"></i>
                        High
                    </span>

                    <span>
                        <i className="medium"></i>
                        Medium
                    </span>

                    <span>
                        <i className="low"></i>
                        Low
                    </span>

                    <span>
                        <i className="no-data"></i>
                        No Data
                    </span>

                </div>
            </div>


            <div className="maparea">

                <IndiaMap
                    className="indiamap"
                    type="select-single"
                    onSelect={(state) => handleStateHover(state)}
                    onMouseEnter={(state) => handleStateHover(state)}
                    onMouseLeave={handleStateLeave}
                    locationClassName={(state) => getRiskClass(state)}
                />


                {selectedState && (
                    <div className="statetooltip">

                        <strong>
                            {selectedState}
                        </strong>

                        <span>
                            Risk Level:
                            <b className={getRiskClass(selectedState)}>
                                {getRiskClass(selectedState).toUpperCase()}
                            </b>
                        </span>

                    </div>
                )}

            </div>

        </div>
    );
}

export default IndiaRiskMap;