<template>
  <div class="tracker-page">
    <div class="page-header">
      <h2>AI Exercise Tracker</h2>
    </div>

    <div class="card">
      <p class="info-text">
        This module uses AI-powered pose estimation to track exercise form in real-time.
        Select an exercise and start a session to begin tracking via WebSocket connection.
      </p>
      <p class="info-text" style="margin-top: 8px; color: #636e72;">
        Available in Module 2 — MediaPipe pose engine, state machine, and WebSocket integration.
      </p>

      <div class="tracker-preview">
        <div class="preview-box">
          <div class="placeholder-cam">
            <span>Webcam Feed + Pose Overlay</span>
            <p>Module 2</p>
          </div>
        </div>
        <div class="preview-stats">
          <div class="stat-item">
            <label>Exercise</label>
            <select disabled>
              <option>Squat</option>
              <option>Bicep Curl</option>
              <option>Shoulder Press</option>
            </select>
          </div>
          <div class="stat-item">
            <label>Rep Count</label>
            <div class="big-number">0</div>
          </div>
          <div class="stat-item">
            <label>Form Score</label>
            <div class="big-number">--</div>
          </div>
          <div class="stat-item">
            <label>State</label>
            <div class="state-badge">IDLE</div>
          </div>
          <div class="stat-item">
            <label>Duration</label>
            <div class="big-number">0:00</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.info-text {
  font-size: 14px;
  color: #2d3436;
  line-height: 1.6;
}

.tracker-preview {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-top: 24px;
}

.placeholder-cam {
  background: #1a1a2e;
  border-radius: 12px;
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 18px;
}

.placeholder-cam p {
  margin-top: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.3);
}

.preview-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item label {
  font-size: 12px;
  font-weight: 600;
  color: #636e72;
  text-transform: uppercase;
  display: block;
  margin-bottom: 4px;
}

.big-number {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a2e;
}

.state-badge {
  display: inline-block;
  padding: 4px 12px;
  background: #dfe6e9;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
}
</style>
