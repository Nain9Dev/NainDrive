<script setup lang="ts">
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import LicencePlate from '../components/ui/LicencePlate.vue'
import ProgressRing from '../components/ui/ProgressRing.vue'
import ModalDialog from '../components/ui/ModalDialog.vue'
import { recordFuelExpense } from '../services/api'
import type { Instructor } from '../types/contracts'
import { driveData } from '../store/driveData'
import { useToast } from '../composables/useToast'
import { daysUntil, formatEuro, initials, licenceClass, parseEsDate } from '../utils/format'

const { state } = driveData
const toast = useToast()

/** Display window for the ITV gauge: a full ring means a year or more of validity left. */
const ITV_WINDOW_DAYS = 365

function itv(inst: Instructor) {
  const d = parseEsDate(inst.itv_expiration_date)
  const days = daysUntil(d)
  if (days === null) return { days: null, ratio: 0, tone: 'var(--slate)', label: '—', state: 'unknown' as const }
  if (days < 0) return { days, ratio: 0, tone: 'var(--rose)', label: 'Caducada', state: 'expired' as const }
  const ratio = Math.min(1, days / ITV_WINDOW_DAYS)
  const tone = days < 30 ? 'var(--rose)' : days < 90 ? 'var(--amber)' : 'var(--emerald)'
  return { days, ratio, tone, label: `${days} d`, state: days < 30 ? ('soon' as const) : ('ok' as const) }
}

function studentsOf(instructorId: string): number {
  return state.students.filter((s) => s.assigned_instructor_id === instructorId).length
}

const fuelTarget = ref<Instructor | null>(null)
const fuelAmount = ref(50)
const busy = ref(false)

function openFuel(inst: Instructor) {
  fuelTarget.value = inst
  fuelAmount.value = 50
}

async function saveFuel() {
  if (!fuelTarget.value || fuelAmount.value <= 0) return
  busy.value = true
  try {
    await recordFuelExpense(fuelTarget.value.instructor_id, fuelAmount.value)
    toast.success(`Repostaje de ${formatEuro(fuelAmount.value)} anotado`)
    fuelTarget.value = null
    await driveData.refresh()
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'No se pudo anotar')
  } finally {
    busy.value = false
  }
}

const packages = computed(() =>
  state.packages.map((p) => ({ ...p, code: p.package_code.replace(/^PERMIT_/, '') }))
)

function packageIcon(code: string): 'car' | 'steering' | 'flag' {
  if (code === 'A2') return 'steering'
  if (code === 'C') return 'flag'
  return 'car'
}
</script>

<template>
  <section class="fleet">
    <div class="block">
      <h2 class="eyebrow block-title">Instructores y vehículos</h2>
      <div v-if="state.loading" class="grid">
        <div v-for="i in 3" :key="i" class="skeleton skel"></div>
      </div>
      <div v-else class="grid">
        <article v-for="inst in state.instructors" :key="inst.instructor_id" class="panel inst">
          <header class="inst-head">
            <span class="avatar lic-other">{{ initials(inst.full_name.split(' ')[0] ?? '', inst.full_name.split(' ').slice(1).join(' ')) }}</span>
            <div class="inst-who">
              <h3 class="inst-name">{{ inst.full_name }}</h3>
              <span class="dim inst-meta">{{ studentsOf(inst.instructor_id) }} {{ studentsOf(inst.instructor_id) === 1 ? 'alumno' : 'alumnos' }} · {{ inst.instructor_id }}</span>
            </div>
          </header>

          <div class="vehicle">
            <div class="vehicle-text">
              <span class="model">{{ inst.vehicle_model }}</span>
              <LicencePlate :plate="inst.assigned_vehicle_plate" />
            </div>
            <div class="itv" :class="itv(inst).state" :title="`ITV hasta ${inst.itv_expiration_date}`">
              <ProgressRing :ratio="itv(inst).ratio" :size="58" :thickness="6" :color="itv(inst).tone">
                <AppIcon name="shield" :size="18" />
              </ProgressRing>
              <span class="itv-text">
                <span class="eyebrow">ITV</span>
                <strong class="mono">{{ itv(inst).label }}</strong>
              </span>
            </div>
          </div>

          <footer class="inst-foot">
            <span class="fuel">
              <AppIcon name="fuel" :size="16" />
              <strong class="mono">{{ formatEuro(inst.total_fuel_expenses) }}</strong>
            </span>
            <button type="button" class="btn btn-soft btn-sm" @click="openFuel(inst)">
              <AppIcon name="plus" :size="14" />
              Repostaje
            </button>
          </footer>
        </article>
      </div>
    </div>

    <div class="block">
      <h2 class="eyebrow block-title">Tarifas</h2>
      <div class="grid">
        <article v-for="p in packages" :key="p.package_code" class="panel tariff" :class="licenceClass(p.code)">
          <header class="tariff-head">
            <span class="tariff-icon"><AppIcon :name="packageIcon(p.code)" :size="22" /></span>
            <span class="tariff-code display">{{ p.code }}</span>
          </header>
          <strong class="tariff-price display mono">{{ formatEuro(p.enrollment_fee) }}</strong>
          <span class="dim tariff-sub">matrícula</span>
          <ul class="tariff-lines">
            <li><span>Clases incluidas</span><strong class="mono">{{ p.included_practical_classes }}</strong></li>
            <li><span>Clase extra</span><strong class="mono">{{ formatEuro(p.extra_class_price) }}</strong></li>
            <li><span>Tasa examen</span><strong class="mono">{{ formatEuro(p.dgt_exam_fee) }}</strong></li>
          </ul>
        </article>
      </div>
    </div>

    <ModalDialog :open="!!fuelTarget" title="Repostaje" :eyebrow="fuelTarget?.assigned_vehicle_plate" :width="400" @close="fuelTarget = null">
      <div class="presets">
        <button v-for="p in [30, 50, 80]" :key="p" type="button" class="btn btn-soft" :class="{ on: fuelAmount === p }" @click="fuelAmount = p">{{ p }} €</button>
      </div>
      <div class="money">
        <input v-model.number="fuelAmount" class="input lg" type="number" min="1" step="0.01" aria-label="Importe" />
        <span class="money-unit">€</span>
      </div>
      <template #footer>
        <button type="button" class="btn btn-ghost" @click="fuelTarget = null">Cancelar</button>
        <button type="button" class="btn btn-primary" :disabled="busy || fuelAmount <= 0" @click="saveFuel">
          <AppIcon name="check" :size="16" />
          Anotar
        </button>
      </template>
    </ModalDialog>
  </section>
