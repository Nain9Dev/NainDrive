<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import StatTile from '../components/ui/StatTile.vue'
import DonutChart, { type DonutSlice } from '../components/ui/DonutChart.vue'
import type { ViewKey } from '../components/NavRail.vue'
import { driveData } from '../store/driveData'
import { formatEuro, initials, licenceClass, licenceColor, monthShort, parseEsDate, toNumber } from '../utils/format'

const emit = defineEmits<{
  (e: 'openStudent', dni: string): void
  (e: 'go', view: ViewKey): void
}>()

const { state } = driveData

const slices = computed<DonutSlice[]>(() =>
  Object.entries(state.summary.license_distribution)
    .sort((a, b) => b[1] - a[1])
    .map(([key, value]) => ({ key, label: `Permiso ${key}`, value, color: licenceColor(key) }))
)

/** Display proportion only: share of the API's pending balance over its gross figure. */
const pendingShare = computed(() => {
  const gross = toNumber(state.summary.total_gross)
  const pending = toNumber(state.summary.total_pending)
  if (gross <= 0) return 0
  return Math.min(1, Math.max(0, pending / gross))
})

const upcoming = computed(() =>
  state.appointments
    .filter((a) => a.status === 'SCHEDULED')
    .map((a) => ({ ...a, date: parseEsDate(a.appointment_date), student: driveData.studentFor(a.student_dni) }))
    .sort((a, b) => (a.date?.getTime() ?? 0) - (b.date?.getTime() ?? 0))
    .slice(0, 4)
)

const roster = computed(() =>
  [...state.students]
    .map((s) => ({ s, pkg: driveData.packageFor(s.target_license) }))
    .sort((a, b) => b.s.completed_classes - a.s.completed_classes)
    .slice(0, 5)
)
</script>

<template>
  <section class="dash">
    <div class="tiles">
      <template v-if="state.loading">
        <div v-for="i in 4" :key="i" class="skeleton tile-skel"></div>
      </template>
      <template v-else>
        <StatTile label="Facturado" :value="formatEuro(state.summary.total_gross)" icon="euro" tone="blue" hint="IVA incluido" />
        <StatTile label="IVA" :value="formatEuro(state.summary.total_vat)" icon="shield" tone="emerald" hint="21 %" />
        <StatTile label="Pendiente" :value="formatEuro(state.summary.total_pending)" icon="clock" tone="amber" hint="por cobrar" />
        <StatTile label="Clases" :value="String(state.summary.completed_lessons_sum)" icon="steering" tone="violet" :hint="`${state.summary.average_lessons_per_student} por alumno`" />
      </template>
    </div>

    <div class="grid">
      <!-- Licence distribution -->
      <article class="panel panel-pad card-donut">
        <header class="panel-head">
          <h2 class="panel-title">Permisos</h2>
          <button type="button" class="icon-btn sm" aria-label="Ver alumnos" @click="emit('go', 'students')">
            <AppIcon name="chevron-right" :size="16" />
          </button>
        </header>
        <div class="donut-row">
          <DonutChart :slices="slices" :size="170" center-label="alumnos" :center-value="String(state.summary.total_students)" />
          <ul class="legend">
            <li v-for="s in slices" :key="s.key">
              <span class="swatch" :style="{ background: s.color }"></span>
              <span class="legend-label">{{ s.label }}</span>
              <strong class="mono">{{ s.value }}</strong>
            </li>
            <li v-if="!slices.length" class="dim">Sin alumnos</li>
          </ul>
        </div>
      </article>

      <!-- Billing -->
      <article class="panel panel-pad card-billing">
        <header class="panel-head">
          <h2 class="panel-title">Cobros</h2>
          <span class="chip chip-amber">{{ Math.round(pendingShare * 100) }} % pendiente</span>
        </header>
        <div class="bar" role="img" :aria-label="`Pendiente ${formatEuro(state.summary.total_pending)} de ${formatEuro(state.summary.total_gross)}`">
          <span class="bar-fill" :style="{ width: `${(1 - pendingShare) * 100}%` }"></span>
        </div>
        <div class="bar-legend">
          <span><i class="sw sw-ok"></i>Cobrado</span>
          <span><i class="sw sw-pend"></i>Pendiente <strong class="mono">{{ formatEuro(state.summary.total_pending) }}</strong></span>
        </div>
        <div class="mini-stats">
          <div>
            <span class="eyebrow">Alumnos</span>
            <strong class="display mono">{{ state.summary.total_students }}</strong>
          </div>
          <div>
            <span class="eyebrow">Instructores</span>
            <strong class="display mono">{{ state.summary.total_instructors }}</strong>
          </div>
          <div>
            <span class="eyebrow">Clases / alumno</span>
            <strong class="display mono">{{ state.summary.average_lessons_per_student }}</strong>
          </div>
        </div>
      </article>

      <!-- Agenda -->
      <article class="panel panel-pad card-agenda">
        <header class="panel-head">
          <h2 class="panel-title">Próximos exámenes</h2>
          <button type="button" class="icon-btn sm" aria-label="Ver exámenes" @click="emit('go', 'exams')">
            <AppIcon name="chevron-right" :size="16" />
          </button>
        </header>
        <ul class="agenda">
          <li v-for="a in upcoming" :key="a.appointment_id">
            <button type="button" class="agenda-row" @click="emit('openStudent', a.student_dni)">
              <span class="date-block">
                <strong class="display">{{ a.date?.getDate() ?? '—' }}</strong>
                <span>{{ a.date ? monthShort(a.date) : '' }}</span>
              </span>
              <span class="agenda-main">
                <span class="agenda-name">{{ a.student ? `${a.student.first_name} ${a.student.last_name}` : a.student_dni }}</span>
                <span class="agenda-sub dim">{{ a.center_location }}</span>
              </span>
              <span class="chip" :class="a.exam_type === 'PRACTICAL' ? 'chip-blue' : 'chip-violet'">
                {{ a.exam_type === 'PRACTICAL' ? 'Práctico' : 'Teórico' }}
              </span>
            </button>
          </li>
          <li v-if="!upcoming.length" class="empty">
            <AppIcon name="calendar" />
            <span>Sin convocatorias</span>
          </li>
        </ul>
      </article>

      <!-- Roster -->
      <article class="panel panel-pad card-roster">
        <header class="panel-head">
          <h2 class="panel-title">Alumnos</h2>
          <button type="button" class="icon-btn sm" aria-label="Ver todos los alumnos" @click="emit('go', 'students')">
            <AppIcon name="chevron-right" :size="16" />
          </button>
        </header>
        <ul class="roster">
          <li v-for="{ s, pkg } in roster" :key="s.dni">
            <button type="button" class="roster-row" :class="licenceClass(s.target_license)" @click="emit('openStudent', s.dni)">
              <span class="avatar">{{ initials(s.first_name, s.last_name) }}</span>
              <span class="roster-main">
                <span class="roster-name">{{ s.first_name }} {{ s.last_name }}</span>
                <span class="track" aria-hidden="true">
                  <span
                    class="track-fill"
                    :style="{ width: `${pkg ? Math.min(100, (s.completed_classes / Math.max(1, pkg.included_practical_classes)) * 100) : 0}%` }"
                  ></span>
                </span>
              </span>
              <span class="roster-meta mono">
                <strong>{{ s.completed_classes }}</strong><span class="dim">/{{ pkg?.included_practical_classes ?? '—' }}</span>
              </span>
              <span class="chip lic-chip">{{ s.target_license }}</span>
            </button>
          </li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped>
