import { Link } from "react-router-dom";
import bgImage from "../assets/water.jpg";
import "./Home.css";

const QUICK_LINKS = [
  { to: "/prediction", title: "Start a Test", desc: "Run a live water-quality test and log a report." },
  { to: "/dashboard", title: "View Dashboard", desc: "Real-time sensor stream and historical trends." },
  { to: "/reports", title: "Past Reports", desc: "Browse every test with min / max / avg ranges." },
];

function Home() {
  return (
    <div className="home-page" style={{ backgroundImage: `url(${bgImage})` }}>
      <div className="overlay"></div>

      <div className="home-content">
        <div className="left-section">
          <span className="eyebrow">ESP32 · Real-time · Machine Learning</span>
          <h1>
            Know your water,
            <br />
            <span className="grad-text">before it knows you.</span>
          </h1>
          <p>
            Our system reads pH, turbidity, dissolved oxygen, temperature and TDS
            straight off an ESP32 sensor array, streams it live, and predicts
            water safety with a trained ML model — so contamination is caught
            in seconds, not days.
          </p>
          <div className="hero-actions">
            <Link to="/prediction" className="btn">Start a Test</Link>
            <Link to="/dashboard" className="btn ghost">View Live Dashboard</Link>
          </div>
        </div>

        <div className="right-section">
          <div className="sonar-ring">
            <div className="sonar-sweep" />
            <div className="sonar-core">
              <span className="sonar-label">LIVE SCAN</span>
              <span className="sonar-sub">ESP32 · WQS-01</span>
            </div>
          </div>
        </div>
      </div>

      <div className="quick-links">
        {QUICK_LINKS.map((q) => (
          <Link key={q.to} to={q.to} className="quick-card">
            <h3>{q.title}</h3>
            <p>{q.desc}</p>
            <span className="quick-arrow">→</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default Home;