</template>

<style scoped>
.fleet {
  display: flex;
  flex-direction: column;
  gap: 1.6rem;
}

.block {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.block-title {
  margin-left: 0.25rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.skel {
  height: 210px;
}

.inst {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.1rem;
  transition: border-color var(--t-med), transform var(--t-med);
}

.inst:hover,
.tariff:hover {
  border-color: var(--line-3);
  transform: translateY(-3px);
}

.inst-head {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.inst-who {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.inst-name {
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.inst-meta {
  font-size: 0.76rem;
}

.vehicle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 0.9rem;
  border-radius: 14px;
  background: rgba(7, 11, 22, 0.55);
  border: 1px solid var(--line);
}

.vehicle-text {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 0;
}

.model {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--ink-2);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.itv {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-shrink: 0;
}

.itv-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.itv-text strong {
  font-size: 0.95rem;
}

.itv.ok .itv-text strong { color: var(--emerald-2); }
.itv.soon .itv-text strong,
.itv.expired .itv-text strong { color: var(--rose-2); }
.itv.ok :deep(svg path) { color: var(--emerald-2); }
.itv.soon :deep(.ring-center), .itv.expired :deep(.ring-center) { color: var(--rose-2); }
.itv.ok :deep(.ring-center) { color: var(--emerald-2); }

.inst-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 0.8rem;
  border-top: 1px solid var(--line);
}

.fuel {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--ink-2);
}

.fuel strong {
  color: var(--ink);
}

.tariff {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1.2rem 1.2rem 1rem;
  transition: border-color var(--t-med), transform var(--t-med);
  overflow: hidden;
}

.tariff::after {
  content: '';
  position: absolute;
  right: -60px;
  top: -60px;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--lic) 30%, transparent) 0%, transparent 70%);
  pointer-events: none;
}

.tariff-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}

.tariff-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  background: var(--lic-soft);
  color: var(--lic-2);
  border: 1px solid color-mix(in srgb, var(--lic) 30%, transparent);
}

.tariff-code {
  font-size: 1.6rem;
  color: var(--lic-2);
}

.tariff-price {
  font-size: 2rem;
  line-height: 1;
}

.tariff-sub {
  font-size: 0.78rem;
}

.tariff-lines {
  list-style: none;
  margin-top: 0.9rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font-size: 0.86rem;
}

.tariff-lines li {
  display: flex;
  justify-content: space-between;
  color: var(--ink-2);
}

.tariff-lines strong {
  color: var(--ink);
}

.presets {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.presets .on {
  border-color: var(--blue);
  background: rgba(79, 140, 255, 0.16);
}

.money {
  position: relative;
}

.money .input {
  padding-right: 2.6rem;
  text-align: right;
}

.money-unit {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--ink-3);
  font-weight: 600;
  font-size: 1.1rem;
}
</style>
