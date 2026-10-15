<script setup lang="ts">
import { ref, computed } from 'vue'
import type { NewStudentPayload, Student } from '../types/contracts'
import {
  addStudentClasses,
  createStudent,
  deleteStudent,
  recordStudentAdvance,
  registerStudentExam,
} from '../services/api'

const props = defineProps<{
  students: Student[]
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'viewInvoice', dni: string): void
}>()

// Filter / Search
const searchQuery = ref('')
const filteredStudents = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.students
  return props.students.filter(
    (s) =>
      s.dni.toLowerCase().includes(q) ||
      s.first_name.toLowerCase().includes(q) ||
      s.last_name.toLowerCase().includes(q) ||
      s.registration_number.toLowerCase().includes(q)
  )
})

// Modulo 23 checksum calculation helper for live feedback
const DNI_LETTERS = 'TRWAGMYFPDXBNJZSQVHLCKE'
function checkDniValidity(raw: string): { valid: boolean; reason: string } {
  const clean = raw.trim().toUpperCase().replace(/[-\s]/g, '')
  if (!clean) return { valid: false, reason: 'Introduce el DNI o NIE' }

  let digits = clean
  if (clean.startsWith('X')) digits = '0' + clean.slice(1)
  else if (clean.startsWith('Y')) digits = '1' + clean.slice(1)
  else if (clean.startsWith('Z')) digits = '2' + clean.slice(1)

  if (!/^\d{8}[A-Z]$/.test(digits)) {
    return { valid: false, reason: 'Formato esperado: 8 números y letra de control' }
  }

  const num = parseInt(digits.slice(0, 8), 10)
  const letter = digits.slice(8)
  const expected = DNI_LETTERS[num % 23]

  if (letter !== expected) {
    return { valid: false, reason: `Letra incorrecta: calculada '${expected}', introducida '${letter}'` }
  }

  return { valid: true, reason: `Checksum Módulo 23 correcto (${expected})` }
}

// Enrollment Form
const showEnrollModal = ref(false)
const newStudent = ref<NewStudentPayload>({
  dni: '',
  first_name: '',
  last_name: '',
  phone: '600111222',
  target_license: 'B',
  total_advances_paid: 100,
})

const dniFeedback = computed(() => checkDniValidity(newStudent.value.dni))
const isSubmitting = ref(false)
const formError = ref<string | null>(null)

async function handleEnroll() {
  if (!dniFeedback.value.valid) {
    formError.value = dniFeedback.value.reason
    return
  }
  isSubmitting.value = true
  formError.value = null
  try {
    await createStudent(newStudent.value)
    showEnrollModal.value = false
    newStudent.value = {
      dni: '',
      first_name: '',
      last_name: '',
      phone: '600111222',
      target_license: 'B',
      total_advances_paid: 100,
    }
    emit('refresh')
  } catch (err: unknown) {
    formError.value = err instanceof Error ? err.message : 'Error desconocido al matricular'
  } finally {
    isSubmitting.value = false
  }
}

// Quick Operations Modal
const activeStudent = ref<Student | null>(null)
const opType = ref<'classes' | 'advance' | 'exam' | null>(null)
const classesToAdd = ref(2)
const advanceToAdd = ref(50)
const examTypeToRegister = ref<'THEORETICAL' | 'PRACTICAL'>('PRACTICAL')

function openOp(student: Student, type: 'classes' | 'advance' | 'exam') {
  activeStudent.value = student
  opType.value = type
}

function closeOp() {
  activeStudent.value = null
  opType.value = null
}

async function handleExecuteOp() {
  if (!activeStudent.value) return
  isSubmitting.value = true
  try {
    if (opType.value === 'classes') {
      await addStudentClasses(activeStudent.value.dni, classesToAdd.value)
    } else if (opType.value === 'advance') {
      await recordStudentAdvance(activeStudent.value.dni, advanceToAdd.value)
    } else if (opType.value === 'exam') {
      await registerStudentExam(activeStudent.value.dni, examTypeToRegister.value)
    }
    closeOp()
    emit('refresh')
  } catch (err: unknown) {
    alert(err instanceof Error ? err.message : 'Error en la operación')
  } finally {
    isSubmitting.value = false
  }
}

async function handleDelete(student: Student) {
  if (!confirm(`¿Eliminar al alumno ${student.first_name} ${student.last_name} (${student.dni})?`)) return
  try {
    await deleteStudent(student.dni)
    emit('refresh')
  } catch (err) {
    alert('Error al eliminar alumno')
  }
}
</script>

