<template>
  <div class="tracker-page">
    <div class="page-header">
      <h2>AI Exercise Tracker</h2>
      <p class="subtitle">Real-time pose estimation with form analysis</p>
    </div>

    <div class="tracker-layout">
      <!-- Video Feed -->
      <div class="video-section card">
        <div class="video-container">
          <video
            ref="videoElement"
            autoplay
            playsinline
            muted
            :class="{ active: webcam.isActive.value }"
          />
          <canvas ref="overlayCanvas" class="pose-overlay" />

          <!-- Idle overlay -->
          <div v-if="!webcam.isActive.value" class="video-placeholder">
            <div class="placeholder-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                <circle cx="12" cy="13" r="4"/>
              </svg>
            </div>
            <span>Select an exercise and click Start to begin</span>
          </div>

          <!-- State indicator overlay -->
          <div v-if="webcam.isActive.value" class="state-overlay">
            <span class="state-pill" :class="stateClass">{{ socket.state.value }}</span>
          </div>

          <!-- Feedback overlay -->
          <div v-if="socket.feedback.value.length" class="feedback-overlay">
            <div
              v-for="(msg, i) in socket.feedback.value"
              :key="i"
              class="feedback-msg"
            >
              {{ msg }}
            </div>
          </div>

          <!-- Rep flash overlay -->
          <transition name="flash">
            <div v-if="showRepFlash" class="rep-flash">
              <div class="flash-content">
                <span class="flash-rep">Rep {{ socket.repCount.value }}</span>
                <span class="flash-score" :class="scoreClass(socket.lastRepScore.value)">
                  {{ socket.lastRepScore.value?.toFixed(0) }}
                </span>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Control Panel -->
      <div class="control-section">
        <!-- Exercise Selector -->
        <div class="card control-card">
          <label class="control-label">Exercise</label>
          <div class="exercise-options">
            <button
              v-for="ex in exercises"
              :key="ex.name"
              :class="['exercise-btn', { active: selectedExercise === ex.name }]"
              :disabled="isSessionActive"
              @click="selectedExercise = ex.name"
            >
              <span class="exercise-icon">{{ ex.icon }}</span>
              <span>{{ ex.displayName }}</span>
            </button>
          </div>
        </div>

        <!-- Session Controls -->
        <div class="card control-card">
          <button
            v-if="!isSessionActive"
            class="btn btn-start"
            @click="startSession"
          >
            Start Session
          </button>
          <button
            v-else
            class="btn btn-stop"
            @click="stopSession"
          >
            End Session
          </button>
        </div>

        <!-- Live Stats -->
        <div class="card control-card stats-card">
          <div class="stat-row">
            <label>Reps</label>
            <div class="stat-value big">{{ socket.repCount.value }}</div>
          </div>
          <div class="stat-row">
            <label>Avg Form</label>
            <div class="stat-value" :class="scoreClass(socket.avgFormScore.value)">
              {{ socket.avgFormScore.value ? socket.avgFormScore.value.toFixed(1) + '%' : '--' }}
            </div>
          </div>
          <div class="stat-row">
            <label>Last Rep</label>
            <div class="stat-value" :class="scoreClass(socket.lastRepScore.value)">
              {{ socket.lastRepScore.value ? socket.lastRepScore.value.toFixed(1) + '%' : '--' }}
            </div>
          </div>
          <div class="stat-row">
            <label>Duration</label>
            <div class="stat-value">{{ formattedDuration }}</div>
          </div>
        </div>

        <!-- Angle Debug -->
        <div v-if="isSessionActive && Object.keys(socket.angles.value).length" class="card control-card">
          <label class="control-label">Joint Angles</label>
          <div class="angle-list">
            <div
              v-for="(val, key) in socket.angles.value"
              :key="key"
              class="angle-item"
            >
              <span class="angle-name">{{ formatAngleName(key) }}</span>
              <span class="angle-val">{{ val ? val.toFixed(1) + '°' : '--' }}</span>
            </div>
          </div>
        </div>

        <!-- Session History -->
        <div v-if="sessionHistory.length" class="card control-card">
          <label class="control-label">Recent Sessions</label>
          <div class="history-list">
            <div
              v-for="session in sessionHistory"
              :key="session.id"
              class="history-item"
            >
              <span class="hist-exercise">{{ session.exercise }}</span>
              <span class="hist-reps">{{ session.total_reps }} reps</span>
              <span class="hist-score" :class="scoreClass(session.avg_form_score)">
                {{ session.avg_form_score ? session.avg_form_score.toFixed(0) + '%' : '--' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Error display -->
        <div v-if="webcam.error.value || socket.error.value" class="card control-card error-card">
          <p>{{ webcam.error.value || socket.error.value }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import { useWebcam } from '../composables/useWebcam'
import { useExerciseSocket } from '../composables/useExerciseSocket'
import { exerciseApi } from '../services/api'

const webcam = useWebcam()
const socket = useExerciseSocket()

const videoElement = ref(null)
const overlayCanvas = ref(null)
const selectedExercise = ref('squat')
const isSessionActive = ref(false)
const sessionDuration = ref(0)
const showRepFlash = ref(false)
const sessionHistory = ref([])

let frameInterval = null
let durationInterval = null

const exercises = [
  { name: 'squat', displayName: 'Squat', icon: '🏋️' },
  { name: 'bicep_curl', displayName: 'Bicep Curl', icon: '💪' },
  { name: 'shoulder_press', displayName: 'Shoulder Press', icon: '🙌' },
]

const formattedDuration = computed(() => {
  const mins = Math.floor(sessionDuration.value / 60)
  const secs = sessionDuration.value % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
})

const stateClass = computed(() => {
  const s = socket.state.value
  if (s === 'DOWN') return 'state-down'
  if (s === 'UP') return 'state-up'
  if (s === 'GOING_DOWN' || s === 'GOING_UP') return 'state-moving'
  return 'state-idle'
})

function scoreClass(score) {
  if (!score) return ''
  if (score >= 85) return 'score-good'
  if (score >= 65) return 'score-ok'
  return 'score-bad'
}

function formatAngleName(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

async function startSession() {
  // Assign video element to composable
  webcam.videoRef.value = videoElement.value

  await webcam.start()
  if (!webcam.isActive.value) return

  // Wait for video to be ready
  await nextTick()

  socket.reset()
  socket.connect(selectedExercise.value)

  isSessionActive.value = true
  sessionDuration.value = 0

  // Send frames at ~10 FPS
  frameInterval = setInterval(() => {
    const frame = webcam.captureFrame()
    if (frame) {
      socket.sendFrame(frame)
    }
  }, 100)

  // Duration timer
  durationInterval = setInterval(() => {
    sessionDuration.value++
  }, 1000)
}

function stopSession() {
  if (frameInterval) {
    clearInterval(frameInterval)
    frameInterval = null
  }
  if (durationInterval) {
    clearInterval(durationInterval)
    durationInterval = null
  }

  socket.disconnect()
  webcam.stop()
  isSessionActive.value = false

  loadHistory()
}

// Flash on rep completion
watch(() => socket.repCount.value, (newVal, oldVal) => {
  if (newVal > oldVal) {
    showRepFlash.value = true
    setTimeout(() => {
      showRepFlash.value = false
    }, 1200)
  }
})

// Draw pose landmarks on overlay canvas
watch(() => socket.landmarks.value, (lm) => {
  if (!overlayCanvas.value || !lm) return
  const canvas = overlayCanvas.value
  const video = videoElement.value
  if (!video) return

  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  // Draw landmark dots
  ctx.fillStyle = '#00b894'
  for (const [, point] of Object.entries(lm)) {
    if (point.visibility > 0.5) {
      const x = point.x * canvas.width
      const y = point.y * canvas.height
      ctx.beginPath()
      ctx.arc(x, y, 5, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // Draw skeleton connections
  const connections = [
    ['LEFT_SHOULDER', 'LEFT_ELBOW'],
    ['LEFT_ELBOW', 'LEFT_WRIST'],
    ['RIGHT_SHOULDER', 'RIGHT_ELBOW'],
    ['RIGHT_ELBOW', 'RIGHT_WRIST'],
    ['LEFT_SHOULDER', 'RIGHT_SHOULDER'],
    ['LEFT_SHOULDER', 'LEFT_HIP'],
    ['RIGHT_SHOULDER', 'RIGHT_HIP'],
    ['LEFT_HIP', 'RIGHT_HIP'],
    ['LEFT_HIP', 'LEFT_KNEE'],
    ['LEFT_KNEE', 'LEFT_ANKLE'],
    ['RIGHT_HIP', 'RIGHT_KNEE'],
    ['RIGHT_KNEE', 'RIGHT_ANKLE'],
  ]

  ctx.strokeStyle = '#00cec9'
  ctx.lineWidth = 2
  for (const [a, b] of connections) {
    if (lm[a] && lm[b] && lm[a].visibility > 0.5 && lm[b].visibility > 0.5) {
      ctx.beginPath()
      ctx.moveTo(lm[a].x * canvas.width, lm[a].y * canvas.height)
      ctx.lineTo(lm[b].x * canvas.width, lm[b].y * canvas.height)
      ctx.stroke()
    }
  }
})

async function loadHistory() {
  try {
    const { data } = await exerciseApi.listSessions({ limit: 5 })
    sessionHistory.value = data.items || []
  } catch {
    // API may not be available
  }
}

onUnmounted(() => {
  if (frameInterval) clearInterval(frameInterval)
  if (durationInterval) clearInterval(durationInterval)
})

loadHistory()
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.subtitle {
  color: #636e72;
  font-size: 14px;
  margin-top: 4px;
}

.tracker-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  align-items: start;
}

/* Video Section */
.video-section {
  padding: 0;
  overflow: hidden;
}

.video-container {
  position: relative;
  background: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 4 / 3;
}

.video-container video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transform: scaleX(-1);
}

.pose-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transform: scaleX(-1);
}

.video-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

.placeholder-icon {
  color: rgba(255, 255, 255, 0.3);
}

/* State overlay */
.state-overlay {
  position: absolute;
  top: 12px;
  left: 12px;
}

.state-pill {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.state-idle { background: rgba(99, 110, 114, 0.8); color: #fff; }
.state-moving { background: rgba(0, 184, 148, 0.85); color: #fff; }
.state-down { background: rgba(253, 203, 110, 0.9); color: #2d3436; }
.state-up { background: rgba(108, 92, 231, 0.85); color: #fff; }

/* Feedback overlay */
.feedback-overlay {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: center;
}

.feedback-msg {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 8px 20px;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  backdrop-filter: blur(8px);
}

/* Rep flash */
.rep-flash {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(108, 92, 231, 0.15);
  pointer-events: none;
}

.flash-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.flash-rep {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
}

.flash-score {
  font-size: 20px;
  font-weight: 700;
  padding: 4px 16px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
}

.flash-enter-active { transition: all 0.2s ease-out; }
.flash-leave-active { transition: all 0.8s ease-in; }
.flash-enter-from { opacity: 0; transform: scale(0.8); }
.flash-leave-to { opacity: 0; }

/* Control Section */
.control-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.control-card {
  padding: 16px;
}

.control-label {
  display: block;
  font-size: 11px;
  font-weight: 700;
  color: #636e72;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

/* Exercise buttons */
.exercise-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.exercise-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 2px solid #dfe6e9;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #2d3436;
  transition: all 0.15s;
}

.exercise-btn:hover:not(:disabled) {
  border-color: #6c5ce7;
  background: #f8f7ff;
}

.exercise-btn.active {
  border-color: #6c5ce7;
  background: #6c5ce7;
  color: #fff;
}

.exercise-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.exercise-icon {
  font-size: 20px;
}

/* Session buttons */
.btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-start {
  background: #00b894;
  color: #fff;
}

.btn-start:hover {
  background: #00a884;
}

.btn-stop {
  background: #e17055;
  color: #fff;
}

.btn-stop:hover {
  background: #d15643;
}

/* Stats */
.stats-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-row label {
  font-size: 12px;
  font-weight: 600;
  color: #636e72;
  text-transform: uppercase;
}

.stat-value {
  font-size: 22px;
  font-weight: 800;
  color: #1a1a2e;
}

.stat-value.big {
  font-size: 28px;
}

.score-good { color: #00b894; }
.score-ok { color: #fdcb6e; }
.score-bad { color: #e17055; }

/* Angle debug */
.angle-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.angle-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.angle-name {
  color: #636e72;
}

.angle-val {
  font-weight: 600;
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: #2d3436;
}

/* History */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f1f2f6;
  font-size: 13px;
}

.history-item:last-child {
  border-bottom: none;
}

.hist-exercise {
  font-weight: 600;
  color: #2d3436;
  text-transform: capitalize;
}

.hist-reps {
  color: #636e72;
}

.hist-score {
  font-weight: 700;
}

/* Error */
.error-card {
  background: #fff5f5;
  border-left: 3px solid #e17055;
}

.error-card p {
  color: #e17055;
  font-size: 13px;
  margin: 0;
}

@media (max-width: 900px) {
  .tracker-layout {
    grid-template-columns: 1fr;
  }
}
</style>
