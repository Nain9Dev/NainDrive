<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '../AppIcon.vue'
import ProgressRing from '../ui/ProgressRing.vue'
import {
  addStudentClasses,
  deleteStudent,
  fetchInvoice,
  getInvoicePdfDownloadUrl,
  recordStudentAdvance,
  registerStudentExam,
} from '../../services/api'
import type { InvoiceCalculation, Student } from '../../types/contracts'
import { driveData } from '../../store/driveData'
import { useToast } from '../../composables/useToast'
import { formatEuro, initials, licenceClass, toNumber } from '../../utils/format'

type Action = 'classes' | 'advance' | 'exam'

const props = defineProps<{
  student: Student | null
  initialAction?: Action | 'invoice' | null
}>()

const emit = defineEmits<{ (e: 'close'): void }>()

const toast = useToast()

const invoice = ref<InvoiceCalculation | null>(null)
const invoiceLoading = ref(false)
const action = ref<Action | null>(null)
const qty = ref(1)
const amount = ref(50)
const examType = ref<'THEORETICAL' | 'PRACTICAL'>('PRACTICAL')
const busy = ref(false)
const confirmDelete = ref(false)

const pkg = computed(() => (props.student ? driveData.packageFor(props.student.target_license) : undefined))
const included = computed(() => pkg.value?.included_practical_classes ?? 0)
const ratio = computed(() => (props.student && included.value ? props.student.completed_classes / included.value : 0))
const pending = computed(() => toNumber(invoice.value?.pending_balance))

async function loadInvoice() {
  if (!props.student) return
  invoiceLoading.value = true
  try {
    invoice.value = await fetchInvoice(props.student.dni)
  } catch {
    invoice.value = null
  } finally {
    invoiceLoading.value = false
  }
}

watch(
  () => props.student?.dni,
  (dni) => {
    invoice.value = null
    action.value = null
    confirmDelete.value = false
    if (dni) {
      loadInvoice()
      if (props.initialAction && props.initialAction !== 'invoice') action.value = props.initialAction
    }
  },
  { immediate: true }
)

watch(
  () => props.initialAction,
  (a) => {
    if (a && a !== 'invoice') action.value = a
  }
)

function openAction(a: Action) {
  action.value = action.value === a ? null : a
  qty.value = 1
  amount.value = 50
}

async function run() {
  if (!props.student || !action.value) return
  busy.value = true
  const dni = props.student.dni
  try {
    if (action.value === 'classes') {
      await addStudentClasses(dni, qty.value)
      toast.success(`+${qty.value} clase${qty.value > 1 ? 's' : ''}`)
    } else if (action.value === 'advance') {
      await recordStudentAdvance(dni, amount.value)
      toast.success(`Pago de ${formatEuro(amount.value)} registrado`)
    } else {
      await registerStudentExam(dni, examType.value)
      toast.success(examType.value === 'PRACTICAL' ? 'Examen práctico registrado' : 'Examen teórico registrado')
    }
    action.value = null
    await driveData.refresh()
    await loadInvoice()
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'La operación falló')
  } finally {
    busy.value = false
  }
}

async function remove() {
  if (!props.student) return
  busy.value = true
  try {
    await deleteStudent(props.student.dni)
    toast.success('Expediente eliminado')
    emit('close')
    await driveData.refresh()
  } catch {
    toast.error('No se pudo eliminar')
  } finally {
    busy.value = false
  }
}

