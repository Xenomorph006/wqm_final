"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
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
  const pathname = usePathname();

  return (
    <>
      <div className="nav-trigger" aria-hidden="true" />
      <nav className="topnav">
        <div className="nav-brand">
          <span className="nav-brand-dot" />
          WQS
        </div>
        <div className="nav-left">
          {LINKS.map((link) => {
            const isActive =
              link.to === "/" ? pathname === "/" : pathname.startsWith(link.to);
            return (
              <Link
                key={link.to}
                href={link.to}
                className={"nav-link" + (isActive ? " active" : "")}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </>
  );
}

export default Navbar;
