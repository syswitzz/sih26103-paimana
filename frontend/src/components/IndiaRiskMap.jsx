import { useEffect, useState } from "react";
import IndiaMap from "@react-map/india";
import "./IndiaRiskMap.css";
import { getErrorMessage, getStateRisks } from "../services/api";

function IndiaRiskMap() {

    const [selectedState, setSelectedState] = useState(null);
    const [riskData, setRiskData] = useState({});
    const [error, setError] = useState(null);

    const normalizeKey = (state) => (state || "").replace(/\s+/g, "");

    useEffect(() => {
        getStateRisks()
            .then((states) => {
                setRiskData(Object.fromEntries(states.map((item) => [
                    normalizeKey(item.state),
                    item,
                ])));
            })
            .catch((err) => setError(getErrorMessage(err)));
    }, []);

    const getRiskClass = (state) => {
        return riskData[normalizeKey(state)]?.risk_level?.toLowerCase() || "no-data";
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

                        {riskData[normalizeKey(selectedState)] && (
                            <span>{riskData[normalizeKey(selectedState)].project_count} projects</span>
                        )}

                    </div>
                )}

            </div>

            {error && <p className="maperror">{error}</p>}

        </div>
    );
}

export default IndiaRiskMap;