import { ref, onUnmounted } from 'vue'

export function useExerciseSocket() {
  const ws = ref(null)
  const isConnected = ref(false)
  const state = ref('IDLE')
  const repCount = ref(0)
  const avgFormScore = ref(null)
  const lastRepScore = ref(null)
  const feedback = ref([])
  const angles = ref({})
  const landmarks = ref(null)
  const error = ref(null)

  function connect(exerciseType, memberId = 'anonymous') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/exercise/${exerciseType}?member_id=${memberId}`

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      isConnected.value = true
      error.value = null
    }

    ws.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)

        if (data.error) {
          error.value = data.error
          return
        }

        state.value = data.state
        repCount.value = data.rep_count
        avgFormScore.value = data.avg_form_score
        feedback.value = data.feedback || []
        angles.value = data.angles || {}
        landmarks.value = data.landmarks || null

        if (data.completed_rep && data.rep_score !== null) {
          lastRepScore.value = data.rep_score
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.value.onclose = () => {
      isConnected.value = false
    }

    ws.value.onerror = () => {
      error.value = 'WebSocket connection failed'
      isConnected.value = false
    }
  }

  function sendFrame(base64Frame) {
    if (ws.value && ws.value.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify({ frame: base64Frame }))
    }
  }

  function disconnect() {
    if (ws.value) {
      ws.value.close()
      ws.value = null
    }
    isConnected.value = false
  }

  function reset() {
    state.value = 'IDLE'
    repCount.value = 0
    avgFormScore.value = null
    lastRepScore.value = null
    feedback.value = []
    angles.value = {}
    landmarks.value = null
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    state,
    repCount,
    avgFormScore,
    lastRepScore,
    feedback,
    angles,
    landmarks,
    error,
    connect,
    sendFrame,
    disconnect,
    reset,
  }
}
