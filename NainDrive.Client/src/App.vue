<script setup lang="ts">
import { ref, onMounted } from 'vue'
import HeaderNav from './components/HeaderNav.vue'
import DashboardKpis from './components/DashboardKpis.vue'
import StudentsManager from './components/StudentsManager.vue'
import DgtAppointments from './components/DgtAppointments.vue'
import InstructorsFleet from './components/InstructorsFleet.vue'
import InvoiceBillingModal from './components/InvoiceBillingModal.vue'
import {
  fetchDashboard,
  fetchStudents,
  fetchAllDgtAppointments,
  fetchHealth,
} from './services/api'
import type {
  KPIDashboardSummary,
  Student,
  DgtExamAppointment,
} from './types/contracts'

type ActiveTab = 'students' | 'dgt' | 'fleet'

const activeTab = ref<ActiveTab>('students')
const apiHealthy = ref(false)
const loading = ref(true)
const globalError = ref<string | null>(null)

const summary = ref<KPIDashboardSummary>({
  total_gross: 0,
  total_vat: 0,
  total_pending: 0,
  completed_lessons_sum: 0,
  license_distribution: {},
  total_students: 0,
  total_instructors: 0,
  average_lessons_per_student: 0,
})

const students = ref<Student[]>([])
const appointments = ref<DgtExamAppointment[]>([])
const selectedInvoiceDni = ref<string | null>(null)

async function checkHealthStatus() {
  try {
    const h = await fetchHealth()
    apiHealthy.value = h.status === 'healthy'
  } catch {
    apiHealthy.value = false
  }
}

async function loadInitialData() {
  loading.value = true
  globalError.value = null
  try {
    await checkHealthStatus()
    const [dashData, studentsData, apptsData] = await Promise.all([
      fetchDashboard(),
      fetchStudents(),
      fetchAllDgtAppointments(),
    ])
    summary.value = dashData
    students.value = studentsData
    appointments.value = apptsData
  } catch (err: any) {
    globalError.value = err.message || 'Error al conectar con la pasarela FastAPI (:8150).'
  } finally {
    loading.value = false
  }
}

async function handleRefresh() {
  try {
    await checkHealthStatus()
    const [dashData, studentsData, apptsData] = await Promise.all([
      fetchDashboard(),
      fetchStudents(),
      fetchAllDgtAppointments(),
    ])
    summary.value = dashData
    students.value = studentsData
    appointments.value = apptsData
  } catch (err: any) {
    console.error('Error refreshing state:', err)
  }
}

function handleViewInvoice(dni: string) {
  selectedInvoiceDni.value = dni
}

function handleCloseInvoice() {
  selectedInvoiceDni.value = null
}

onMounted(() => {
  loadInitialData()
})
</script>

<template>
  <div class="app-root">
    <!-- Header -->
    <HeaderNav :api-healthy="apiHealthy" @reset="handleRefresh" />

    <!-- Main Container -->
    <main class="container main-content">
      <!-- Error Alert -->
      <div v-if="globalError" class="alert alert-danger mb-6">
        <div class="flex items-center justify-between">
          <div>
            <strong>Error de Comunicación API:</strong> {{ globalError }}
          </div>
          <button class="btn btn-secondary btn-sm" @click="loadInitialData">Reintentar</button>
        </div>
      </div>

      <!-- KPI Executive Dashboard Overview -->
      <section class="section-kpis mb-8">
        <DashboardKpis :summary="summary" />
      </section>

      <!-- Navigation Tabs -->
      <div class="tabs-nav-bar mb-6">
        <div class="tabs-wrapper">
          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'students' }"
            @click="activeTab = 'students'"
          >
            <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <span>Alumnos y Liquidación</span>
            <span class="tab-count font-mono">{{ students.length }}</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'dgt' }"
            @click="activeTab = 'dgt'"
          >
            <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>Convocatorias DGT</span>
            <span class="tab-count font-mono">{{ appointments.length }}</span>
          </button>

          <button
            type="button"
            class="tab-btn"
            :class="{ active: activeTab === 'fleet' }"
            @click="activeTab = 'fleet'"
          >
            <svg class="tab-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
            <span>Flota & Tarifas</span>
            <span class="tab-count font-mono">{{ summary.total_instructors }}</span>
          </button>
        </div>
      </div>

      <!-- Tab Content Area -->
      <transition name="fade-fast" mode="out-in">
        <!-- Students Tab -->
        <div v-if="activeTab === 'students'" key="students">
          <StudentsManager
            :students="students"
            @refresh="handleRefresh"
            @view-invoice="handleViewInvoice"
          />
        </div>

        <!-- DGT Appointments Tab -->
        <div v-else-if="activeTab === 'dgt'" key="dgt">
          <DgtAppointments
            :appointments="appointments"
            :students="students"
            @refresh="handleRefresh"
          />
        </div>

        <!-- Fleet & Instructors Tab -->
        <div v-else-if="activeTab === 'fleet'" key="fleet">
          <InstructorsFleet
            @refresh="handleRefresh"
          />
        </div>
      </transition>
    </main>

    <!-- In-memory PDF Billing Modal -->
    <InvoiceBillingModal
      :dni="selectedInvoiceDni"
      @close="handleCloseInvoice"
    />

    <!-- Footer -->
    <footer class="app-footer">
      <div class="container footer-content">
        <div class="footer-left">
          <strong>NainDrive v2.0.0</strong> · Sistema de Gestión de Autoescuela con Arquitectura Limpia y Facturación Determinista.
        </div>
        <div class="footer-right">
          <span>Python 3.12 · FastAPI :8150 · Vue 3 :5379 · Streamlit :8151</span>
          <span class="separator">|</span>
          <a href="https://www.naindev.com" target="_blank" rel="noopener" class="footer-link">
            Aitor Nain Mendoza Vallejo (naindev)
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 2rem;
  padding-bottom: 4rem;
}

.mb-6 {
  margin-bottom: 1.5rem;
}

.mb-8 {
  margin-bottom: 2rem;
}

.tabs-nav-bar {
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-start;
}

.tabs-wrapper {
  display: flex;
  gap: 0.5rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-dim);
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: -1px;
}

.tab-btn:hover {
  color: var(--color-text-main);
  background: rgba(255, 255, 255, 0.02);
}

.tab-btn.active {
  color: var(--accent-blue);
  border-bottom-color: var(--accent-blue);
}

.tab-icon {
  width: 1.2rem;
  height: 1.2rem;
}

.tab-count {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.08);
  color: var(--color-text-muted);
}

.tab-btn.active .tab-count {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.fade-fast-enter-active,
.fade-fast-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.fade-fast-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.fade-fast-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.app-footer {
  border-top: 1px solid var(--color-border);
  background: rgba(6, 9, 19, 0.9);
  padding: 1.5rem 0;
  color: var(--color-text-dim);
  font-size: 0.82rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
}

.separator {
  color: var(--color-border);
}

.footer-link {
  color: var(--accent-blue);
  text-decoration: none;
  font-family: var(--font-sans);
  font-weight: 500;
}

.footer-link:hover {
  text-decoration: underline;
}

.alert {
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
}

.alert-danger {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.justify-between {
  justify-content: space-between;
}
</style>
