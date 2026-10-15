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

const API_BASE = '/api/v1'

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error(`Health status check failed: ${res.status}`)
  return res.json()
}

export async function fetchDashboard(): Promise<KPIDashboardSummary> {
  const res = await fetch(`${API_BASE}/dashboard`)
  if (!res.ok) throw new Error(`Failed to fetch dashboard metrics: ${res.status}`)
  return res.json()
}

export async function fetchStudents(): Promise<Student[]> {
  const res = await fetch(`${API_BASE}/students`)
  if (!res.ok) throw new Error(`Failed to fetch students: ${res.status}`)
  return res.json()
}

export async function fetchStudent(dni: string): Promise<Student> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}`)
  if (!res.ok) throw new Error(`Student ${dni} not found.`)
  return res.json()
}

export async function createStudent(payload: NewStudentPayload): Promise<Student> {
  const res = await fetch(`${API_BASE}/students`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const errorBody = await res.json().catch(() => null)
    const msg = errorBody?.detail || `Error creating student (${res.status})`
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg))
  }
  return res.json()
}

export async function deleteStudent(dni: string): Promise<void> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error(`Failed to delete student (${res.status})`)
}

export async function addStudentClasses(dni: string, count: number): Promise<Student> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/classes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ count }),
  })
  if (!res.ok) throw new Error(`Failed to add practical classes: ${res.status}`)
  return res.json()
}

export async function registerStudentExam(
  dni: string,
  examType: 'THEORETICAL' | 'PRACTICAL'
): Promise<Student> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/exams`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ exam_type: examType }),
  })
  if (!res.ok) throw new Error(`Failed to register exam attempt: ${res.status}`)
  return res.json()
}

export async function recordStudentAdvance(dni: string, amount: number): Promise<Student> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/advances`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount }),
  })
  if (!res.ok) throw new Error(`Failed to record advance payment: ${res.status}`)
  return res.json()
}

export async function fetchInvoice(dni: string): Promise<InvoiceCalculation> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/invoice`)
  if (!res.ok) throw new Error(`Failed to calculate invoice: ${res.status}`)
  return res.json()
}

export function getInvoicePdfDownloadUrl(dni: string): string {
  return `${API_BASE}/students/${encodeURIComponent(dni)}/pdf`
}

export async function fetchAllDgtAppointments(): Promise<DgtExamAppointment[]> {
  const res = await fetch(`${API_BASE}/dgt/appointments`)
  if (!res.ok) throw new Error(`Failed to fetch DGT appointments: ${res.status}`)
  return res.json()
}

export async function scheduleDgtAppointment(
  dni: string,
  payload: ScheduleDgtPayload
): Promise<DgtExamAppointment> {
  const res = await fetch(`${API_BASE}/students/${encodeURIComponent(dni)}/dgt/appointments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const errorBody = await res.json().catch(() => null)
    throw new Error(errorBody?.detail || `Failed to schedule DGT appointment: ${res.status}`)
  }
  return res.json()
}

export async function fetchInstructors(): Promise<Instructor[]> {
  const res = await fetch(`${API_BASE}/instructors`)
  if (!res.ok) throw new Error(`Failed to fetch instructors: ${res.status}`)
  return res.json()
}

export async function recordFuelExpense(instructorId: string, amount: number): Promise<Instructor> {
  const res = await fetch(`${API_BASE}/instructors/${encodeURIComponent(instructorId)}/fuel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ amount }),
  })
  if (!res.ok) throw new Error(`Failed to record fuel expense: ${res.status}`)
  return res.json()
}

export async function fetchPackages(): Promise<LicensePackage[]> {
  const res = await fetch(`${API_BASE}/packages`)
  if (!res.ok) throw new Error(`Failed to fetch packages: ${res.status}`)
  return res.json()
}

export async function resetDatabase(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API_BASE}/admin/reset`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to reset database: ${res.status}`)
  return res.json()
}
