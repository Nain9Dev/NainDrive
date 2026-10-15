export interface KPIDashboardSummary {
  total_gross: number | string
  total_vat: number | string
  total_pending: number | string
  completed_lessons_sum: number
  license_distribution: Record<string, number>
  total_students: number
  total_instructors: number
  average_lessons_per_student: number
}

export interface Student {
  registration_number: string
  dni: string
  first_name: string
  last_name: string
  phone: string
  birth_date?: string
  email?: string
  address?: string
  target_license: string
  assigned_instructor_id?: string
  completed_classes: number
  theoretical_exams_count: number
  practical_exams_count: number
  total_advances_paid: number | string
}

export interface NewStudentPayload {
  dni: string
  first_name: string
  last_name: string
  phone: string
  target_license: string
  total_advances_paid: number
}

export interface Instructor {
  instructor_id: string
  full_name: string
  assigned_vehicle_plate: string
  vehicle_model: string
  itv_expiration_date: string
  total_fuel_expenses: number | string
}

export interface LicensePackage {
  package_code: string
  name: string
  enrollment_fee: number | string
  included_practical_classes: number
  extra_class_price: number | string
  dgt_exam_fee: number | string
  renewal_fee: number | string
}

export interface InvoiceCalculation {
  invoice_number: string
  invoice_date: string
  student_dni: string
  student_name: string
  target_license: string
  enrollment_fee: number | string
  included_classes: number
  completed_classes: number
  extra_classes_count: number
  extra_classes_cost: number | string
  total_exams_count: number
  total_exams_cost: number | string
  subtotal_amount: number | string
  vat_percentage: number | string
  vat_amount: number | string
  total_with_vat: number | string
  advances_paid: number | string
  pending_balance: number | string
}

export type DgtExamType = 'THEORETICAL' | 'PRACTICAL'
export type DgtAppointmentStatus = 'SCHEDULED' | 'PASSED' | 'FAILED' | 'CANCELLED'

export interface DgtExamAppointment {
  appointment_id: string
  student_dni: string
  exam_type: DgtExamType
  appointment_date: string
  center_location: string
  status: DgtAppointmentStatus
}

export interface ScheduleDgtPayload {
  exam_type: DgtExamType
  appointment_date: string
  center_location?: string
}

export interface HealthStatus {
  service: string
  version: string
  architecture: string
  status: string
  transport: string
}
