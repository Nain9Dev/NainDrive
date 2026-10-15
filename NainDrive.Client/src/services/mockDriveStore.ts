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

const INITIAL_PACKAGES: LicensePackage[] = [
  {
    package_code: 'PERMIT_B',
    name: 'Permiso B - Turismo (Manual / Automático)',
    enrollment_fee: 195.0,
    included_practical_classes: 10,
    extra_class_price: 32.5,
    dgt_exam_fee: 94.05,
    renewal_fee: 150.0,
  },
  {
    package_code: 'PERMIT_A2',
    name: 'Permiso A2 - Motocicletas hasta 35kW',
    enrollment_fee: 150.0,
    included_practical_classes: 5,
    extra_class_price: 28.0,
    dgt_exam_fee: 94.05,
    renewal_fee: 150.0,
  },
  {
    package_code: 'PERMIT_C',
    name: 'Permiso C - Camión Rígido Profesional',
    enrollment_fee: 350.0,
    included_practical_classes: 8,
    extra_class_price: 55.0,
    dgt_exam_fee: 94.05,
    renewal_fee: 180.0,
  },
]

const INITIAL_INSTRUCTORS: Instructor[] = [
  {
    instructor_id: 'INST-01',
    full_name: 'NainDev Mendoza Vallejo',
    assigned_vehicle_plate: '1234-BBC',
    vehicle_model: 'SEAT León 2.0 TDI FR',
    itv_expiration_date: '01-08-2027',
    total_fuel_expenses: 450.5,
  },
  {
    instructor_id: 'INST-02',
    full_name: 'Carlos García Torrijos',
    assigned_vehicle_plate: '5678-LMN',
    vehicle_model: 'Yamaha MT-07 ABS',
    itv_expiration_date: '15-11-2026',
    total_fuel_expenses: 180.2,
  },
  {
    instructor_id: 'INST-03',
    full_name: 'Elena Rostropovich',
    assigned_vehicle_plate: '9012-KLP',
    vehicle_model: 'Volvo FL6 Camión Rígido',
    itv_expiration_date: '30-04-2027',
    total_fuel_expenses: 890.0,
  },
]

const INITIAL_STUDENTS: Student[] = [
  {
    registration_number: 'EXP-2026-001',
    dni: '53822281G',
    first_name: 'Alvaro',
    last_name: 'Morata Lopez',
    phone: '612345678',
    target_license: 'B',
    assigned_instructor_id: 'INST-01',
    completed_classes: 14,
    theoretical_exams_count: 1,
    practical_exams_count: 1,
    total_advances_paid: 250.0,
  },
  {
    registration_number: 'EXP-2026-002',
    dni: '11223344B',
    first_name: 'Lucia',
    last_name: 'Jimenez Diaz',
    phone: '698765432',
    target_license: 'A2',
    assigned_instructor_id: 'INST-02',
    completed_classes: 5,
    theoretical_exams_count: 1,
    practical_exams_count: 0,
    total_advances_paid: 150.0,
  },
  {
    registration_number: 'EXP-2026-003',
    dni: '44556677L',
    first_name: 'David',
    last_name: 'Rodriguez Fernandez',
    phone: '655443322',
    target_license: 'C',
    assigned_instructor_id: 'INST-03',
    completed_classes: 12,
    theoretical_exams_count: 2,
    practical_exams_count: 1,
    total_advances_paid: 500.0,
  },
  {
    registration_number: 'EXP-2026-004',
    dni: '78901234X',
    first_name: 'Sofia',
    last_name: 'Alvarez Castillo',
    phone: '677889900',
    target_license: 'B',
    assigned_instructor_id: 'INST-01',
    completed_classes: 3,
    theoretical_exams_count: 0,
    practical_exams_count: 0,
    total_advances_paid: 100.0,
  },
]

const INITIAL_APPOINTMENTS: DgtExamAppointment[] = [
  {
    appointment_id: 'DGT-2026-001',
    student_dni: '53822281G',
    exam_type: 'THEORETICAL',
    appointment_date: '22-11-2026',
    center_location: 'Centro de Examenes DGT Madrid-Mostoles',
    status: 'PASSED',
  },
  {
    appointment_id: 'DGT-2026-002',
    student_dni: '53822281G',
    exam_type: 'PRACTICAL',
    appointment_date: '15-12-2026',
    center_location: 'Centro de Examenes DGT Madrid-Mostoles',
    status: 'SCHEDULED',
  },
  {
    appointment_id: 'DGT-2026-003',
    student_dni: '11223344B',
    exam_type: 'THEORETICAL',
    appointment_date: '05-12-2026',
    center_location: 'Centro de Examenes DGT Madrid-Mostoles',
    status: 'PASSED',
  },
]

