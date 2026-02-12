<template>
  <div class="members-page">
    <div class="page-header">
      <h2>Members</h2>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ New Member' }}
      </button>
    </div>

    <!-- Create Form -->
    <div v-if="showForm" class="card form-card">
      <h3>Add New Member</h3>
      <form @submit.prevent="createMember">
        <div class="form-grid">
          <div class="form-group">
            <label>First Name</label>
            <input v-model="form.first_name" required />
          </div>
          <div class="form-group">
            <label>Last Name</label>
            <input v-model="form.last_name" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Phone</label>
            <input v-model="form.phone" />
          </div>
          <div class="form-group">
            <label>Plan</label>
            <select v-model="form.membership.plan">
              <option value="basic">Basic</option>
              <option value="premium">Premium</option>
              <option value="pt">Personal Training</option>
            </select>
          </div>
          <div class="form-group">
            <label>Fitness Level</label>
            <select v-model="form.profile.fitness_level">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn btn-primary" style="margin-top: 16px">Save Member</button>
      </form>
    </div>

    <!-- Filters -->
    <div class="card filters">
      <input
        v-model="search"
        placeholder="Search by name or email..."
        @input="fetchMembers"
      />
      <select v-model="filterStatus" @change="fetchMembers">
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="frozen">Frozen</option>
        <option value="expired">Expired</option>
      </select>
      <select v-model="filterPlan" @change="fetchMembers">
        <option value="">All Plans</option>
        <option value="basic">Basic</option>
        <option value="premium">Premium</option>
        <option value="pt">PT</option>
      </select>
    </div>

    <!-- Members Table -->
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Joined</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="member.id">
            <td>
              <router-link :to="`/members/${member.id}`" class="member-name">
                {{ member.first_name }} {{ member.last_name }}
              </router-link>
            </td>
            <td>{{ member.email }}</td>
            <td><span :class="`badge badge-${member.membership.plan}`">{{ member.membership.plan }}</span></td>
            <td><span :class="`badge badge-${member.membership.status}`">{{ member.membership.status }}</span></td>
            <td>{{ new Date(member.created_at).toLocaleDateString() }}</td>
            <td>
              <button class="btn btn-danger btn-sm" @click="deleteMember(member.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="members.length === 0" class="empty-state">
        No members found
      </div>

      <div class="pagination">
        <button class="btn btn-secondary" :disabled="page <= 1" @click="page--; fetchMembers()">Previous</button>
        <span>Page {{ page }} of {{ totalPages }}</span>
        <button class="btn btn-secondary" :disabled="page >= totalPages" @click="page++; fetchMembers()">Next</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { memberApi } from '../services/api'

const members = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const filterStatus = ref('')
const filterPlan = ref('')
const showForm = ref(false)

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  membership: { plan: 'basic' },
  profile: { fitness_level: 'beginner' },
})

const totalPages = ref(1)

async function fetchMembers() {
  try {
    const params = { page: page.value, page_size: pageSize }
    if (search.value) params.search = search.value
    if (filterStatus.value) params.status = filterStatus.value
    if (filterPlan.value) params.plan = filterPlan.value

    const { data } = await memberApi.list(params)
    members.value = data.items
    total.value = data.total
    totalPages.value = Math.ceil(data.total / pageSize) || 1
  } catch (e) {
    console.error('Failed to fetch members:', e)
  }
}

async function createMember() {
  try {
    await memberApi.create(form.value)
    showForm.value = false
    form.value = {
      first_name: '', last_name: '', email: '', phone: '',
      membership: { plan: 'basic' }, profile: { fitness_level: 'beginner' },
    }
    await fetchMembers()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to create member')
  }
}

async function deleteMember(id) {
  if (!confirm('Are you sure you want to delete this member?')) return
  try {
    await memberApi.delete(id)
    await fetchMembers()
  } catch (e) {
    alert('Failed to delete member')
  }
}

onMounted(fetchMembers)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-card {
  margin-bottom: 24px;
}

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

.filters input {
  flex: 2;
}

.filters select {
  flex: 1;
}

.member-name {
  color: #6c5ce7;
  text-decoration: none;
  font-weight: 500;
}

.member-name:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #636e72;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

h3 {
  font-size: 16px;
  font-weight: 600;
}
</style>
