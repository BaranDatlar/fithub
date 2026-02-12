<template>
  <div class="analytics-page">
    <div class="page-header">
      <h2>Analytics</h2>
    </div>

    <!-- Member Analytics -->
    <div class="section">
      <h3>Member Analytics</h3>
      <div class="stats-grid">
        <StatCard icon="👥" :value="memberStats.total" label="Total Members" color="#6c5ce7" />
        <StatCard icon="✅" :value="memberStats.active" label="Active" color="#00b894" />
        <StatCard icon="❄️" :value="memberStats.frozen" label="Frozen" color="#74b9ff" />
        <StatCard icon="⏰" :value="memberStats.expired" label="Expired" color="#e17055" />
      </div>

      <div class="card" style="margin-top: 16px">
        <h4>Members by Plan</h4>
        <div class="plan-bars">
          <div v-for="(count, plan) in memberStats.by_plan" :key="plan" class="plan-bar-item">
            <span class="plan-label">{{ plan }}</span>
            <div class="plan-bar">
              <div class="plan-bar-fill" :style="{ width: barWidth(count) }"></div>
            </div>
            <span class="plan-count">{{ count }}</span>
          </div>
        </div>
        <p class="growth-rate">
          Growth rate: <strong>{{ memberStats.growth_rate }}%</strong> vs last month
        </p>
      </div>
    </div>

    <!-- Class Analytics -->
    <div class="section">
      <h3>Class Analytics</h3>
      <div class="stats-grid">
        <StatCard icon="📅" :value="classStats.total_classes" label="Total Classes" color="#6c5ce7" />
        <StatCard icon="📊" :value="(classStats.avg_attendance_rate * 100).toFixed(0) + '%'" label="Avg Attendance" color="#00b894" />
        <StatCard icon="🎫" :value="classStats.total_bookings" label="Total Bookings" color="#fdcb6e" />
        <StatCard icon="⭐" :value="classStats.most_popular || 'N/A'" label="Most Popular" color="#e17055" />
      </div>

      <div class="card" style="margin-top: 16px">
        <h4>Classes by Category</h4>
        <div class="plan-bars">
          <div v-for="(count, cat) in classStats.by_category" :key="cat" class="plan-bar-item">
            <span class="plan-label">{{ cat }}</span>
            <div class="plan-bar">
              <div class="plan-bar-fill" :style="{ width: barWidth(count), background: '#00b894' }"></div>
            </div>
            <span class="plan-count">{{ count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Revenue -->
    <div class="section">
      <h3>Revenue Estimate</h3>
      <div class="card">
        <div class="revenue-total">
          <span>Estimated Monthly Revenue</span>
          <strong>${{ revenue.estimated_monthly?.toFixed(2) || '0.00' }}</strong>
        </div>
        <div class="plan-bars" style="margin-top: 16px">
          <div v-for="(count, plan) in revenue.total_members_by_plan" :key="plan" class="plan-bar-item">
            <span class="plan-label">{{ plan }} (${{ planPrices[plan] || 0 }}/mo)</span>
            <span class="plan-count">{{ count }} members</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { analyticsApi } from '../services/api'
import StatCard from '../components/analytics/StatCard.vue'

const memberStats = ref({ total: 0, active: 0, frozen: 0, expired: 0, by_plan: {}, growth_rate: 0 })
const classStats = ref({ total_classes: 0, avg_attendance_rate: 0, by_category: {}, most_popular: null, total_bookings: 0 })
const revenue = ref({ total_members_by_plan: {}, estimated_monthly: 0 })

const planPrices = { basic: 29.99, premium: 49.99, pt: 89.99 }

function barWidth(count) {
  const max = Math.max(...Object.values(memberStats.value.by_plan || {}), 1)
  return `${(count / max) * 100}%`
}

onMounted(async () => {
  try {
    const [memberRes, classRes, revenueRes] = await Promise.all([
      analyticsApi.getMembers(),
      analyticsApi.getClasses(),
      analyticsApi.getRevenue(),
    ])
    memberStats.value = memberRes.data
    classStats.value = classRes.data
    revenue.value = revenueRes.data
  } catch (e) {
    console.error('Failed to load analytics:', e)
  }
})
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}

.section {
  margin-bottom: 32px;
}

.section h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
}

.plan-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.plan-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plan-label {
  width: 160px;
  font-size: 13px;
  font-weight: 500;
  text-transform: capitalize;
}

.plan-bar {
  flex: 1;
  height: 24px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.plan-bar-fill {
  height: 100%;
  background: #6c5ce7;
  border-radius: 4px;
  transition: width 0.3s;
}

.plan-count {
  font-size: 14px;
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

.growth-rate {
  margin-top: 12px;
  font-size: 14px;
  color: #636e72;
}

.revenue-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
}

.revenue-total strong {
  font-size: 28px;
  color: #00b894;
}
</style>