.dash {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.tiles {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.tile-skel {
  height: 104px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 1rem;
}

.card-donut { grid-column: span 4; }
.card-billing { grid-column: span 4; }
.card-agenda { grid-column: span 4; }
.card-roster { grid-column: span 12; }

.donut-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.legend {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  flex: 1;
  min-width: 0;
}

.legend li {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.88rem;
}

.legend-label {
  flex: 1;
  color: var(--ink-2);
}

.swatch {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  box-shadow: 0 0 8px currentColor;
}

.bar {
  height: 14px;
  border-radius: 7px;
  background: rgba(245, 176, 43, 0.22);
  overflow: hidden;
  margin-top: 0.4rem;
}

.bar-fill {
  display: block;
  height: 100%;
  border-radius: 7px;
  background: linear-gradient(90deg, var(--emerald), var(--emerald-2));
  box-shadow: 0 0 14px rgba(34, 197, 139, 0.5);
  transition: width 600ms var(--ease);
}

.bar-legend {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 0.7rem;
  font-size: 0.8rem;
  color: var(--ink-2);
}

.bar-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.sw {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.sw-ok { background: var(--emerald); }
.sw-pend { background: var(--amber); }

.mini-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.mini-stats div {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.mini-stats strong {
  font-size: 1.4rem;
}

.agenda,
.roster {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.agenda-row,
.roster-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.55rem 0.6rem;
  border-radius: 14px;
  text-align: left;
  transition: background var(--t-fast);
}

.agenda-row:hover,
.roster-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.date-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 44px;
  padding: 0.3rem 0;
  border-radius: 10px;
  background: rgba(79, 140, 255, 0.12);
  border: 1px solid rgba(79, 140, 255, 0.28);
  color: var(--blue-2);
  line-height: 1;
  flex-shrink: 0;
}

.date-block strong {
  font-size: 1.15rem;
}

.date-block span {
  font-size: 0.62rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agenda-main,
.roster-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.agenda-name,
.roster-name {
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agenda-sub {
  font-size: 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track {
  height: 5px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.07);
  overflow: hidden;
  max-width: 260px;
}

.track-fill {
  display: block;
  height: 100%;
  background: var(--lic);
  border-radius: 3px;
  box-shadow: 0 0 8px var(--lic);
  transition: width 500ms var(--ease);
}

.roster-meta {
  font-size: 0.9rem;
}

.lic-chip {
  background: var(--lic-soft);
  color: var(--lic-2);
  border-color: color-mix(in srgb, var(--lic) 30%, transparent);
}

@media (max-width: 1100px) {
  .tiles {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .card-donut,
  .card-billing {
    grid-column: span 6;
  }

  .card-agenda {
    grid-column: span 12;
  }
}

@media (max-width: 640px) {
  .tiles {
    grid-template-columns: 1fr;
  }

  .card-donut,
  .card-billing {
    grid-column: span 12;
  }

  .donut-row {
    flex-direction: column;
  }

  .legend {
    width: 100%;
  }
}
</style>
