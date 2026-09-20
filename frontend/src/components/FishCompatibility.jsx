import React from "react";
import "./FishCompatibility.css";

function badgeFromLists(suitable, moderate, notRecommended) {
  if (notRecommended.length > 0) return "poor";
  if (moderate.length > 0) return "moderate";
  if (suitable.length > 0) return "excellent";
  return "unknown";
}

function FishCompatibility({ data }) {
  // No agent result yet
  if (!data) {
    return (
      <section className="fish-section">
        <div className="fish-header">
          <div>
            <h3>🐟 Fish Compatibility</h3>
            <p>
              Run a water quality test to determine which fish species may be
              suitable.
            </p>
          </div>

          <span className="fish-status awaiting-test">Awaiting Test</span>
        </div>

        <div className="fish-empty">
          <div className="fish-empty-icon">🐟</div>

          <h4>No Compatibility Result Yet</h4>

          <p>
            Fish compatibility recommendations will appear here once the ML
            agent posts a prediction.
          </p>
        </div>
      </section>
    );
  }

  const {
    recommended_fish = [],
    unsuitable_fish = [],
    overall_recommendation = "",
  } = data;

  // recommended_fish items are bucketed by their own `suitability` field;
  // unsuitable_fish is already a distinct not-recommended list from the agent.
  const suitable = recommended_fish.filter((f) => f.suitability === "High");
  const moderate = recommended_fish.filter((f) => f.suitability !== "High");
  const notRecommended = unsuitable_fish;

  const waterCondition = badgeFromLists(suitable, moderate, notRecommended);
  const badgeLabel =
    waterCondition === "excellent"
      ? "Excellent"
      : waterCondition === "moderate"
      ? "Moderate"
      : waterCondition === "poor"
      ? "Poor"
      : "Unknown";

  return (
    <section className="fish-section">
      {/* Header */}
      <div className="fish-header">
        <div>
          <h3>🐟 Fish Compatibility</h3>

          <p>
            Recommended species based on current and predicted water quality.
          </p>
        </div>

        <span className={`fish-status ${waterCondition}`}>{badgeLabel}</span>
      </div>

      {/* Main Message */}
      {overall_recommendation && (
        <div className="fish-message">
          <span className="fish-message-icon">💧</span>

          <p>{overall_recommendation}</p>
        </div>
      )}

      {/* Suitable */}
      {suitable.length > 0 && (
        <div className="fish-group">
          <div className="fish-group-title suitable-title">
            <span className="fish-indicator suitable-indicator" />
            <h4>Suitable Species</h4>
          </div>

          <div className="fish-list">
            {suitable.map((fish, index) => (
              <div
                className="fish-card suitable-card"
                key={`${fish.species}-${index}`}
                title={fish.reason}
              >
                <span className="fish-icon">🐟</span>

                <div>
                  <strong>{fish.species}</strong>
                  <span>{fish.percentage}% match</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Moderate */}
      {moderate.length > 0 && (
        <div className="fish-group">
          <div className="fish-group-title moderate-title">
            <span className="fish-indicator moderate-indicator" />
            <h4>Moderately Suitable</h4>
          </div>

          <div className="fish-list">
            {moderate.map((fish, index) => (
              <div
                className="fish-card moderate-card"
                key={`${fish.species}-${index}`}
                title={fish.reason}
              >
                <span className="fish-icon">🐠</span>

                <div>
                  <strong>{fish.species}</strong>
                  <span>{fish.percentage}% match</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Not Recommended */}
      {notRecommended.length > 0 && (
        <div className="fish-group">
          <div className="fish-group-title danger-title">
            <span className="fish-indicator danger-indicator" />
            <h4>Not Recommended</h4>
          </div>

          <div className="fish-list">
            {notRecommended.map((fish, index) => (
              <div
                className="fish-card danger-card"
                key={`${fish.species}-${index}`}
                title={fish.reason}
              >
                <span className="fish-icon">🚫</span>

                <div>
                  <strong>{fish.species}</strong>
                  <span>{fish.percentage != null ? `${fish.percentage}% match` : "Not recommended"}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No species returned */}
      {suitable.length === 0 &&
        moderate.length === 0 &&
        notRecommended.length === 0 && (
          <div className="fish-empty">
            <div className="fish-empty-icon">🔬</div>

            <h4>Insufficient Data</h4>

            <p>
              There is not enough water quality information to provide a fish
              compatibility recommendation.
            </p>
          </div>
        )}

      {/* Disclaimer */}
      <div className="fish-disclaimer">
        <span>ⓘ</span>

        <p>
          This recommendation is based on the measured and predicted
          water-quality parameters. Additional factors such as ammonia,
          nitrite, nitrate, salinity and species-specific requirements should
          also be considered before introducing fish.
        </p>
      </div>
    </section>
  );
}

export default FishCompatibility;