<template>
  <div class="workouts-page">
    <div class="page-header">
      <h2>Workout Plans</h2>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ New Plan' }}
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showForm" class="card form-card">
      <h3>Create Workout Plan</h3>
      <form @submit.prevent="createPlan">
        <div class="form-grid">
          <div class="form-group">
            <label>Plan Name</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>Difficulty</label>
            <select v-model="form.difficulty">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div class="form-group">
            <label>Duration (minutes)</label>
            <input v-model.number="form.estimated_duration_minutes" type="number" min="1" required />
          </div>
          <div class="form-group">
            <label>Created By</label>
            <input v-model="form.created_by" required />
          </div>
        </div>
        <div class="form-group" style="margin-top: 16px">
          <label>Description</label>
          <textarea v-model="form.description" rows="2"></textarea>
        </div>

        <h4 style="margin-top: 16px">Exercises</h4>
        <div v-for="(ex, idx) in form.exercises" :key="idx" class="exercise-row">
          <input v-model="ex.name" placeholder="Exercise name" required />
          <input v-model.number="ex.sets" type="number" placeholder="Sets" min="1" required />
          <input v-model.number="ex.reps" type="number" placeholder="Reps" min="1" required />
          <input v-model.number="ex.rest_seconds" type="number" placeholder="Rest (s)" />
          <button type="button" class="btn btn-danger btn-sm" @click="form.exercises.splice(idx, 1)">X</button>
        </div>
        <button type="button" class="btn btn-secondary" @click="addExercise" style="margin-top: 8px">+ Add Exercise</button>
        <br />
        <button type="submit" class="btn btn-primary" style="margin-top: 16px">Save Plan</button>
      </form>
    </div>

    <!-- Filters -->
    <div class="card filters">
      <select v-model="filterDifficulty" @change="fetchPlans">
        <option value="">All Difficulties</option>
        <option value="beginner">Beginner</option>
        <option value="intermediate">Intermediate</option>
        <option value="advanced">Advanced</option>
      </select>
    </div>

    <!-- Plans -->
    <div class="plans-grid">
      <div v-for="plan in plans" :key="plan.id" class="card plan-card">
        <div class="plan-header">
          <h3>{{ plan.name }}</h3>
          <span :class="`badge badge-${plan.difficulty === 'advanced' ? 'pt' : plan.difficulty === 'intermediate' ? 'premium' : 'basic'}`">
            {{ plan.difficulty }}
          </span>
        </div>
        <p class="plan-desc">{{ plan.description }}</p>
        <div class="plan-meta">
          <span>{{ plan.estimated_duration_minutes }} min</span>
          <span>{{ plan.exercises.length }} exercises</span>
          <span>By {{ plan.created_by }}</span>
        </div>
        <div class="exercises-list">
          <div v-for="ex in plan.exercises" :key="ex.name" class="exercise-item">
            {{ ex.name }} — {{ ex.sets }}x{{ ex.reps }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="plans.length === 0" class="card empty-state">
      No workout plans found
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { workoutApi } from '../services/api'

const plans = ref([])
const showForm = ref(false)
const filterDifficulty = ref('')

const form = ref({
  name: '',
  description: '',
  difficulty: 'beginner',
  estimated_duration_minutes: 45,
  created_by: '',
  exercises: [{ name: '', sets: 3, reps: 12, rest_seconds: 60 }],
})

function addExercise() {
  form.value.exercises.push({ name: '', sets: 3, reps: 12, rest_seconds: 60 })
}

async function fetchPlans() {
  try {
    const params = {}
    if (filterDifficulty.value) params.difficulty = filterDifficulty.value
    const { data } = await workoutApi.listPlans(params)
    plans.value = data.items
  } catch (e) {
    console.error('Failed to fetch plans:', e)
  }
}

async function createPlan() {
  try {
    await workoutApi.createPlan(form.value)
    showForm.value = false
    form.value = {
      name: '', description: '', difficulty: 'beginner',
      estimated_duration_minutes: 45, created_by: '',
      exercises: [{ name: '', sets: 3, reps: 12, rest_seconds: 60 }],
    }
    await fetchPlans()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to create plan')
  }
}

onMounted(fetchPlans)
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

.plans-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.plan-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-desc {
  font-size: 14px;
  color: #636e72;
}

.plan-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #636e72;
}

.exercises-list {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.exercise-item {
  font-size: 13px;
  padding: 4px 0;
  color: #2d3436;
}

.exercise-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  align-items: center;
}

.exercise-row input {
  flex: 1;
}

.exercise-row input:first-child {
  flex: 3;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #636e72;
}

h3 { font-size: 16px; font-weight: 600; }
h4 { font-size: 14px; font-weight: 600; }
.btn-sm { padding: 4px 10px; font-size: 12px; }
</style>
