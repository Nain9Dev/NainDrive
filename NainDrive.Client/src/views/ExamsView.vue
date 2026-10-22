<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import ModalDialog from '../components/ui/ModalDialog.vue'
import { scheduleDgtAppointment } from '../services/api'
import type { DgtAppointmentStatus, DgtExamAppointment, DgtExamType } from '../types/contracts'
import { driveData } from '../store/driveData'
import { useToast } from '../composables/useToast'
import { daysUntil, initials, isoToEsDate, licenceClass, monthLabel, monthShort, parseEsDate, todayIso } from '../utils/format'

const emit = defineEmits<{ (e: 'openStudent', dni: string): void }>()

const { state } = driveData
const toast = useToast()

type Filter = 'all' | DgtAppointmentStatus
const filter = ref<Filter>('all')

const STATUS: Record<DgtAppointmentStatus, { label: string; chip: string }> = {
  SCHEDULED: { label: 'Programado', chip: 'chip-blue' },
  PASSED: { label: 'Apto', chip: 'chip-emerald' },
  FAILED: { label: 'No apto', chip: 'chip-rose' },
  CANCELLED: { label: 'Cancelado', chip: 'chip-slate' },
}

const counts = computed(() => {
  const c: Record<Filter, number> = { all: state.appointments.length, SCHEDULED: 0, PASSED: 0, FAILED: 0, CANCELLED: 0 }
  for (const a of state.appointments) c[a.status] += 1
  return c
})

interface Row extends DgtExamAppointment {
  date: Date | null
}

const groups = computed(() => {
  const rows: Row[] = state.appointments
    .filter((a) => filter.value === 'all' || a.status === filter.value)
    .map((a) => ({ ...a, date: parseEsDate(a.appointment_date) }))
    .sort((a, b) => (a.date?.getTime() ?? 0) - (b.date?.getTime() ?? 0))

  const map = new Map<string, { label: string; rows: Row[] }>()
  for (const r of rows) {
    const key = r.date ? `${r.date.getFullYear()}-${r.date.getMonth()}` : 'none'
    const label = r.date ? monthLabel(r.date) : 'Sin fecha'
    if (!map.has(key)) map.set(key, { label, rows: [] })
    map.get(key)!.rows.push(r)
  }
  return Array.from(map.values())
})

// Scheduling
const open = ref(false)
const dni = ref('')
const type = ref<DgtExamType>('PRACTICAL')
const date = ref(todayIso())
const center = ref('Centro de Exámenes DGT Madrid-Móstoles')
const busy = ref(false)

watch(open, (v) => {
  if (v) {
    dni.value = state.students[0]?.dni ?? ''
    type.value = 'PRACTICAL'
    date.value = todayIso()
  }
})

async function schedule() {
  if (!dni.value || !date.value) return
  busy.value = true
  try {
    await scheduleDgtAppointment(dni.value, {
      exam_type: type.value,
      appointment_date: isoToEsDate(date.value),
      center_location: center.value.trim() || undefined,
    })
    toast.success('Convocatoria agendada')
    open.value = false
    await driveData.refresh()
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'No se pudo agendar')
  } finally {
    busy.value = false
  }
}

function relative(d: Date | null): string {
  const n = daysUntil(d)
  if (n === null) return ''
  if (n === 0) return 'hoy'
  if (n === 1) return 'mañana'
  if (n > 1) return `en ${n} días`
  return `hace ${-n} días`
}
</script>

