// POST /api/tests/start
// The actual sampling + evaluation happens client-side in Prediction.jsx
// (it polls /api/data on its own timer). This just gives the frontend a
// fast ack + a testId it can optionally tag the finished report with —
// no point blocking the request on a full sampling loop the client
// isn't waiting for.
function startTest(req, res) {
    const testId = `test_${Date.now()}`;
    res.json({ success: true, testId, startedAt: new Date().toISOString() });
}

export { startTest };