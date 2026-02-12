<template>
  <div class="stat-card" :style="{ borderLeft: `4px solid ${color}` }">
    <div class="stat-icon">{{ icon }}</div>
    <div class="stat-info">
      <p class="stat-value">{{ value }}</p>
      <p class="stat-label">{{ label }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📊' },
  value: { type: [String, Number], default: 0 },
  label: { type: String, default: '' },
  color: { type: String, default: '#6c5ce7' },
})
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
}

.stat-label {
  font-size: 13px;
  color: #636e72;
  margin-top: 2px;
}
</style>
