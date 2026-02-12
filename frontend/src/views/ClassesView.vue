<template>
  <div class="classes-page">
    <div class="page-header">
      <h2>Class Schedule</h2>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ New Class' }}
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showForm" class="card form-card">
      <h3>Create New Class</h3>
      <form @submit.prevent="createClass">
        <div class="form-grid">
          <div class="form-group">
            <label>Name</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>Instructor</label>
            <input v-model="form.instructor" required />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="form.category" required>
              <option value="yoga">Yoga</option>
              <option value="hiit">HIIT</option>
              <option value="strength">Strength</option>
              <option value="cardio">Cardio</option>
              <option value="pilates">Pilates</option>
            </select>
          </div>
          <div class="form-group">
            <label>Location</label>
            <input v-model="form.location" />
          </div>
          <div class="form-group">
            <label>Day</label>
            <select v-model="form.schedule.day_of_week" required>
              <option :value="0">Monday</option>
              <option :value="1">Tuesday</option>
              <option :value="2">Wednesday</option>
              <option :value="3">Thursday</option>
              <option :value="4">Friday</option>
              <option :value="5">Saturday</option>
              <option :value="6">Sunday</option>
            </select>
          </div>
          <div class="form-group">
            <label>Capacity</label>
            <input v-model.number="form.capacity" type="number" min="1" required />
          </div>
          <div class="form-group">
            <label>Start Time</label>
            <input v-model="form.schedule.start_time" type="time" required />
          </div>
          <div class="form-group">
            <label>End Time</label>
            <input v-model="form.schedule.end_time" type="time" required />
          </div>
        </div>
        <div class="form-group" style="margin-top: 16px">
          <label>Description</label>
          <textarea v-model="form.description" rows="2"></textarea>
        </div>
        <button type="submit" class="btn btn-primary" style="margin-top: 16px">Save Class</button>
      </form>
    </div>

    <!-- Filters -->
    <div class="card filters">
      <select v-model="filterCategory" @change="fetchClasses">
        <option value="">All Categories</option>
        <option value="yoga">Yoga</option>
        <option value="hiit">HIIT</option>
        <option value="strength">Strength</option>
        <option value="cardio">Cardio</option>
        <option value="pilates">Pilates</option>
      </select>
      <select v-model="filterDay" @change="fetchClasses">
        <option value="">All Days</option>
        <option value="0">Monday</option>
        <option value="1">Tuesday</option>
        <option value="2">Wednesday</option>
        <option value="3">Thursday</option>
        <option value="4">Friday</option>
        <option value="5">Saturday</option>
        <option value="6">Sunday</option>
      </select>
    </div>

    <!-- Class Cards -->
    <div class="classes-grid">
      <div v-for="cls in classes" :key="cls.id" class="card class-card">
        <div class="class-header">
          <h3>{{ cls.name }}</h3>
          <span :class="`badge badge-${cls.status === 'scheduled' ? 'active' : 'expired'}`">
            {{ cls.status }}
          </span>
        </div>
        <p class="class-desc">{{ cls.description }}</p>
        <div class="class-meta">
          <span>{{ cls.instructor }}</span>
          <span>{{ days[cls.schedule.day_of_week] }} {{ cls.schedule.start_time }}-{{ cls.schedule.end_time }}</span>
          <span>{{ cls.location }}</span>
        </div>
        <div class="class-capacity">
          <div class="capacity-bar">
            <div
              class="capacity-fill"
              :style="{ width: `${(cls.current_bookings / cls.capacity) * 100}%` }"
              :class="{ full: cls.current_bookings >= cls.capacity }"
            ></div>
          </div>
          <span>{{ cls.current_bookings }}/{{ cls.capacity }} spots</span>
        </div>
        <div class="class-actions">
          <button class="btn btn-danger btn-sm" @click="cancelClass(cls.id)">Cancel</button>
        </div>
      </div>
    </div>

    <div v-if="classes.length === 0" class="card empty-state">
      No classes found
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { classApi } from '../services/api'

const classes = ref([])
const showForm = ref(false)
const filterCategory = ref('')
const filterDay = ref('')

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const form = ref({
  name: '',
  description: '',
  instructor: '',
  category: 'yoga',
  location: 'Main Floor',
  capacity: 20,
  schedule: { day_of_week: 0, start_time: '09:00', end_time: '10:00', recurring: true },
})

async function fetchClasses() {
  try {
    const params = {}
    if (filterCategory.value) params.category = filterCategory.value
    if (filterDay.value !== '') params.day_of_week = parseInt(filterDay.value)
    const { data } = await classApi.list(params)
    classes.value = data.items
  } catch (e) {
    console.error('Failed to fetch classes:', e)
  }
}

async function createClass() {
  try {
    await classApi.create(form.value)
    showForm.value = false
    form.value = {
      name: '', description: '', instructor: '', category: 'yoga',
      location: 'Main Floor', capacity: 20,
      schedule: { day_of_week: 0, start_time: '09:00', end_time: '10:00', recurring: true },
    }
    await fetchClasses()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to create class')
  }
}

async function cancelClass(id) {
  if (!confirm('Cancel this class?')) return
  try {
    await classApi.delete(id)
    await fetchClasses()
  } catch (e) {
    alert('Failed to cancel class')
  }
}

onMounted(fetchClasses)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-card { margin-bottom: 24px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #636e72;
  margin-bottom: 4px;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.class-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-desc {
  font-size: 14px;
  color: #636e72;
}

.class-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #636e72;
}

.capacity-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.capacity-fill {
  height: 100%;
  background: #00b894;
  border-radius: 4px;
  transition: width 0.3s;
}

.capacity-fill.full {
  background: #e17055;
}

.class-capacity span {
  font-size: 12px;
  color: #636e72;
}

.class-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #636e72;
}

h3 { font-size: 16px; font-weight: 600; }
.btn-sm { padding: 4px 10px; font-size: 12px; }
</style>
