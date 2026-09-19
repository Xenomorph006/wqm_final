import { NavLink } from "react-router-dom";
import "./Navbar.css";

const LINKS = [
  { to: "/", label: "Home" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/prediction", label: "Start Test" },
  { to: "/reports", label: "Reports" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

function Navbar() {
  return (
    <>
      <div className="nav-trigger" aria-hidden="true" />
      <nav className="topnav">
        <div className="nav-brand">
          <span className="nav-brand-dot" />
          WQS
        </div>
        <div className="nav-left">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </>
  );
}

export default Navbar;
