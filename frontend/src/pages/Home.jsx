import bgImage from "../assets/water.jpg";
import rotatingImage from "../assets/react.svg"; // temporary image
import "./Home.css";

function Home() {
  return (
    <div
      className="home-page"
      style={{
        backgroundImage: `url(${bgImage})`
      }}
    >
      <div className="overlay"></div>

      <div className="home-content">

        {/* Left Side */}
        <div className="left-section">
          <h1>Welcome</h1>
          <p>
            Our system analyzes parameters like pH, turbidity,
            dissolved oxygen, and temperature to predict
            water quality using machine learning.
          </p>
        </div>

        {/* Right Side */}
        <div className="right-section">
          <img src={rotatingImage} alt="rotating" />
        </div>

      </div>
    </div>
  );
}

export default Home;
