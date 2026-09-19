import { Link } from "react-router-dom";
import bgImage from "../assets/water.jpg";
import "./About.css";

function About() {
  return (
    <div
      className="page about-page"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="overlay"></div>
      <div className="content">
        <h2>About This Project</h2>

        <strong className="accent">Smart Water Quality Prediction Using ESP32</strong>

        <p>
          This project focuses on developing a smart and cost-effective water
          quality monitoring and prediction system using the ESP32
          microcontroller. The system collects real-time water parameters such
          as pH, turbidity, temperature, and Total Dissolved Solids (TDS)
          through connected sensors. These parameters are continuously
          processed by the ESP32 and transmitted to a cloud platform for
          storage and analysis via Wi-Fi connectivity.
        </p>

        <p>
          The main objective of this project is not only to monitor water
          quality but also to predict water quality status using machine
          learning techniques. By analyzing sensor data patterns, the system
          can classify water as safe or unsafe and provide early warnings if
          contamination levels increase. This makes the solution highly useful
          for drinking water monitoring, aquaculture, environmental studies,
          and smart city applications.
        </p>

        <p>
          The ESP32 is chosen due to its low power consumption, built-in Wi-Fi
          and Bluetooth capabilities, and high processing performance, making
          it ideal for IoT-based environmental monitoring systems. The system
          is designed to be affordable, scalable, and easy to deploy in rural
          and urban areas.
        </p>

        <p>
          Overall, this project contributes to sustainable water management by
          enabling real-time monitoring and intelligent prediction of water
          quality.
        </p>

        <div className="about-links">
          <Link to="/prediction" className="btn">Try a Live Test</Link>
          <Link to="/dashboard" className="btn ghost">See the Dashboard</Link>
          <Link to="/contact" className="btn ghost">Get in Touch</Link>
        </div>
      </div>
    </div>
  );
}

export default About;
