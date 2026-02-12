import { ref, onUnmounted } from 'vue'

export function useWebcam() {
  const videoRef = ref(null)
  const stream = ref(null)
  const isActive = ref(false)
  const error = ref(null)

  async function start() {
    try {
      error.value = null
      stream.value = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' },
        audio: false,
      })
      if (videoRef.value) {
        videoRef.value.srcObject = stream.value
      }
      isActive.value = true
    } catch (err) {
      error.value = err.message || 'Camera access denied'
      isActive.value = false
    }
  }

  function stop() {
    if (stream.value) {
      stream.value.getTracks().forEach((track) => track.stop())
      stream.value = null
    }
    if (videoRef.value) {
      videoRef.value.srcObject = null
    }
    isActive.value = false
  }

  function captureFrame() {
    if (!videoRef.value || !isActive.value) return null

    const canvas = document.createElement('canvas')
    canvas.width = videoRef.value.videoWidth || 640
    canvas.height = videoRef.value.videoHeight || 480

    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoRef.value, 0, 0, canvas.width, canvas.height)

    // Return base64 JPEG (strip the data:image/jpeg;base64, prefix)
    const dataUrl = canvas.toDataURL('image/jpeg', 0.7)
    return dataUrl.split(',')[1]
  }

  onUnmounted(() => {
    stop()
  })

  return { videoRef, isActive, error, start, stop, captureFrame }
}