function downloadPdf() {
  if (!props.student) return
  const a = document.createElement('a')
  a.href = getInvoicePdfDownloadUrl(props.student.dni)
  a.download = `Factura_${props.student.dni}.pdf`
  document.body.appendChild(a)
  a.click()
  a.remove()
  toast.info('Factura generada en memoria')
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.student) emit('close')
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="student" class="drawer-root" @click.self="emit('close')">
        <aside class="drawer" :class="licenceClass(student.target_license)" role="dialog" aria-modal="true" :aria-label="`Ficha de ${student.first_name} ${student.last_name}`">
          <header class="d-head">
            <span class="avatar lg">{{ initials(student.first_name, student.last_name) }}</span>
            <div class="d-who">
              <h2 class="display d-name">{{ student.first_name }} {{ student.last_name }}</h2>
              <div class="d-meta mono">
                <span>{{ student.dni }}</span>
                <span class="dot"></span>
                <span>{{ student.registration_number }}</span>
              </div>
            </div>
            <span class="chip lic-chip">Permiso {{ student.target_license }}</span>
            <button type="button" class="icon-btn" aria-label="Cerrar ficha" @click="emit('close')">
              <AppIcon name="x" :size="18" />
            </button>
          </header>

          <!-- Progress -->
          <section class="d-progress">
            <ProgressRing :ratio="ratio" :size="96" :thickness="9" color="var(--lic)">
              <span class="ring-big mono"><strong>{{ student.completed_classes }}</strong><small>/{{ included || '—' }}</small></span>
            </ProgressRing>
            <div class="d-stats">
              <div>
                <span class="eyebrow">Teóricos</span>
                <strong class="display mono">{{ student.theoretical_exams_count }}</strong>
              </div>
              <div>
                <span class="eyebrow">Prácticos</span>
                <strong class="display mono">{{ student.practical_exams_count }}</strong>
              </div>
              <div>
                <span class="eyebrow">Entregado</span>
                <strong class="display mono emerald">{{ formatEuro(student.total_advances_paid) }}</strong>
              </div>
            </div>
          </section>

          <!-- Quick actions -->
          <section class="d-actions">
            <button type="button" class="act" :class="{ on: action === 'classes' }" @click="openAction('classes')">
              <AppIcon name="steering" :size="20" />
              <span>Clase</span>
            </button>
            <button type="button" class="act" :class="{ on: action === 'advance' }" @click="openAction('advance')">
              <AppIcon name="euro" :size="20" />
              <span>Pago</span>
            </button>
            <button type="button" class="act" :class="{ on: action === 'exam' }" @click="openAction('exam')">
              <AppIcon name="award" :size="20" />
              <span>Examen</span>
            </button>
          </section>

          <Transition name="fade">
            <form v-if="action" class="d-form panel" @submit.prevent="run">
              <div v-if="action === 'classes'" class="stepper" aria-label="Número de clases">
                <button type="button" aria-label="Menos" @click="qty = Math.max(1, qty - 1)"><AppIcon name="minus" :size="16" /></button>
                <input v-model.number="qty" type="number" min="1" max="50" aria-label="Clases" />
                <button type="button" aria-label="Más" @click="qty = Math.min(50, qty + 1)"><AppIcon name="plus" :size="16" /></button>
              </div>

              <div v-else-if="action === 'advance'" class="amount-row">
                <div class="presets">
                  <button v-for="p in [50, 100, 200]" :key="p" type="button" class="btn btn-soft btn-sm" :class="{ on: amount === p }" @click="amount = p">{{ p }} €</button>
                </div>
                <div class="money">
                  <input v-model.number="amount" class="input mono" type="number" min="1" step="5" aria-label="Importe" />
                  <span class="money-unit">€</span>
                </div>
              </div>

              <div v-else class="segmented" role="radiogroup" aria-label="Tipo de examen">
                <button type="button" role="radio" :aria-pressed="examType === 'THEORETICAL'" :aria-checked="examType === 'THEORETICAL'" @click="examType = 'THEORETICAL'">Teórico</button>
                <button type="button" role="radio" :aria-pressed="examType === 'PRACTICAL'" :aria-checked="examType === 'PRACTICAL'" @click="examType = 'PRACTICAL'">Práctico</button>
              </div>

              <button type="submit" class="btn btn-primary" :disabled="busy">
                <AppIcon name="check" :size="16" />
                Confirmar
              </button>
            </form>
          </Transition>

          <!-- Invoice -->
          <section class="d-invoice">
            <header class="inv-head">
              <span class="eyebrow">Liquidación</span>
              <span v-if="invoice" class="mono dim inv-num">{{ invoice.invoice_number }}</span>
            </header>

            <div v-if="invoiceLoading && !invoice" class="inv-skel">
              <div class="skeleton"></div>
              <div class="skeleton"></div>
              <div class="skeleton"></div>
            </div>

            <template v-else-if="invoice">
              <ul class="lines">
                <li>
                  <span>Matrícula <small class="dim">· {{ invoice.included_classes }} clases</small></span>
                  <span class="mono">{{ formatEuro(invoice.enrollment_fee) }}</span>
                </li>
                <li>
                  <span>Clases extra <small class="dim">· {{ invoice.extra_classes_count }}</small></span>
                  <span class="mono">{{ formatEuro(invoice.extra_classes_cost) }}</span>
                </li>
                <li>
                  <span>Tasas DGT <small class="dim">· {{ invoice.total_exams_count }}</small></span>
                  <span class="mono">{{ formatEuro(invoice.total_exams_cost) }}</span>
                </li>
                <li class="sub">
                  <span>Base</span>
                  <span class="mono">{{ formatEuro(invoice.subtotal_amount) }}</span>
                </li>
                <li class="sub">
                  <span>IVA {{ invoice.vat_percentage }}{{ String(invoice.vat_percentage).includes('%') ? '' : ' %' }}</span>
                  <span class="mono">{{ formatEuro(invoice.vat_amount) }}</span>
                </li>
                <li class="total">
                  <span>Total</span>
                  <span class="mono">{{ formatEuro(invoice.total_with_vat) }}</span>
                </li>
                <li class="paid">
                  <span>Entregado</span>
                  <span class="mono">− {{ formatEuro(invoice.advances_paid) }}</span>
                </li>
              </ul>

              <div class="balance" :class="pending > 0 ? 'due' : 'ok'">
                <span class="eyebrow">{{ pending > 0 ? 'Pendiente' : pending < 0 ? 'A favor del alumno' : 'Liquidado' }}</span>
                <strong class="display mono">{{ formatEuro(Math.abs(pending)) }}</strong>
              </div>

              <button type="button" class="btn btn-emerald btn-lg pdf" @click="downloadPdf">
                <AppIcon name="download" :size="18" />
                Factura PDF
              </button>
            </template>
          </section>

          <footer class="d-foot">
            <template v-if="!confirmDelete">
              <button type="button" class="btn btn-ghost btn-sm danger" @click="confirmDelete = true">
                <AppIcon name="trash" :size="15" />
                Eliminar expediente
              </button>
            </template>
            <template v-else>
              <span class="muted">¿Seguro?</span>
              <button type="button" class="btn btn-ghost btn-sm" @click="confirmDelete = false">No</button>
              <button type="button" class="btn btn-danger btn-sm" :disabled="busy" @click="remove">Sí, eliminar</button>
            </template>
          </footer>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-root {
  position: fixed;
  inset: 0;
  z-index: 950;
  background: rgba(3, 6, 14, 0.55);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: flex-end;
}

