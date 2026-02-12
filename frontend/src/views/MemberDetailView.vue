<template>
  <div class="member-detail" v-if="member">
    <div class="page-header">
      <div>
        <router-link to="/members" class="back-link">← Back to Members</router-link>
        <h2>{{ member.first_name }} {{ member.last_name }}</h2>
      </div>
    </div>

    <div class="detail-grid">
      <!-- Profile Card -->
      <div class="card">
        <h3>Profile</h3>
        <div class="profile-info">
          <div class="info-row">
            <span>Email</span>
            <strong>{{ member.email }}</strong>
          </div>
          <div class="info-row">
            <span>Phone</span>
            <strong>{{ member.phone || 'N/A' }}</strong>
          </div>
          <div class="info-row">
            <span>Plan</span>
            <span :class="`badge badge-${member.membership.plan}`">{{ member.membership.plan }}</span>
          </div>
          <div class="info-row">
            <span>Status</span>
            <span :class="`badge badge-${member.membership.status}`">{{ member.membership.status }}</span>
          </div>
          <div class="info-row">
            <span>Fitness Level</span>
            <strong>{{ member.profile.fitness_level }}</strong>
          </div>
          <div class="info-row">
            <span>Joined</span>
            <strong>{{ new Date(member.created_at).toLocaleDateString() }}</strong>
          </div>
        </div>
      </div>

      <!-- Stats Card -->
      <div class="card">
        <h3>Statistics</h3>
        <div class="stats-list">
          <div class="stat-row">
            <span>Total Workouts</span>
            <strong>{{ stats.total_workouts }}</strong>
          </div>
          <div class="stat-row">
            <span>Classes Attended</span>
            <strong>{{ stats.total_classes_attended }}</strong>
          </div>
          <div class="stat-row">
            <span>Avg Form Score</span>
            <strong>{{ stats.avg_form_score ? stats.avg_form_score + '/100' : 'N/A' }}</strong>
          </div>
          <div class="stat-row">
            <span>Last Activity</span>
            <strong>{{ stats.last_activity ? new Date(stats.last_activity).toLocaleDateString() : 'Never' }}</strong>
          </div>
        </div>
      </div>

      <!-- Workout Logs -->
      <div class="card full-width">
        <h3>Recent Workout Logs</h3>
        <table v-if="logs.length > 0">
          <thead>
            <tr>
              <th>Date</th>
              <th>Duration</th>
              <th>Exercises</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td>{{ new Date(log.completed_at).toLocaleDateString() }}</td>
              <td>{{ log.duration_minutes }} min</td>
              <td>{{ log.exercises_completed.map(e => e.exercise_name).join(', ') }}</td>
              <td><span :class="`badge badge-${log.source === 'ai_tracker' ? 'premium' : 'basic'}`">{{ log.source }}</span></td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-state">No workout logs yet</p>
      </div>
    </div>
  </div>
  <div v-else class="loading">Loading...</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { memberApi, workoutApi } from '../services/api'

const route = useRoute()
const member = ref(null)
const stats = ref({ total_workouts: 0, total_classes_attended: 0, avg_form_score: null, last_activity: null })
const logs = ref([])

onMounted(async () => {
  const id = route.params.id
  try {
    const [memberRes, statsRes, logsRes] = await Promise.all([
      memberApi.get(id),
      memberApi.getStats(id),
      workoutApi.getMemberLogs(id),
    ])
    member.value = memberRes.data
    stats.value = statsRes.data
    logs.value = logsRes.data
  } catch (e) {
    console.error('Failed to load member:', e)
  }
})
</script>

<style scoped>
.back-link {
  color: #6c5ce7;
  text-decoration: none;
  font-size: 14px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.full-width {
  grid-column: 1 / -1;
}

.info-row, .stat-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row span:first-child, .stat-row span:first-child {
  color: #636e72;
}

.empty-state {
  text-align: center;
  padding: 24px;
  color: #636e72;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #636e72;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin-top: 8px;
}

h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}
</style>
