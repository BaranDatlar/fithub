import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// --- Members ---
export const memberApi = {
  list: (params) => api.get('/members', { params }),
  get: (id) => api.get(`/members/${id}`),
  create: (data) => api.post('/members', data),
  update: (id, data) => api.put(`/members/${id}`, data),
  delete: (id) => api.delete(`/members/${id}`),
  getStats: (id) => api.get(`/members/${id}/stats`),
}

// --- Classes ---
export const classApi = {
  list: (params) => api.get('/classes', { params }),
  get: (id) => api.get(`/classes/${id}`),
  create: (data) => api.post('/classes', data),
  update: (id, data) => api.put(`/classes/${id}`, data),
  delete: (id) => api.delete(`/classes/${id}`),
  book: (classId, memberId) => api.post(`/classes/${classId}/book?member_id=${memberId}`),
  unbook: (classId, memberId) => api.delete(`/classes/${classId}/book?member_id=${memberId}`),
  getParticipants: (id) => api.get(`/classes/${id}/participants`),
}

// --- Workouts ---
export const workoutApi = {
  listPlans: (params) => api.get('/workouts/plans', { params }),
  getPlan: (id) => api.get(`/workouts/plans/${id}`),
  createPlan: (data) => api.post('/workouts/plans', data),
  assignPlan: (data) => api.post('/workouts/assign', data),
  getMemberWorkouts: (memberId) => api.get(`/workouts/member/${memberId}`),
  logWorkout: (data) => api.post('/workouts/log', data),
  getMemberLogs: (memberId, params) => api.get(`/workouts/member/${memberId}/logs`, { params }),
}

// --- Exercises ---
export const exerciseApi = {
  list: () => api.get('/exercises'),
  listSessions: (params) => api.get('/exercises/sessions', { params }),
  getSession: (id) => api.get(`/exercises/sessions/${id}`),
}

// --- Analytics ---
export const analyticsApi = {
  getOverview: () => api.get('/analytics/overview'),
  getMembers: () => api.get('/analytics/members'),
  getClasses: () => api.get('/analytics/classes'),
  getRevenue: () => api.get('/analytics/revenue'),
}

export default api