.drawer {
  width: min(460px, 100%);
  height: 100%;
  overflow-y: auto;
  background: rgba(11, 17, 33, 0.98);
  border-left: 1px solid var(--line-2);
  box-shadow: var(--shadow-2);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding: 1.4rem 1.4rem 1.6rem;
  padding-top: calc(var(--eco-bar-h) + 1.2rem);
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity var(--t-med);
}

.drawer-enter-active .drawer,
.drawer-leave-active .drawer {
  transition: transform var(--t-med);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer,
.drawer-leave-to .drawer {
  transform: translateX(40px);
}

.d-head {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.d-who {
  flex: 1;
  min-width: 0;
}

.d-name {
  font-size: 1.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.d-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.74rem;
  color: var(--ink-3);
}

.dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--ink-3);
}

.lic-chip {
  background: var(--lic-soft);
  color: var(--lic-2);
  border-color: color-mix(in srgb, var(--lic) 30%, transparent);
}

.d-progress {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.ring-big {
  display: inline-flex;
  align-items: baseline;
  font-size: 1.3rem;
}

.ring-big small {
  font-size: 0.75rem;
  color: var(--ink-3);
}

.d-stats {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.d-stats div {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.d-stats strong {
  font-size: 1.3rem;
}

.emerald {
  color: var(--emerald-2);
}

.d-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
}

.act {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 0.8rem 0.5rem;
  border-radius: 16px;
  border: 1px solid var(--line-2);
  background: rgba(255, 255, 255, 0.04);
  color: var(--ink-2);
  font-size: 0.78rem;
  font-weight: 600;
  transition: background var(--t-fast), border-color var(--t-fast), color var(--t-fast);
}

.act:hover {
  background: rgba(255, 255, 255, 0.08);
  color: var(--ink);
}

.act.on {
  background: var(--lic-soft);
  border-color: var(--lic);
  color: var(--ink);
}

.d-form {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.9rem;
  flex-wrap: wrap;
}

.amount-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 1;
}

.presets {
  display: flex;
  gap: 0.3rem;
}

.presets .on {
  border-color: var(--blue);
  background: rgba(79, 140, 255, 0.16);
}

.money {
  position: relative;
  width: 120px;
}

.money .input {
  padding-right: 2rem;
}

.money-unit {
  position: absolute;
  right: 0.8rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--ink-3);
  font-weight: 600;
}

.d-invoice {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.inv-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.inv-num {
  font-size: 0.75rem;
}

.inv-skel {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.inv-skel .skeleton {
  height: 22px;
}

.lines {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.9rem;
}

.lines li {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.lines small {
  font-size: 0.75rem;
}

.lines .sub {
  color: var(--ink-2);
  font-size: 0.84rem;
}

.lines .sub:first-of-type {
  margin-top: 0.3rem;
  padding-top: 0.55rem;
  border-top: 1px dashed var(--line-2);
}

.lines .total {
  font-weight: 700;
  font-size: 1rem;
}

.lines .paid {
  color: var(--emerald-2);
}

.balance {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.9rem 1.1rem;
  border-radius: 16px;
  border: 1px solid;
}

.balance strong {
  font-size: 1.6rem;
}

.balance.due {
  background: rgba(245, 176, 43, 0.1);
  border-color: rgba(245, 176, 43, 0.4);
  color: var(--amber-2);
}

.balance.ok {
  background: rgba(34, 197, 139, 0.1);
  border-color: rgba(34, 197, 139, 0.4);
  color: var(--emerald-2);
}

.pdf {
  width: 100%;
}

.d-foot {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.danger {
  color: var(--ink-3);
}

.danger:hover {
  color: var(--rose-2);
}
</style>
