import { computed, reactive, readonly } from 'vue'
import {
  fetchAllDgtAppointments,
  fetchDashboard,
  fetchHealth,
  fetchInstructors,
  fetchPackages,
  fetchStudents,
} from '../services/api'
import type {
  DgtExamAppointment,
  Instructor,
  KPIDashboardSummary,
  LicensePackage,
  Student,
} from '../types/contracts'

const EMPTY_SUMMARY: KPIDashboardSummary = {
  total_gross: 0,
  total_vat: 0,
  total_pending: 0,
  completed_lessons_sum: 0,
  license_distribution: {},
  total_students: 0,
  total_instructors: 0,
  average_lessons_per_student: 0,
}

const state = reactive({
  loading: true,
  error: null as string | null,
  healthy: false,
  summary: EMPTY_SUMMARY as KPIDashboardSummary,
  students: [] as Student[],
  appointments: [] as DgtExamAppointment[],
  instructors: [] as Instructor[],
  packages: [] as LicensePackage[],
})

async function refresh(): Promise<void> {
  state.error = null
  try {
    const [health, summary, students, appointments, instructors, packages] = await Promise.all([
      fetchHealth().catch(() => null),
      fetchDashboard(),
      fetchStudents(),
      fetchAllDgtAppointments(),
      fetchInstructors(),
      fetchPackages(),
    ])
    // The mock store also reports healthy; only a real gateway counts as connected.
    state.healthy = health?.status === 'healthy' && !/in-memory/i.test(health.transport ?? '')
    state.summary = summary
    state.students = students
    state.appointments = appointments
    state.instructors = instructors
    state.packages = packages
  } catch (err: unknown) {
    state.error = err instanceof Error ? err.message : 'No se pudo cargar la información.'
  } finally {
    state.loading = false
  }
}

const packageByLicence = computed(() => {
  const map = new Map<string, LicensePackage>()
  for (const p of state.packages) {
    const code = p.package_code.replace(/^PERMIT_/, '')
    map.set(code, p)
  }
  return map
})

const studentByDni = computed(() => {
  const map = new Map<string, Student>()
  for (const s of state.students) map.set(s.dni.toUpperCase(), s)
  return map
})

export const driveData = {
  state: readonly(state),
  refresh,
  packageFor(licence: string): LicensePackage | undefined {
    return packageByLicence.value.get(licence) ?? state.packages[0]
  },
  studentFor(dni: string): Student | undefined {
    return studentByDni.value.get(dni.toUpperCase())
  },
}
