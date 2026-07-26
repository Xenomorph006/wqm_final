"use client";

import { usePathname } from "next/navigation";
import Navbar from "./Navbar";
import Footer from "./Footer";

export default function AppShell({ children }) {
  const pathname = usePathname();
  const isDashboard = pathname === "/dashboard";

  return (
    <div className="app">
      <Navbar />

      <div key={pathname} className="route-transition">
        {children}
      </div>

      {!isDashboard && <Footer />}
    </div>
  );
}
