import { useState } from "react";
import bgImage from "../assets/water.jpg";
import "./Prediction.css";

function Prediction() {
  const [result, setResult] = useState("");

  const handlePredict = () => {
    setResult("Water is Safe for Drinking ✅"); // temporary output
  };

  return (
    <div
      className="page"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="overlay"></div>

      <div className="form-container">
        <h2>Water Quality Prediction</h2>

        <input type="number" placeholder="pH Level" />
        <input type="number" placeholder="Turbidity" />
        <input type="number" placeholder="Dissolved Oxygen" />
        <input type="number" placeholder="Temperature" />

        <button onClick={handlePredict}>Predict</button>

        {result && <h3 className="result">{result}</h3>}
      </div>
    </div>
  );
}

export default Prediction;
