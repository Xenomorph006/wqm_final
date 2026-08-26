import { Link } from "react-router-dom";
import "./Footer.css";

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <span className="nav-brand-dot" />
          <span>Water Quality System</span>
        </div>
        <nav className="footer-links">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/prediction">Start Test</Link>
          <Link to="/reports">Reports</Link>
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
        </nav>
      </div>
    </footer>
  );
}

export default Footer;
