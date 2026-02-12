<template>
  <div class="app-layout">
    <Sidebar />
    <div class="main-content">
      <TopBar />
      <div class="page-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import Sidebar from './components/layout/Sidebar.vue'
import TopBar from './components/layout/TopBar.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, sans-serif;
  background-color: #f5f7fa;
  color: #1a1a2e;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
}

.page-content {
  padding: 24px;
  flex: 1;
}

/* Utility classes */
.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #6c5ce7;
  color: white;
}

.btn-primary:hover {
  background: #5a4bd1;
}

.btn-danger {
  background: #ff6b6b;
  color: white;
}

.btn-danger:hover {
  background: #ee5a5a;
}

.btn-secondary {
  background: #dfe6e9;
  color: #2d3436;
}

.btn-secondary:hover {
  background: #b2bec3;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  font-weight: 600;
  color: #636e72;
  font-size: 13px;
  text-transform: uppercase;
}

input, select, textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #6c5ce7;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-active { background: #d4edda; color: #155724; }
.badge-frozen { background: #cce5ff; color: #004085; }
.badge-expired { background: #f8d7da; color: #721c24; }
.badge-basic { background: #e2e3e5; color: #383d41; }
.badge-premium { background: #fff3cd; color: #856404; }
.badge-pt { background: #d4edda; color: #155724; }
</style>