<template>
  <section class="exams">
    <div class="toolbar">
      <div class="segmented" role="group" aria-label="Filtrar por estado">
        <button type="button" :aria-pressed="filter === 'all'" @click="filter = 'all'">Todos <span class="n mono">{{ counts.all }}</span></button>
        <button type="button" :aria-pressed="filter === 'SCHEDULED'" @click="filter = 'SCHEDULED'">Programados <span class="n mono">{{ counts.SCHEDULED }}</span></button>
        <button type="button" :aria-pressed="filter === 'PASSED'" @click="filter = 'PASSED'">Aptos <span class="n mono">{{ counts.PASSED }}</span></button>
        <button v-if="counts.FAILED" type="button" :aria-pressed="filter === 'FAILED'" @click="filter = 'FAILED'">No aptos <span class="n mono">{{ counts.FAILED }}</span></button>
      </div>
      <button type="button" class="btn btn-primary new" :disabled="!state.students.length" @click="open = true">
        <AppIcon name="plus" :size="18" />
        <span>Convocatoria</span>
      </button>
    </div>

    <div v-if="state.loading" class="skeleton skel"></div>

    <div v-else-if="groups.length" class="timeline">
      <section v-for="g in groups" :key="g.label" class="month">
        <h2 class="month-label eyebrow">{{ g.label }}</h2>
        <ul class="rows">
          <li v-for="a in g.rows" :key="a.appointment_id">
            <button
              type="button"
              class="row panel"
              :class="[licenceClass(driveData.studentFor(a.student_dni)?.target_license ?? ''), `st-${a.status.toLowerCase()}`]"
              @click="emit('openStudent', a.student_dni)"
            >
              <span class="date">
                <strong class="display">{{ a.date?.getDate() ?? '—' }}</strong>
                <span>{{ a.date ? monthShort(a.date) : '' }}</span>
              </span>

              <span class="who">
                <span class="avatar sm">{{ driveData.studentFor(a.student_dni) ? initials(driveData.studentFor(a.student_dni)!.first_name, driveData.studentFor(a.student_dni)!.last_name) : '?' }}</span>
                <span class="who-text">
                  <span class="name">{{ driveData.studentFor(a.student_dni) ? `${driveData.studentFor(a.student_dni)!.first_name} ${driveData.studentFor(a.student_dni)!.last_name}` : a.student_dni }}</span>
                  <span class="center dim">{{ a.center_location }}</span>
                </span>
              </span>

              <span class="chips">
                <span class="chip" :class="a.exam_type === 'PRACTICAL' ? 'chip-blue' : 'chip-violet'">
                  <AppIcon :name="a.exam_type === 'PRACTICAL' ? 'steering' : 'book'" :size="12" />
                  {{ a.exam_type === 'PRACTICAL' ? 'Práctico' : 'Teórico' }}
                </span>
                <span class="chip" :class="STATUS[a.status].chip">{{ STATUS[a.status].label }}</span>
              </span>

              <span class="when dim mono">{{ a.status === 'SCHEDULED' ? relative(a.date) : '' }}</span>
              <AppIcon name="chevron-right" :size="16" class="chev" />
            </button>
          </li>
        </ul>
      </section>
    </div>

    <div v-else class="empty panel">
      <AppIcon name="calendar" />
      <span>Sin convocatorias</span>
    </div>

    <ModalDialog :open="open" title="Nueva convocatoria" eyebrow="DGT" :width="500" @close="open = false">
      <form class="form" @submit.prevent="schedule">
        <div class="field">
          <label class="field-label" for="sch-student">Alumno</label>
          <select id="sch-student" v-model="dni" class="select" required>
            <option v-for="s in state.students" :key="s.dni" :value="s.dni">
              {{ s.first_name }} {{ s.last_name }} · {{ s.target_license }}
            </option>
          </select>
        </div>

        <div class="field">
          <span class="field-label">Prueba</span>
          <div class="segmented wide" role="radiogroup" aria-label="Tipo de prueba">
            <button type="button" role="radio" :aria-pressed="type === 'THEORETICAL'" :aria-checked="type === 'THEORETICAL'" @click="type = 'THEORETICAL'">
              <AppIcon name="book" :size="16" /> Teórico
            </button>
            <button type="button" role="radio" :aria-pressed="type === 'PRACTICAL'" :aria-checked="type === 'PRACTICAL'" @click="type = 'PRACTICAL'">
              <AppIcon name="steering" :size="16" /> Práctico
            </button>
          </div>
        </div>

        <div class="row2">
          <div class="field">
            <label class="field-label" for="sch-date">Fecha</label>
            <input id="sch-date" v-model="date" class="input mono" type="date" required :min="todayIso()" />
          </div>
          <div class="field">
            <label class="field-label" for="sch-center">Centro</label>
            <input id="sch-center" v-model="center" class="input" />
          </div>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn btn-ghost" @click="open = false">Cancelar</button>
        <button type="button" class="btn btn-primary" :disabled="busy || !dni || !date" @click="schedule">
          <AppIcon name="calendar" :size="16" />
          Agendar
        </button>
      </template>
    </ModalDialog>
  </section>
</template>

<style scoped>
.exams {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.segmented button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.n {
  font-size: 0.7rem;
  padding: 0 0.35rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--ink-3);
}

button[aria-pressed='true'] .n {
  background: var(--blue);
  color: #fff;
}

.new {
  height: 44px;
}

.skel {
  height: 300px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.month-label {
  margin: 0 0 0.6rem 0.25rem;
}

.rows {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.7rem 0.9rem 0.7rem 0.7rem;
  border-radius: 18px;
  text-align: left;
  transition: border-color var(--t-med), transform var(--t-med);
}

.row:hover {
  border-color: var(--line-3);
  transform: translateX(3px);
}

.row.st-cancelled {
  opacity: 0.6;
}

.date {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 52px;
  padding: 0.4rem 0;
  border-radius: 12px;
  background: var(--lic-soft);
  border: 1px solid color-mix(in srgb, var(--lic) 30%, transparent);
  color: var(--lic-2);
  line-height: 1;
  flex-shrink: 0;
}

.date strong {
  font-size: 1.35rem;
}

.date span {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.who {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.avatar.sm {
  width: 36px;
  height: 36px;
  font-size: 0.8rem;
  border-radius: 11px;
}

.who-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.name {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.center {
  font-size: 0.76rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chips {
  display: flex;
  gap: 0.4rem;
  flex-shrink: 0;
}

.when {
  font-size: 0.76rem;
  width: 90px;
  text-align: right;
  flex-shrink: 0;
}

.chev {
  color: var(--ink-3);
  flex-shrink: 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.row2 {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 0.9rem;
}

.segmented.wide {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.segmented.wide button {
  justify-content: center;
  height: 40px;
}

@media (max-width: 720px) {
  .when,
  .center {
    display: none;
  }

  .chips {
    flex-direction: column;
    align-items: flex-end;
    gap: 0.25rem;
  }

  .new span {
    display: none;
  }

  .new {
    width: 44px;
    padding: 0;
  }

  .row2 {
    grid-template-columns: 1fr;
  }
}
</style>
