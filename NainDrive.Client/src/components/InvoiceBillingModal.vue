<script setup lang="ts">
import { ref, watch } from 'vue'
import { fetchInvoice, getInvoicePdfDownloadUrl } from '../services/api'
import type { InvoiceCalculation } from '../types/contracts'

const props = defineProps<{
  dni: string | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const invoice = ref<InvoiceCalculation | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const downloadingPdf = ref(false)

async function loadInvoice(targetDni: string) {
  loading.value = true
  error.value = null
  invoice.value = null
  try {
    invoice.value = await fetchInvoice(targetDni)
  } catch (err: any) {
    error.value = err.message || 'Error al calcular la factura oficial.'
  } finally {
    loading.value = false
  }
}

watch(
  () => props.dni,
  (newDni) => {
    if (newDni) {
      loadInvoice(newDni)
    } else {
      invoice.value = null
      error.value = null
    }
  },
  { immediate: true }
)

function formatEuro(val: number | string | undefined | null): string {
  if (val === undefined || val === null) return '0,00 €'
  const num = typeof val === 'string' ? parseFloat(val) : val
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(num || 0)
}

function handleDownloadPdf() {
  if (!props.dni) return
  downloadingPdf.value = true
  const downloadUrl = getInvoicePdfDownloadUrl(props.dni)
  const a = document.createElement('a')
  a.href = downloadUrl
  a.setAttribute('download', `Factura_${props.dni}.pdf`)
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  setTimeout(() => {
    downloadingPdf.value = false
  }, 1000)
}
</script>

<template>
  <div v-if="props.dni" class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card">
      <!-- Modal Header -->
      <div class="modal-header">
        <div>
          <div class="modal-tag">Desglose Fiscal Oficial · IVA 21%</div>
          <h2 class="modal-title">
            Factura y Liquidación
            <span v-if="invoice" class="invoice-num">#{{ invoice.invoice_number }}</span>
          </h2>
        </div>
        <button class="btn-icon" @click="emit('close')" title="Cerrar">&times;</button>
      </div>

      <!-- Loading / Error States -->
      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p class="state-msg">Calculando desglose fiscal determinista según ADR-0003...</p>
      </div>

      <div v-else-if="error" class="state-container error-state">
        <div class="state-title">Error en Liquidación</div>
        <p class="state-msg">{{ error }}</p>
        <button class="btn btn-secondary" @click="props.dni && loadInvoice(props.dni)">Reintentar</button>
      </div>

      <!-- Invoice Details Body -->
      <div v-else-if="invoice" class="modal-body">
        <!-- Student Info Strip -->
        <div class="invoice-student-strip">
          <div>
            <div class="strip-label">Alumno / Titular</div>
            <div class="strip-val">{{ invoice.student_name }}</div>
          </div>
          <div>
            <div class="strip-label">DNI / NIE</div>
            <div class="strip-val font-mono">{{ invoice.student_dni }}</div>
          </div>
          <div>
            <div class="strip-label">Permiso Solicitado</div>
            <div class="badge badge-accent">Permiso {{ invoice.target_license }}</div>
          </div>
          <div>
            <div class="strip-label">Fecha Emisión</div>
            <div class="strip-val font-mono">{{ invoice.invoice_date }}</div>
          </div>
        </div>

        <!-- Breakdown Table -->
        <div class="table-container">
          <table class="table invoice-table">
            <thead>
              <tr>
                <th>Concepto Facturable</th>
                <th class="text-center">Unidades</th>
                <th class="text-right">Base Imponible</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div class="item-name">Matrícula & Material Didáctico Permiso {{ invoice.target_license }}</div>
                  <div class="item-sub">Incluye {{ invoice.included_classes }} clases prácticas reglamentarias</div>
                </td>
                <td class="text-center">1 pack</td>
                <td class="text-right font-mono">{{ formatEuro(invoice.enrollment_fee) }}</td>
              </tr>
              <tr>
                <td>
                  <div class="item-name">Clases Prácticas de Perfeccionamiento</div>
                  <div class="item-sub">
                    {{ invoice.completed_classes }} realizadas vs {{ invoice.included_classes }} en pack ({{ invoice.extra_classes_count }} extra)
                  </div>
                </td>
                <td class="text-center">{{ invoice.extra_classes_count }}</td>
                <td class="text-right font-mono">{{ formatEuro(invoice.extra_classes_cost) }}</td>
              </tr>
              <tr>
                <td>
                  <div class="item-name">Tasas de Examen DGT y Gestión Administrativa</div>
                  <div class="item-sub">{{ invoice.total_exams_count }} convocatorias gestionadas</div>
                </td>
                <td class="text-center">{{ invoice.total_exams_count }}</td>
                <td class="text-right font-mono">{{ formatEuro(invoice.total_exams_cost) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Fiscal Summary Grid -->
        <div class="fiscal-summary-grid">
          <div class="fiscal-row">
            <span class="fiscal-label">Subtotal Base Imponible:</span>
            <span class="fiscal-val font-mono">{{ formatEuro(invoice.subtotal_amount) }}</span>
          </div>
          <div class="fiscal-row">
            <span class="fiscal-label">Impuesto sobre el Valor Añadido (IVA 21%):</span>
            <span class="fiscal-val font-mono">{{ formatEuro(invoice.vat_amount) }}</span>
          </div>
          <div class="fiscal-row total-row">
            <span class="fiscal-label">Total Bruto Facturable:</span>
            <span class="fiscal-val font-mono text-cyan">{{ formatEuro(invoice.total_with_vat) }}</span>
          </div>
          <div class="fiscal-row">
            <span class="fiscal-label">Entregas a Cuenta y Anticipos Recibidos:</span>
            <span class="fiscal-val font-mono text-emerald">- {{ formatEuro(invoice.advances_paid) }}</span>
          </div>
          <div
            class="fiscal-row balance-row"
            :class="{ 'settled': Number(invoice.pending_balance) <= 0, 'pending': Number(invoice.pending_balance) > 0 }"
          >
            <span class="fiscal-label">SALDO PENDIENTE DE COBRO:</span>
            <span class="fiscal-val font-mono">{{ formatEuro(invoice.pending_balance) }}</span>
          </div>
        </div>

        <!-- PDF Zero-Disk Generation Notice & Actions -->
        <div class="modal-footer">
          <div class="security-notice">
            <svg class="w-4 h-4 text-emerald" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>Generación en memoria (zero-disk write) certificada por ReportLab & FastAPI</span>
          </div>
          <div class="footer-actions">
            <button class="btn btn-secondary" @click="emit('close')">Cerrar</button>
            <button
              class="btn btn-primary"
              :disabled="downloadingPdf"
              @click="handleDownloadPdf"
            >
              <svg class="btn-icon-svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>{{ downloadingPdf ? 'Generando PDF...' : 'Descargar Factura Oficial PDF' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1.5rem;
}

.modal-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-modal);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--bg-card-header);
}