<template>
  <div class="glass-panel manager-panel">
    <!-- Header with Search & Enroll Button -->
    <div class="manager-header">
      <div>
        <h3 class="display-title manager-title">Directorio de Alumnos & Expedientes</h3>
        <p class="manager-sub">
          Control de clases prácticas impartidas, convocatorias de examen y depósitos a cuenta.
        </p>
      </div>

      <div class="header-actions">
        <input
          v-model="searchQuery"
          type="text"
          class="form-input search-input font-mono"
          placeholder="Buscar por DNI o nombre..."
        />
        <button
          type="button"
          class="btn btn-primary"
          @click="showEnrollModal = true"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
            <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          Nuevo Alumno
        </button>
      </div>
    </div>

    <!-- Students Table -->
    <div class="table-wrapper">
      <table class="students-table">
        <thead>
          <tr>
            <th>Expediente</th>
            <th>DNI / NIE</th>
            <th>Alumno</th>
            <th>Permiso</th>
            <th>Clases Dadas</th>
            <th>Exámenes</th>
            <th>Anticipos</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filteredStudents" :key="s.dni">
            <td class="font-mono text-dim">{{ s.registration_number }}</td>
            <td class="font-mono font-bold">{{ s.dni }}</td>
            <td>
              <div class="student-name">{{ s.first_name }} {{ s.last_name }}</div>
              <div class="student-phone font-mono">{{ s.phone }}</div>
            </td>
            <td>
              <span class="badge" :class="s.target_license === 'B' ? 'badge-blue' : s.target_license === 'A2' ? 'badge-emerald' : 'badge-amber'">
                Permiso {{ s.target_license }}
              </span>
            </td>
            <td class="font-mono">
              <strong>{{ s.completed_classes }}</strong> clases
            </td>
            <td>
              <div class="exam-badges font-mono">
                <span class="badge badge-blue" title="Exámenes teóricos">T: {{ s.theoretical_exams_count }}</span>
                <span class="badge badge-emerald" title="Exámenes prácticos">P: {{ s.practical_exams_count }}</span>
              </div>
            </td>
            <td class="font-mono font-bold text-emerald">
              {{ typeof s.total_advances_paid === 'number' ? s.total_advances_paid.toFixed(2) : s.total_advances_paid }} €
            </td>
            <td class="text-right">
              <div class="row-actions">
                <button
                  type="button"
                  class="btn btn-secondary btn-sm"
                  title="Calcular y descargar factura oficial"
                  @click="emit('viewInvoice', s.dni)"
                >
                  Factura
                </button>
                <button
                  type="button"
                  class="btn btn-ghost btn-sm"
                  title="Añadir clases prácticas"
                  @click="openOp(s, 'classes')"
                >
                  + Clases
                </button>
                <button
                  type="button"
                  class="btn btn-ghost btn-sm"
                  title="Añadir pago a cuenta"
                  @click="openOp(s, 'advance')"
                >
                  + Anticipo
                </button>
                <button
                  type="button"
                  class="btn btn-ghost btn-sm"
                  title="Registrar convocatoria de examen"
                  @click="openOp(s, 'exam')"
                >
                  + Examen
                </button>
                <button
                  type="button"
                  class="action-del"
                  title="Eliminar expediente"
                  @click="handleDelete(s)"
                >
                  &times;
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Enrollment Modal -->
    <div v-if="showEnrollModal" class="modal-backdrop" @click.self="showEnrollModal = false">
      <div class="glass-panel modal-card" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3 class="display-title modal-title">Matricular Nuevo Alumno</h3>
          <button type="button" class="close-x" @click="showEnrollModal = false">&times;</button>
        </div>

        <div v-if="formError" class="alert alert-error">
          {{ formError }}
        </div>

        <form @submit.prevent="handleEnroll" class="modal-form">
          <div class="form-group">
            <label class="form-label" for="inputDni">DNI / NIE (Verificación Módulo 23)*</label>
            <input
              id="inputDni"
              v-model="newStudent.dni"
              type="text"
              required
              class="form-input font-mono"
              placeholder="12345678Z"
            />
            <div
              v-if="newStudent.dni"
              class="validation-hint"
              :class="dniFeedback.valid ? 'hint-valid' : 'hint-invalid'"
            >
              {{ dniFeedback.reason }}
            </div>
          </div>

          <div class="form-row form-row-2">
            <div class="form-group">
              <label class="form-label" for="inputFirst">Nombre*</label>
              <input id="inputFirst" v-model="newStudent.first_name" type="text" required class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label" for="inputLast">Apellidos*</label>
              <input id="inputLast" v-model="newStudent.last_name" type="text" required class="form-input" />
            </div>
          </div>

          <div class="form-row form-row-2">
            <div class="form-group">
              <label class="form-label" for="inputPhone">Teléfono</label>
              <input id="inputPhone" v-model="newStudent.phone" type="text" class="form-input font-mono" />
            </div>
            <div class="form-group">
              <label class="form-label" for="inputLicense">Permiso Objetivo</label>
              <select id="inputLicense" v-model="newStudent.target_license" class="form-select font-mono">
                <option value="B">Permiso B (Turismo)</option>
                <option value="A2">Permiso A2 (Motocicleta)</option>
                <option value="C">Permiso C (Camión)</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label" for="inputAdv">Anticipo Inicial en €</label>
            <input id="inputAdv" v-model.number="newStudent.total_advances_paid" type="number" min="0" step="10" class="form-input font-mono" />
          </div>

          <div class="modal-foot">
            <button type="button" class="btn btn-secondary" @click="showEnrollModal = false">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !dniFeedback.valid">
              {{ isSubmitting ? 'Registrando...' : 'Matricular Alumno' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Operation Action Modal (Add Classes, Advance, Exam) -->
    <div v-if="activeStudent" class="modal-backdrop" @click.self="closeOp">
      <div class="glass-panel modal-card" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3 class="display-title modal-title">
            {{ opType === 'classes' ? 'Impartir Clases Prácticas' : opType === 'advance' ? 'Registrar Pago a Cuenta' : 'Registrar Convocatoria de Examen' }}
          </h3>
          <button type="button" class="close-x" @click="closeOp">&times;</button>
        </div>

        <p class="op-target">
          Expediente: <strong>{{ activeStudent.first_name }} {{ activeStudent.last_name }}</strong> ({{ activeStudent.dni }})
        </p>

        <div v-if="opType === 'classes'" class="form-group">
          <label class="form-label">Nº de Clases Prácticas Realizadas</label>
          <input v-model.number="classesToAdd" type="number" min="1" max="50" class="form-input font-mono" />
        </div>

        <div v-if="opType === 'advance'" class="form-group">
          <label class="form-label">Importe Abonado (€)</label>
          <input v-model.number="advanceToAdd" type="number" min="5" step="10" class="form-input font-mono" />
        </div>

        <div v-if="opType === 'exam'" class="form-group">
          <label class="form-label">Tipo de Convocatoria</label>
          <select v-model="examTypeToRegister" class="form-select font-mono">
            <option value="PRACTICAL">Examen Práctico de Circulación</option>
            <option value="THEORETICAL">Examen Teórico</option>
          </select>
        </div>

        <div class="modal-foot">
          <button type="button" class="btn btn-secondary" @click="closeOp">Cancelar</button>
          <button type="button" class="btn btn-primary" :disabled="isSubmitting" @click="handleExecuteOp">
            {{ isSubmitting ? 'Guardando...' : 'Confirmar Registro' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.manager-panel {
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.manager-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.manager-title {
  font-size: 1.25rem;
  color: var(--color-text-main);
  margin-bottom: 0.25rem;
}

.manager-sub {
  font-size: 0.85rem;
  color: var(--color-text-dim);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.search-input {
  min-width: 240px;
  padding: 0.5rem 0.75rem;
  font-size: 0.825rem;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: rgba(10, 15, 33, 0.6);
}

.students-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  text-align: left;
}

.students-table th {
  background: rgba(14, 21, 44, 0.9);
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--color-border);
}

.students-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.students-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.student-name {
  font-weight: 600;
  color: var(--color-text-main);
}

.student-phone {
  font-size: 0.75rem;
  color: var(--color-text-dim);
}

.exam-badges {
  display: flex;
  gap: 0.35rem;
}

.text-right {
  text-align: right;
}

.text-dim {
  color: var(--color-text-dim);
}

.text-emerald {
  color: var(--accent-emerald);
}

.font-bold {
  font-weight: 600;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.4rem;
}

.action-del {
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0 0.35rem;
  line-height: 1;
  transition: color var(--transition-fast);
}

.action-del:hover {
  color: var(--accent-rose);
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(4, 6, 14, 0.82);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-card {
  width: 100%;
  max-width: 540px;
  padding: 1.5rem;
  border: 1px solid var(--color-border-bright);
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.modal-title {
  font-size: 1.2rem;
  color: var(--color-text-main);
}

.close-x {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-foot {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.validation-hint {
  font-size: 0.725rem;
  font-weight: 600;
  margin-top: 0.2rem;
}

.hint-valid {
  color: var(--accent-emerald);
}

.hint-invalid {
  color: var(--accent-rose);
}

.alert-error {
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.3);
  color: #f43f5e;
  padding: 0.6rem 0.85rem;
  border-radius: var(--radius-md);
  font-size: 0.825rem;
  margin-bottom: 1rem;
}

.op-target {
  font-size: 0.875rem;
  color: var(--color-text-muted);
  margin-bottom: 1.25rem;
  background: rgba(255, 255, 255, 0.04);
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-sm);
}

@media (max-width: 860px) {
  .manager-header { flex-direction: column; }
  .header-actions { width: 100%; justify-content: space-between; }
  .search-input { min-width: 0; flex: 1; }
}
</style>
