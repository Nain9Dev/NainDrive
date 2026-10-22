<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import NavRail, { type NavItem, type ViewKey } from './components/NavRail.vue'
import TopBar from './components/TopBar.vue'
import ToastHost from './components/ToastHost.vue'
import AppIcon from './components/AppIcon.vue'
import StudentDrawer from './components/students/StudentDrawer.vue'
import DashboardView from './views/DashboardView.vue'
import StudentsView from './views/StudentsView.vue'
import ExamsView from './views/ExamsView.vue'
import FleetView from './views/FleetView.vue'
import { driveData } from './store/driveData'

const { state } = driveData

type DrawerAction = 'classes' | 'advance' | 'exam' | 'invoice'

const active = ref<ViewKey>('dashboard')
const openDni = ref<string | null>(null)
const openAction = ref<DrawerAction | null>(null)

function openStudent(dni: string, action?: DrawerAction) {
  openDni.value = dni
  openAction.value = action ?? null
}

function closeStudent() {
  openDni.value = null
  openAction.value = null
}

const navItems = computed<NavItem[]>(() => [
  { key: 'dashboard', label: 'Panel', icon: 'dashboard' },
  { key: 'students', label: 'Alumnos', icon: 'users', count: state.students.length },
  { key: 'exams', label: 'Exámenes', icon: 'calendar', count: state.appointments.filter((a) => a.status === 'SCHEDULED').length },
  { key: 'fleet', label: 'Flota', icon: 'car', count: state.instructors.length },
])

const viewTitle = computed(() => navItems.value.find((n) => n.key === active.value)?.label ?? '')

const drawerStudent = computed(() => (openDni.value ? driveData.studentFor(openDni.value) ?? null : null))

function go(key: ViewKey) {
  active.value = key
  window.scrollTo({ top: 0 })
}

onMounted(() => {
  driveData.refresh()
})
</script>

<template>
  <div class="backdrop" aria-hidden="true">
    <div class="backdrop-grid"></div>
  </div>

  <div class="shell">
    <TopBar :healthy="state.healthy" :title="viewTitle" @refresh="driveData.refresh" />

    <div class="shell-body">
      <NavRail :items="navItems" :active="active" @select="go" />

      <main class="content" :aria-busy="state.loading">
        <div v-if="state.error" class="error-bar panel" role="alert">
          <AppIcon name="alert" :size="18" />
          <span>{{ state.error }}</span>
          <button type="button" class="btn btn-soft btn-sm" @click="driveData.refresh">Reintentar</button>
        </div>

        <Transition name="fade" mode="out-in">
          <DashboardView v-if="active === 'dashboard'" key="dashboard" @open-student="openStudent" @go="go" />
          <StudentsView v-else-if="active === 'students'" key="students" @open-student="openStudent" />
          <ExamsView v-else-if="active === 'exams'" key="exams" @open-student="openStudent" />
          <FleetView v-else key="fleet" />
        </Transition>
      </main>
    </div>

    <footer class="foot">
      <span>NainDrive</span>
      <span class="dot" aria-hidden="true"></span>
      <a href="https://www.naindev.com" target="_blank" rel="noopener">naindev</a>
    </footer>
  </div>

  <StudentDrawer :student="drawerStudent" :initial-action="openAction" @close="closeStudent" />
  <ToastHost />
</template>

<style scoped>
.shell {
  position: relative;
  z-index: 1;
  max-width: var(--shell-max);
  margin: 0 auto;
  padding: 0 1.5rem 2rem;
  min-height: calc(100vh - var(--eco-bar-h));
  display: flex;
  flex-direction: column;
}

.shell-body {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
  flex: 1;
}

.content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.error-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.8rem 1rem;
  border-color: rgba(255, 77, 109, 0.4);
  color: var(--rose-2);
}

.error-bar span {
  flex: 1;
  color: var(--ink);
}

.foot {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 2rem 0 0;
  font-size: 0.75rem;
  color: var(--ink-3);
}

.foot a:hover {
  color: var(--ink);
}

.dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--ink-3);
}

@media (max-width: 860px) {
  .shell {
    padding: 0 1rem 6.5rem;
  }

  .shell-body {
    gap: 0;
  }
}
</style>
