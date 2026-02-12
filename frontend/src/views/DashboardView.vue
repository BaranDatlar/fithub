<template>
  <div class="dashboard">
    <div class="stats-grid">
      <StatCard icon="👥" :value="overview.active_members" label="Active Members" color="#6c5ce7" />
      <StatCard icon="📅" :value="overview.classes_this_week" label="Classes This Week" color="#00b894" />
      <StatCard icon="💪" :value="overview.total_workouts_logged" label="Workouts Logged" color="#fdcb6e" />
      <StatCard icon="🤖" :value="overview.ai_sessions_this_month" label="AI Sessions" color="#e17055" />
    </div>

    <div class="dashboard-grid">
      <div class="card">
        <h3>Overview</h3>
        <div class="overview-list">
          <div class="overview-item">
            <span>Total Members</span>
            <strong>{{ overview.total_members }}</strong>
          </div>
          <div class="overview-item">
            <span>New This Month</span>
            <strong>{{ overview.new_members_this_month }}</strong>
          </div>
          <div class="overview-item">
            <span>Avg Class Attendance</span>
            <strong>{{ (overview.avg_class_attendance * 100).toFixed(0) }}%</strong>
          </div>
          <div class="overview-item">
            <span>Most Popular Class</span>
            <strong>{{ overview.most_popular_class || 'N/A' }}</strong>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Quick Actions</h3>
        <div class="actions">
          <router-link to="/members" class="btn btn-primary">Manage Members</router-link>
          <router-link to="/classes" class="btn btn-primary">View Classes</router-link>
          <router-link to="/workouts" class="btn btn-primary">Workout Plans</router-link>
          <router-link to="/exercise-tracker" class="btn btn-primary">AI Tracker</router-link>
        </div>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { analyticsApi } from '../services/api'
import StatCard from '../components/analytics/StatCard.vue'

const overview = ref({
  total_members: 0,
  active_members: 0,
  new_members_this_month: 0,
  classes_this_week: 0,
  avg_class_attendance: 0,
  most_popular_class: null,
  total_workouts_logged: 0,
  ai_sessions_this_month: 0,
})
const error = ref(null)

onMounted(async () => {
  try {
    const { data } = await analyticsApi.getOverview()
    overview.value = data
  } catch (e) {
    error.value = 'Failed to load dashboard data'
  }
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.overview-list {
  margin-top: 16px;
}

.overview-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.overview-item span {
  color: #636e72;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.actions .btn {
  text-align: center;
  text-decoration: none;
}

.error {
  color: #e17055;
  margin-top: 16px;
}

h3 {
  font-size: 16px;
  font-weight: 600;
}
</style>
