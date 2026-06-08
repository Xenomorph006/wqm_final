import React from "react";
import "./Dashboard.css";
import bgImage from "../assets/water.jpg";

function Dashboard() {
  return (
    <div
      className="dashboard"
      style={{
        backgroundImage: `url(${bgImage})`
      }}
    >
      {/* Overlay */}
      <div className="overlay"></div>

      <div className="dashboard-content">

        {/* Sidebar */}
        <div className="sidebar">
          <h2 className="logo">💧 WQS</h2>
          <ul>
            <li className="active">Dashboard</li>
            <li>Predictions</li>
            <li>Reports</li>
            <li>Settings</li>
          </ul>
        </div>

        {/* Main Section */}
        <div className="main">

          <div className="topbar">
            <h2>Dashboard</h2>
          </div>

          {/* Cards */}
          <div className="cards">
            <div className="card">
              <h3>120</h3>
              <p>Total Tests</p>
            </div>

            <div className="card">
              <h3>85%</h3>
              <p>Good Water</p>
            </div>

            <div className="card">
              <h3>10%</h3>
              <p>Moderate</p>
            </div>

            <div className="card">
              <h3>5%</h3>
              <p>Poor</p>
            </div>
          </div>

          {/* Chart */}
          <div className="chart-section">
            <h3>Water Quality Overview</h3>
            <div className="chart-placeholder">
              📊 Chart will appear here
            </div>
          </div>

          {/* Table */}
          <div className="table-section">
            <h3>Recent Predictions</h3>
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>pH</th>
                  <th>Turbidity</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>19 Feb</td>
                  <td>7.2</td>
                  <td>3 NTU</td>
                  <td className="good">Good</td>
                </tr>
                <tr>
                  <td>18 Feb</td>
                  <td>6.1</td>
                  <td>7 NTU</td>
                  <td className="moderate">Moderate</td>
                </tr>
                <tr>
                  <td>17 Feb</td>
                  <td>5.5</td>
                  <td>12 NTU</td>
                  <td className="poor">Poor</td>
                </tr>
              </tbody>
            </table>
          </div>

        </div>
      </div>
    </div>
  );
}

export default Dashboard;
