import Link from "next/link";
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
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/prediction">Start Test</Link>
          <Link href="/reports">Reports</Link>
          <Link href="/about">About</Link>
          <Link href="/contact">Contact</Link>
        </nav>
      </div>
    </footer>
  );
}

export default Footer;