// Mutable in-memory store
let packages = JSON.parse(JSON.stringify(INITIAL_PACKAGES)) as LicensePackage[]
let instructors = JSON.parse(JSON.stringify(INITIAL_INSTRUCTORS)) as Instructor[]
let students = JSON.parse(JSON.stringify(INITIAL_STUDENTS)) as Student[]
let appointments = JSON.parse(JSON.stringify(INITIAL_APPOINTMENTS)) as DgtExamAppointment[]

function calculateInvoiceForStudent(student: Student): InvoiceCalculation {
  const pkgCode =
    student.target_license === 'A2'
      ? 'PERMIT_A2'
      : student.target_license === 'C'
      ? 'PERMIT_C'
      : 'PERMIT_B'
  const pkg = packages.find((p) => p.package_code === pkgCode) || packages[0]

  const enrollmentFee = Number(pkg.enrollment_fee)
  const extraPrice = Number(pkg.extra_class_price)
  const examFee = Number(pkg.dgt_exam_fee)
  const includedClasses = pkg.included_practical_classes

  const extraClasses = Math.max(0, student.completed_classes - includedClasses)
  const extraClassesCost = Math.round(extraClasses * extraPrice * 100) / 100

  const totalExams = student.theoretical_exams_count + student.practical_exams_count
  const totalExamsCost = Math.round(totalExams * examFee * 100) / 100

  const subtotal = Math.round((enrollmentFee + extraClassesCost + totalExamsCost) * 100) / 100
  const vatRate = 0.21
  const vatAmount = Math.round(subtotal * vatRate * 100) / 100
  const totalWithVat = Math.round((subtotal + vatAmount) * 100) / 100

  const advances = Number(student.total_advances_paid)
  const pending = Math.round((totalWithVat - advances) * 100) / 100

  const today = new Date().toISOString().split('T')[0]

  return {
    invoice_number: `FAC-2026-${student.registration_number.replace('EXP-2026-', '')}`,
    invoice_date: today,
    student_dni: student.dni,
    student_name: `${student.first_name} ${student.last_name}`,
    target_license: pkg.name,
    enrollment_fee: enrollmentFee.toFixed(2),
    included_classes: includedClasses,
    completed_classes: student.completed_classes,
    extra_classes_count: extraClasses,
    extra_classes_cost: extraClassesCost.toFixed(2),
    total_exams_count: totalExams,
    total_exams_cost: totalExamsCost.toFixed(2),
    subtotal_amount: subtotal.toFixed(2),
    vat_percentage: '21%',
    vat_amount: vatAmount.toFixed(2),
    total_with_vat: totalWithVat.toFixed(2),
    advances_paid: advances.toFixed(2),
    pending_balance: pending.toFixed(2),
  }
}

