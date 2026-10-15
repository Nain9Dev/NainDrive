<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchInstructors, recordFuelExpense, fetchPackages } from '../services/api'
import type { Instructor, LicensePackage } from '../types/contracts'

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const instructors = ref<Instructor[]>([])
const packages = ref<LicensePackage[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// Fuel expense modal/inline state
const selectedInstructor = ref<Instructor | null>(null)
const fuelAmount = ref<number>(50)
const loggingFuel = ref(false)
const fuelError = ref<string | null>(null)
const fuelSuccess = ref<string | null>(null)

async function loadData() {
  loading.value = true
  error.value = null
  try {
    const [insts, pcks] = await Promise.all([fetchInstructors(), fetchPackages()])
    instructors.value = insts
    packages.value = pcks
  } catch (err: any) {
    error.value = err.message || 'Error al cargar profesores y flota de vehículos.'
  } finally {
    loading.value = false
  }
}

function isItvExpired(dateStr: string): boolean {
  if (!dateStr) return false
  const exp = new Date(dateStr)
  return exp.getTime() < Date.now()
}

function formatEuro(val: number | string | undefined | null): string {
  if (val === undefined || val === null) return '0,00 €'
  const num = typeof val === 'string' ? parseFloat(val) : val
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(num || 0)
}

function openFuelModal(instructor: Instructor) {
  selectedInstructor.value = instructor
  fuelAmount.value = 50
  fuelError.value = null
  fuelSuccess.value = null
}

function closeFuelModal() {
  selectedInstructor.value = null
  fuelError.value = null
  fuelSuccess.value = null
}

async function handleRecordFuel() {
  if (!selectedInstructor.value) return
  if (!fuelAmount.value || fuelAmount.value <= 0) {
    fuelError.value = 'El importe de repostaje debe ser superior a 0 €.'
    return
  }

  loggingFuel.value = true
  fuelError.value = null
  fuelSuccess.value = null

  try {
    const updated = await recordFuelExpense(selectedInstructor.value.instructor_id, fuelAmount.value)
    fuelSuccess.value = `Gasto de ${formatEuro(fuelAmount.value)} registrado en ${updated.assigned_vehicle_plate}.`
    await loadData()
    emit('refresh')
    setTimeout(() => {
      closeFuelModal()
    }, 1200)
  } catch (err: any) {
    fuelError.value = err.message || 'Error al imputar gasto de combustible.'
  } finally {
    loggingFuel.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="fleet-page-grid">
    <!-- Fleet & Instructors Card -->
    <div class="card instructors-card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Flota de Vehículos y Cuadro Docente</h2>
          <p class="card-subtitle">
            Control de inspecciones técnicas de vehículos (ITV), vehículos de doble mando y consumo de carburante.
          </p>
        </div>
        <button class="btn btn-secondary btn-sm" @click="loadData" :disabled="loading">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Actualizar
        </button>
      </div>

      <div v-if="loading && instructors.length === 0" class="state-container">
        <div class="spinner"></div>
        <p class="state-msg">Cargando flota de vehículos...</p>
      </div>

      <div v-else-if="error" class="state-container error-state">
        <p class="state-msg">{{ error }}</p>
        <button class="btn btn-secondary btn-sm" @click="loadData">Reintentar</button>
      </div>

      <div v-else class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Profesor / Instructor</th>
              <th>Vehículo & Matrícula</th>
              <th>Vigencia ITV</th>
              <th class="text-right">Gasto Carburante</th>
              <th class="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inst in instructors" :key="inst.instructor_id">
              <td>
                <div class="font-semibold text-main">{{ inst.full_name }}</div>
                <div class="text-xs text-muted font-mono">ID: {{ inst.instructor_id }}</div>
              </td>
              <td>
                <div class="font-semibold text-main">{{ inst.vehicle_model }}</div>
                <div class="plate-badge font-mono">{{ inst.assigned_vehicle_plate }}</div>
              </td>
              <td>
                <div v-if="isItvExpired(inst.itv_expiration_date)" class="badge badge-danger">
                  Caducada ({{ inst.itv_expiration_date }})
                </div>
                <div v-else class="badge badge-success">
                  En vigor ({{ inst.itv_expiration_date }})
                </div>
              </td>
              <td class="text-right font-mono font-semibold text-main">
                {{ formatEuro(inst.total_fuel_expenses) }}
              </td>
              <td class="text-right">
                <button
                  class="btn btn-secondary btn-sm"
                  @click="openFuelModal(inst)"
                  title="Registrar ticket de gasóleo/gasolina"
                >
                  <svg class="icon-sm text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Repostaje
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Official License Packages Tariff Card -->
    <div class="card tariffs-card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Tarifas Oficiales por Permiso DGT</h2>
          <p class="card-subtitle">
            Estructura de precios homologada, clases prácticas reglamentarias y tasas oficiales.
          </p>
        </div>
      </div>

      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Permiso</th>
              <th class="text-right">Matrícula Pack</th>
              <th class="text-center">Prácticas Incluidas</th>
              <th class="text-right">Clase Extra</th>
              <th class="text-right">Tasa Examen DGT</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pck in packages" :key="pck.package_code">
              <td>
                <div class="font-semibold text-main">{{ pck.name }}</div>
                <div class="text-xs font-mono text-accent">{{ pck.package_code }}</div>
              </td>
              <td class="text-right font-mono font-semibold text-accent">
                {{ formatEuro(pck.enrollment_fee) }}
              </td>
              <td class="text-center font-mono">
                <span class="badge badge-accent">{{ pck.included_practical_classes }} clases</span>
              </td>
              <td class="text-right font-mono">
                {{ formatEuro(pck.extra_class_price) }}
              </td>
              <td class="text-right font-mono text-muted">
                {{ formatEuro(pck.dgt_exam_fee) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Record Fuel Modal -->
    <div v-if="selectedInstructor" class="modal-backdrop" @click.self="closeFuelModal">
      <div class="modal-card small-modal">
        <div class="modal-header">
          <div>
            <div class="modal-tag">Control de Gasto Operativo</div>
            <h3 class="modal-title">Registrar Factura Combustible</h3>
          </div>
          <button class="btn-icon" @click="closeFuelModal">&times;</button>
        </div>

        <div class="modal-body">
          <div class="vehicle-info-banner">
            <div>
              <span class="text-muted text-xs">Instructor:</span>
              <strong class="ml-1 text-main">{{ selectedInstructor.full_name }}</strong>
            </div>
            <div>
              <span class="text-muted text-xs">Vehículo:</span>
              <span class="plate-badge ml-1 font-mono">{{ selectedInstructor.assigned_vehicle_plate }}</span>
            </div>
          </div>

          <div v-if="fuelError" class="alert alert-danger">{{ fuelError }}</div>
          <div v-if="fuelSuccess" class="alert alert-success">{{ fuelSuccess }}</div>

          <div class="form-group">
            <label class="form-label" for="fuel-amount">Importe del Ticket (€ con IVA incluido)</label>
            <input
              id="fuel-amount"
              v-model.number="fuelAmount"
              type="number"
              step="0.01"
              min="1"
              class="form-input font-mono text-lg"
              placeholder="Ej. 65.50"
            />
          </div>

          <div class="modal-actions">
            <button class="btn btn-secondary" @click="closeFuelModal" :disabled="loggingFuel">
              Cancelar
            </button>
            <button class="btn btn-primary" @click="handleRecordFuel" :disabled="loggingFuel">
              {{ loggingFuel ? 'Guardando...' : 'Confirmar Gasto' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fleet-page-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.plate-badge {
  display: inline-block;
  background: #0f172a;
  border: 1px solid var(--border-color);
  color: #38bdf8;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: var(--radius-sm);
  letter-spacing: 0.05em;
  margin-top: 0.15rem;
}

.w-4 {
  width: 1rem;
  height: 1rem;
}

.icon-sm {
  width: 0.875rem;
  height: 0.875rem;
}

.text-xs {
  font-size: 0.75rem;
}

.ml-1 {
  margin-left: 0.25rem;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
}

.modal-card.small-modal {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 480px;
  overflow: hidden;
}

.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--bg-card-header);
}

.modal-tag {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-light);
  font-weight: 700;
  margin-bottom: 0.2rem;
}

.modal-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-main);
  margin: 0;
}

.btn-icon {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.vehicle-info-banner {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-input {
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-main);
  padding: 0.65rem 0.85rem;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
}

.alert-danger {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.alert-success {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.state-container {
  padding: 2.5rem 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  text-align: center;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid rgba(56, 189, 248, 0.15);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-msg {
  font-size: 0.85rem;
  color: var(--text-muted);
}
</style>
