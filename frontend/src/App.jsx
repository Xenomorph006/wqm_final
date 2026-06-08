import { Routes, Route, NavLink } from "react-router-dom";

import Home from "./pages/Home";
import Prediction from "./pages/Prediction";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Dashboard from "./pages/Dashboard";

import "./App.css";

function App() {
  return (
    <div className="app">

      {/* Top Navbar trigger zone (invisible strip at top) */}
      <div className="nav-trigger" />

      {/* Top Navbar */}
      <nav className="topnav">
        <div className="nav-left">
          <NavLink to="/" className="nav-link">Home</NavLink>
          <NavLink to="/dashboard" className="nav-link">Dashboard</NavLink>
          <NavLink to="/prediction" className="nav-link">Prediction</NavLink>
          <NavLink to="/about" className="nav-link">About</NavLink>
          <NavLink to="/contact" className="nav-link">Contact</NavLink>
        </div>
      </nav>

      {/* Pages */}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/prediction" element={<Prediction />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>

    </div>
  );
}

export default App;
