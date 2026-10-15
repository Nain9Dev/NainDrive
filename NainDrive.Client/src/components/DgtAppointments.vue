<script setup lang="ts">
import { ref } from 'vue'
import type { DgtExamAppointment, DgtExamType, Student } from '../types/contracts'
import { scheduleDgtAppointment } from '../services/api'

const props = defineProps<{
  appointments: DgtExamAppointment[]
  students: Student[]
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const showScheduleModal = ref(false)
const selectedDni = ref(props.students[0]?.dni || '')
const selectedType = ref<DgtExamType>('PRACTICAL')
const appointmentDate = ref('20-12-2026')
const centerLocation = ref('Centro de Examenes DGT Madrid-Mostoles')
const isSubmitting = ref(false)
const errorNotice = ref<string | null>(null)

async function handleSchedule() {
  if (!selectedDni.value) return
  isSubmitting.value = true
  errorNotice.value = null
  try {
    await scheduleDgtAppointment(selectedDni.value, {
      exam_type: selectedType.value,
      appointment_date: appointmentDate.value,
      center_location: centerLocation.value,
    })
    showScheduleModal.value = false
    emit('refresh')
  } catch (err: unknown) {
    errorNotice.value = err instanceof Error ? err.message : 'Error al agendar cita DGT'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="glass-panel dgt-panel">
    <div class="dgt-header">
      <div>
        <div class="dgt-title-row">
          <span class="dgt-tag">DGT Oficial</span>
          <h3 class="display-title dgt-title">Convocatorias de Examen Tráfico</h3>
        </div>
        <p class="dgt-sub">
          Registro y persistencia de fechas oficiales de examen teórico y pruebas de circulación (REQ-004).
        </p>
      </div>

      <button
        type="button"
        class="btn btn-emerald btn-sm"
        @click="showScheduleModal = true"
      >
        <svg viewBox="0 0 20 20" fill="currentColor" width="14" height="14">
          <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Agendar Convocatoria DGT
      </button>
    </div>

    <!-- Table -->
    <div class="dgt-table-wrap">
      <table class="dgt-table">
        <thead>
          <tr>
            <th>ID Convocatoria</th>
            <th>DNI Alumno</th>
            <th>Modalidad</th>
            <th>Fecha Agendada</th>
            <th>Centro Oficial DGT</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="appointments.length === 0">
            <td colspan="6" class="empty-cell">No hay convocatorias DGT programadas.</td>
          </tr>
          <tr v-for="app in appointments" :key="app.appointment_id">
            <td class="font-mono text-dim">#{{ app.appointment_id }}</td>
            <td class="font-mono font-bold">{{ app.student_dni }}</td>
            <td>
              <span class="badge" :class="app.exam_type === 'PRACTICAL' ? 'badge-blue' : 'badge-amber'">
                {{ app.exam_type === 'PRACTICAL' ? 'Práctico Circulación' : 'Teórico Común' }}
              </span>
            </td>
            <td class="font-mono">{{ app.appointment_date }}</td>
            <td class="text-dim">{{ app.center_location }}</td>
            <td>
              <span class="badge" :class="app.status === 'PASSED' ? 'badge-emerald' : app.status === 'SCHEDULED' ? 'badge-blue' : 'badge-rose'">
                {{ app.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Schedule Modal -->
    <div v-if="showScheduleModal" class="modal-backdrop" @click.self="showScheduleModal = false">
      <div class="glass-panel modal-card" role="dialog" aria-modal="true">
        <div class="modal-head">
          <h3 class="display-title modal-title">Agendar Convocatoria Oficial DGT</h3>
          <button type="button" class="close-x" @click="showScheduleModal = false">&times;</button>
        </div>

        <div v-if="errorNotice" class="alert-error">{{ errorNotice }}</div>

        <form @submit.prevent="handleSchedule" class="modal-form">
          <div class="form-group">
            <label class="form-label">Alumno Candidato</label>
            <select v-model="selectedDni" required class="form-select font-mono">
              <option v-for="s in students" :key="s.dni" :value="s.dni">
                {{ s.first_name }} {{ s.last_name }} ({{ s.dni }}) — {{ s.completed_classes }} clases
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Tipo de Prueba</label>
            <select v-model="selectedType" class="form-select font-mono">
              <option value="PRACTICAL">Práctico de Circulación en Vía Abierta</option>
              <option value="THEORETICAL">Teórico Específico / Común</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Fecha de Convocatoria (DD-MM-YYYY)</label>
            <input v-model="appointmentDate" type="text" required class="form-input font-mono" placeholder="20-12-2026" />
          </div>

          <div class="form-group">
            <label class="form-label">Centro de Exámenes</label>
            <input v-model="centerLocation" type="text" class="form-input" />
          </div>

          <div class="modal-foot">
            <button type="button" class="btn btn-secondary" @click="showScheduleModal = false">Cancelar</button>
            <button type="submit" class="btn btn-emerald" :disabled="isSubmitting">
              {{ isSubmitting ? 'Agendando...' : 'Guardar Cita DGT' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dgt-panel {
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.dgt-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.dgt-title-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.25rem;
}

.dgt-tag {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.dgt-title {
  font-size: 1.25rem;
  color: var(--color-text-main);
}

.dgt-sub {
  font-size: 0.85rem;
  color: var(--color-text-dim);
}

.dgt-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: rgba(10, 15, 33, 0.6);
}

.dgt-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  text-align: left;
}

.dgt-table th {
  background: rgba(14, 21, 44, 0.9);
  padding: 0.75rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid var(--color-border);
}

.dgt-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.empty-cell {
  text-align: center;
  color: var(--color-text-dim);
  padding: 1.5rem !important;
}

.text-dim { color: var(--color-text-dim); }
.font-bold { font-weight: 600; }

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
  max-width: 520px;
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

.modal-foot {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
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
</style>
