<template>
  <nav class="sidebar">
    <div class="sidebar-header">
      <h1 class="logo">FitHub</h1>
      <p class="logo-sub">Gym Management</p>
    </div>

    <ul class="nav-links">
      <li v-for="item in navItems" :key="item.path">
        <router-link :to="item.path" class="nav-link" active-class="active">
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </li>
    </ul>

    <div class="sidebar-footer">
      <p>v1.0.0</p>
    </div>
  </nav>
</template>

<script setup>
const navItems = [
  { path: '/', icon: '📊', label: 'Dashboard' },
  { path: '/members', icon: '👥', label: 'Members' },
  { path: '/classes', icon: '📅', label: 'Classes' },
  { path: '/workouts', icon: '💪', label: 'Workouts' },
  { path: '/exercise-tracker', icon: '🤖', label: 'AI Tracker' },
  { path: '/analytics', icon: '📈', label: 'Analytics' },
]
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background: #1a1a2e;
  color: white;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 24px;
  font-weight: 700;
  color: #6c5ce7;
}

.logo-sub {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.nav-links {
  list-style: none;
  padding: 16px 0;
  flex: 1;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.2s;
  gap: 12px;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav-link.active {
  background: rgba(108, 92, 231, 0.2);
  color: #6c5ce7;
  border-right: 3px solid #6c5ce7;
}

.nav-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}
</style>
