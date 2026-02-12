import { createRouter, createWebHistory } from 'vue-router'

import DashboardView from '../views/DashboardView.vue'
import MembersView from '../views/MembersView.vue'
import MemberDetailView from '../views/MemberDetailView.vue'
import ClassesView from '../views/ClassesView.vue'
import WorkoutPlansView from '../views/WorkoutPlansView.vue'
import ExerciseTrackerView from '../views/ExerciseTrackerView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: DashboardView },
  { path: '/members', name: 'Members', component: MembersView },
  { path: '/members/:id', name: 'MemberDetail', component: MemberDetailView },
  { path: '/classes', name: 'Classes', component: ClassesView },
  { path: '/workouts', name: 'Workouts', component: WorkoutPlansView },
  { path: '/exercise-tracker', name: 'ExerciseTracker', component: ExerciseTrackerView },
  { path: '/analytics', name: 'Analytics', component: AnalyticsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