export const mockDriveStore = {
  getHealth(): HealthStatus {
    return {
      service: 'NainDrive Gateway',
      version: '2.4.0',
      architecture: 'Clean Architecture (In-Memory Engine)',
      status: 'healthy',
      transport: 'In-Memory Client Engine',
    }
  },

  getDashboard(): KPIDashboardSummary {
    let totalGross = 0
    let totalVat = 0
    let totalPending = 0
    let totalLessons = 0
    const licenseDist: Record<string, number> = {}

    for (const s of students) {
      const inv = calculateInvoiceForStudent(s)
      totalGross += Number(inv.total_with_vat)
      totalVat += Number(inv.vat_amount)
      totalPending += Number(inv.pending_balance)
      totalLessons += s.completed_classes

      const lic = s.target_license
      licenseDist[lic] = (licenseDist[lic] || 0) + 1
    }

    const studentCount = students.length
    const instructorCount = instructors.length
    const avgLessons =
      studentCount > 0 ? Math.round((totalLessons / studentCount) * 10) / 10 : 0

    return {
      total_gross: Math.round(totalGross * 100) / 100,
      total_vat: Math.round(totalVat * 100) / 100,
      total_pending: Math.round(totalPending * 100) / 100,
      completed_lessons_sum: totalLessons,
      license_distribution: licenseDist,
      total_students: studentCount,
      total_instructors: instructorCount,
      average_lessons_per_student: avgLessons,
    }
  },

  getStudents(): Student[] {
    return JSON.parse(JSON.stringify(students))
  },

  getStudent(dni: string): Student {
    const s = students.find((x) => x.dni.toUpperCase() === dni.toUpperCase())
    if (!s) throw new Error(`Alumno con DNI ${dni} no encontrado.`)
    return JSON.parse(JSON.stringify(s))
  },

  createStudent(payload: NewStudentPayload): Student {
    const cleanDni = payload.dni.trim().toUpperCase()
    if (students.some((s) => s.dni === cleanDni)) {
      throw new Error(`Ya existe un alumno registrado con el DNI ${cleanDni}.`)
    }

    const nextIdx = students.length + 1
    const regNum = `EXP-2026-${String(nextIdx).padStart(3, '0')}`

    const newStudent: Student = {
      registration_number: regNum,
      dni: cleanDni,
      first_name: payload.first_name.trim(),
      last_name: payload.last_name.trim(),
      phone: payload.phone.trim(),
      target_license: payload.target_license,
      assigned_instructor_id: 'INST-01',
      completed_classes: 0,
      theoretical_exams_count: 0,
      practical_exams_count: 0,
      total_advances_paid: Number(payload.total_advances_paid) || 0,
    }

    students.push(newStudent)
    return JSON.parse(JSON.stringify(newStudent))
  },

  deleteStudent(dni: string): void {
    const idx = students.findIndex((x) => x.dni.toUpperCase() === dni.toUpperCase())
    if (idx !== -1) {
      students.splice(idx, 1)
    }
  },

  addClasses(dni: string, count: number): Student {
    const s = students.find((x) => x.dni.toUpperCase() === dni.toUpperCase())
    if (!s) throw new Error(`Alumno con DNI ${dni} no encontrado.`)
    s.completed_classes += count
    return JSON.parse(JSON.stringify(s))
  },

  registerExam(dni: string, examType: 'THEORETICAL' | 'PRACTICAL'): Student {
    const s = students.find((x) => x.dni.toUpperCase() === dni.toUpperCase())
    if (!s) throw new Error(`Alumno con DNI ${dni} no encontrado.`)
    if (examType === 'THEORETICAL') {
      s.theoretical_exams_count += 1
    } else {
      s.practical_exams_count += 1
    }
    return JSON.parse(JSON.stringify(s))
  },

  recordAdvance(dni: string, amount: number): Student {
    const s = students.find((x) => x.dni.toUpperCase() === dni.toUpperCase())
    if (!s) throw new Error(`Alumno con DNI ${dni} no encontrado.`)
    s.total_advances_paid =
      Math.round((Number(s.total_advances_paid) + Number(amount)) * 100) / 100
    return JSON.parse(JSON.stringify(s))
  },

  getInvoice(dni: string): InvoiceCalculation {
    const s = this.getStudent(dni)
    return calculateInvoiceForStudent(s)
  },

  getInvoiceHtmlUrl(dni: string): string {
    const inv = this.getInvoice(dni)
    const html = `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Factura Oficial - ${inv.student_name}</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 2rem; color: #1e293b; max-width: 800px; margin: 0 auto; }
  .header { display: flex; justify-content: space-between; border-bottom: 2px solid #3b82f6; padding-bottom: 1rem; margin-bottom: 2rem; }
  .brand { font-size: 1.5rem; font-weight: bold; color: #1e40af; }
  .inv-num { font-size: 1.25rem; font-weight: 600; color: #64748b; }
  .table { width: 100%; border-collapse: collapse; margin-top: 1.5rem; }
  .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #e2e8f0; }
  .table th { background: #f8fafc; font-weight: 600; }
  .total-row { font-size: 1.25rem; font-weight: bold; color: #0f172a; }
  .footer { margin-top: 3rem; font-size: 0.85rem; color: #94a3b8; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 1rem; }
  @media print { body { padding: 0; } }
</style>
</head>
<body>
<div class="header">
  <div>
    <div class="brand">NAINDRIVE · Autoescuela Central</div>
    <div>C/ Gran Vía 42, 28013 Madrid · CIF B-12345678</div>
  </div>
  <div style="text-align: right;">
    <div class="inv-num">${inv.invoice_number}</div>
    <div>Fecha: ${inv.invoice_date}</div>
  </div>
</div>
<div>
  <strong>Cliente:</strong> ${inv.student_name} (${inv.student_dni})<br>
  <strong>Permiso Oficial:</strong> ${inv.target_license}
</div>
<table class="table">
  <thead>
    <tr><th>Concepto</th><th>Cantidad</th><th>Precio Base</th><th>Importe</th></tr>
  </thead>
  <tbody>
    <tr><td>Matrícula y Clases Teóricas (Incluye ${inv.included_classes} clases prácticas)</td><td>1</td><td>${inv.enrollment_fee} €</td><td>${inv.enrollment_fee} €</td></tr>
    <tr><td>Clases Prácticas Extraordinarias</td><td>${inv.extra_classes_count}</td><td>32,50 €</td><td>${inv.extra_classes_cost} €</td></tr>
    <tr><td>Tasas Oficiales DGT Exámenes</td><td>${inv.total_exams_count}</td><td>94,05 €</td><td>${inv.total_exams_cost} €</td></tr>
    <tr><td colspan="3" style="text-align: right; font-weight: 600;">Base Imponible:</td><td>${inv.subtotal_amount} €</td></tr>
    <tr><td colspan="3" style="text-align: right; font-weight: 600;">IVA (21%):</td><td>${inv.vat_amount} €</td></tr>
    <tr class="total-row"><td colspan="3" style="text-align: right;">Total Factura con IVA:</td><td style="color: #2563eb;">${inv.total_with_vat} €</td></tr>
    <tr><td colspan="3" style="text-align: right; color: #10b981;">Anticipos y Entregas a Cuenta:</td><td style="color: #10b981;">-${inv.advances_paid} €</td></tr>
    <tr class="total-row"><td colspan="3" style="text-align: right;">Saldo Pendiente de Abono:</td><td style="color: #e11d48;">${inv.pending_balance} €</td></tr>
  </tbody>
</table>
<div class="footer">
  Factura oficial expedida con Clean Architecture y validación de tipos determinista. Documento válido para justificación tributaria y contable.
</div>
</body>
</html>`
    const blob = new Blob([html], { type: 'text/html' })
    return URL.createObjectURL(blob)
  },

  getAppointments(): DgtExamAppointment[] {
    return JSON.parse(JSON.stringify(appointments))
  },

  scheduleAppointment(dni: string, payload: ScheduleDgtPayload): DgtExamAppointment {
    const s = this.getStudent(dni)
    const nextIdx = appointments.length + 1
    const appt: DgtExamAppointment = {
      appointment_id: `DGT-2026-${String(nextIdx).padStart(3, '0')}`,
      student_dni: s.dni,
      exam_type: payload.exam_type,
      appointment_date: payload.appointment_date,
      center_location: payload.center_location || 'Centro de Examenes DGT Madrid-Mostoles',
      status: 'SCHEDULED',
    }
    appointments.push(appt)
    return JSON.parse(JSON.stringify(appt))
  },

  getInstructors(): Instructor[] {
    return JSON.parse(JSON.stringify(instructors))
  },

  recordFuel(instructorId: string, amount: number): Instructor {
    const inst = instructors.find((i) => i.instructor_id === instructorId)
    if (!inst) throw new Error(`Instructor ${instructorId} no encontrado.`)
    inst.total_fuel_expenses =
      Math.round((Number(inst.total_fuel_expenses) + Number(amount)) * 100) / 100
    return JSON.parse(JSON.stringify(inst))
  },

  getPackages(): LicensePackage[] {
    return JSON.parse(JSON.stringify(packages))
  },

  reset(): { status: string; message: string } {
    packages = JSON.parse(JSON.stringify(INITIAL_PACKAGES))
    instructors = JSON.parse(JSON.stringify(INITIAL_INSTRUCTORS))
    students = JSON.parse(JSON.stringify(INITIAL_STUDENTS))
    appointments = JSON.parse(JSON.stringify(INITIAL_APPOINTMENTS))
    return {
      status: 'success',
      message: 'Base de datos restaurada al estado sintético de fábrica con éxito.',
    }
  },
}
