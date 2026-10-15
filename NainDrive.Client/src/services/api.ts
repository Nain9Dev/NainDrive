import type {
  DgtExamAppointment,
  HealthStatus,
  Instructor,
  InvoiceCalculation,
  KPIDashboardSummary,
  LicensePackage,
  NewStudentPayload,
  ScheduleDgtPayload,
  Student,
} from '../types/contracts'
import { mockDriveStore } from './mockDriveStore'

const API_BASE = '/api/v1'

export async function fetchHealth(): Promise<HealthStatus> {
  try {
    const res = await fetch(`${API_BASE}/health`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getHealth()
}

export async function fetchDashboard(): Promise<KPIDashboardSummary> {
  try {
    const res = await fetch(`${API_BASE}/dashboard`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getDashboard()
}

export async function fetchStudents(): Promise<Student[]> {
  try {
    const res = await fetch(`${API_BASE}/students`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getStudents()
}

export async function fetchStudent(dni: string): Promise<Student> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getStudent(dni)
}

export async function createStudent(payload: NewStudentPayload): Promise<Student> {
  try {
    const res = await fetch(`${API_BASE}/students`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.createStudent(payload)
}

export async function deleteStudent(dni: string): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}`, {
      method: 'DELETE',
    })
    if (res.ok) return
  } catch {
    // Standalone fallback
  }
  mockDriveStore.deleteStudent(dni)
}

export async function addStudentClasses(dni: string, count: number): Promise<Student> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/classes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ count }),
    })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.addClasses(dni, count)
}

export async function registerStudentExam(
  dni: string,
  examType: 'THEORETICAL' | 'PRACTICAL'
): Promise<Student> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/exams`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ exam_type: examType }),
    })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.registerExam(dni, examType)
}

export async function recordStudentAdvance(dni: string, amount: number): Promise<Student> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/advances`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount }),
    })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.recordAdvance(dni, amount)
}

export async function fetchInvoice(dni: string): Promise<InvoiceCalculation> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/invoice`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getInvoice(dni)
}

export function getInvoicePdfDownloadUrl(dni: string): string {
  if (window.location.hostname === 'localhost' && window.location.port === '5379') {
    return `${API_BASE}/students/${encodeURIComponent(dni)}/pdf`
  }
  return mockDriveStore.getInvoiceHtmlUrl(dni)
}

export async function fetchAllDgtAppointments(): Promise<DgtExamAppointment[]> {
  try {
    const res = await fetch(`${API_BASE}/dgt/appointments`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getAppointments()
}

export async function scheduleDgtAppointment(
  dni: string,
  payload: ScheduleDgtPayload
): Promise<DgtExamAppointment> {
  try {
    const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/dgt/appointments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.scheduleAppointment(dni, payload)
}

export async function fetchInstructors(): Promise<Instructor[]> {
  try {
    const res = await fetch(`${API_BASE}/instructors`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getInstructors()
}

export async function recordFuelExpense(instructorId: string, amount: number): Promise<Instructor> {
  try {
    const res = await fetch(`${API_BASE}/instructors/${encodeURIComponent(instructorId)}/fuel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount }),
    })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.recordFuel(instructorId, amount)
}

export async function fetchPackages(): Promise<LicensePackage[]> {
  try {
    const res = await fetch(`${API_BASE}/packages`)
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.getPackages()
}

export async function resetDatabase(): Promise<{ status: string; message: string }> {
  try {
    const res = await fetch(`${API_BASE}/admin/reset`, { method: 'POST' })
    if (res.ok) return await res.json()
  } catch {
    // Standalone fallback
  }
  return mockDriveStore.reset()
}