.modal-tag {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-light);
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.modal-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.invoice-num {
  font-size: 0.95rem;
  font-family: monospace;
  color: var(--text-muted);
  font-weight: 500;
}

.btn-icon {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.75rem;
  cursor: pointer;
  line-height: 1;
  padding: 0 0.5rem;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.btn-icon:hover {
  color: var(--text-main);
  background: var(--bg-hover);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.invoice-student-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
}

.strip-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.2rem;
}

.strip-val {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-main);
}

.invoice-table .item-name {
  font-weight: 600;
  color: var(--text-main);
}

.invoice-table .item-sub {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 0.15rem;
}

.fiscal-summary-grid {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--border-color);
  padding: 1.25rem;
  border-radius: var(--radius-md);
}

.fiscal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.fiscal-row.total-row {
  padding-top: 0.6rem;
  border-top: 1px dashed var(--border-color);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-main);
}

.fiscal-row.balance-row {
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 1.1rem;
  font-weight: 800;
  margin-top: 0.35rem;
}

.fiscal-row.balance-row.pending {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

.fiscal-row.balance-row.settled {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.text-cyan {
  color: #38bdf8;
}

.text-emerald {
  color: #34d399;
}

.modal-footer {
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.security-notice {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.security-notice .w-4 {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-icon-svg {
  width: 1rem;
  height: 1rem;
}

.state-container {
  padding: 3rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  text-align: center;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(56, 189, 248, 0.15);
  border-top-color: var(--accent-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-title {
  font-weight: 700;
  color: var(--danger-color);
}

.state-msg {
  color: var(--text-muted);
  font-size: 0.88rem;
  max-width: 400px;
}
</style>
