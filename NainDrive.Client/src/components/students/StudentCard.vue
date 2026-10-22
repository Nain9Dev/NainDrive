<script setup lang="ts">
import { computed } from 'vue'
import AppIcon from '../AppIcon.vue'
import ProgressRing from '../ui/ProgressRing.vue'
import type { LicensePackage, Student } from '../../types/contracts'
import { formatEuro, initials, licenceClass } from '../../utils/format'

const props = defineProps<{
  student: Student
  pkg?: LicensePackage
}>()

const emit = defineEmits<{
  (e: 'open'): void
  (e: 'action', kind: 'classes' | 'advance' | 'exam' | 'invoice'): void
}>()

const included = computed(() => props.pkg?.included_practical_classes ?? 0)
const ratio = computed(() => (included.value > 0 ? props.student.completed_classes / included.value : 0))
const extra = computed(() => Math.max(0, props.student.completed_classes - included.value))
</script>

<template>
  <article class="card panel" :class="licenceClass(student.target_license)">
    <button type="button" class="card-open" @click="emit('open')">
      <span class="sr-only">Abrir ficha de {{ student.first_name }} {{ student.last_name }}</span>
    </button>

    <header class="card-head">
      <span class="avatar">{{ initials(student.first_name, student.last_name) }}</span>
      <div class="who">
        <h3 class="name">{{ student.first_name }} {{ student.last_name }}</h3>
        <span class="dni mono dim">{{ student.dni }}</span>
      </div>
      <span class="chip lic-chip">{{ student.target_license }}</span>
    </header>

    <div class="card-body">
      <ProgressRing :ratio="ratio" :size="74" :thickness="7" color="var(--lic)">
        <span class="ring-txt mono"><strong>{{ student.completed_classes }}</strong><small>/{{ included || '—' }}</small></span>
      </ProgressRing>

      <dl class="facts">
        <div>
          <dt>Clases</dt>
          <dd class="mono">
            {{ student.completed_classes }}
            <span v-if="extra" class="chip chip-amber extra">+{{ extra }}</span>
          </dd>
        </div>
        <div>
          <dt>Exámenes</dt>
          <dd class="pips" :aria-label="`${student.theoretical_exams_count} teóricos, ${student.practical_exams_count} prácticos`">
            <span v-for="i in student.theoretical_exams_count" :key="`t${i}`" class="pip pip-t" title="Teórico"></span>
            <span v-for="i in student.practical_exams_count" :key="`p${i}`" class="pip pip-p" title="Práctico"></span>
            <span v-if="!student.theoretical_exams_count && !student.practical_exams_count" class="dim">—</span>
          </dd>
        </div>
        <div>
          <dt>Entregado</dt>
          <dd class="mono emerald">{{ formatEuro(student.total_advances_paid) }}</dd>
        </div>
      </dl>
    </div>

    <footer class="card-actions">
      <button type="button" class="icon-btn" aria-label="Añadir clase" title="Clase" @click.stop="emit('action', 'classes')">
        <AppIcon name="steering" :size="18" />
      </button>
      <button type="button" class="icon-btn" aria-label="Registrar pago" title="Pago" @click.stop="emit('action', 'advance')">
        <AppIcon name="euro" :size="18" />
      </button>
      <button type="button" class="icon-btn" aria-label="Registrar examen" title="Examen" @click.stop="emit('action', 'exam')">
        <AppIcon name="award" :size="18" />
      </button>
      <span class="spacer"></span>
      <button type="button" class="icon-btn accent" aria-label="Ver factura" title="Factura" @click.stop="emit('action', 'invoice')">
        <AppIcon name="file" :size="18" />
      </button>
    </footer>
  </article>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding: 1.1rem 1.1rem 0.8rem;
  transition: border-color var(--t-med), transform var(--t-med), box-shadow var(--t-med);
}

.card:hover {
  border-color: color-mix(in srgb, var(--lic) 45%, transparent);
  transform: translateY(-3px);
  box-shadow: 0 18px 40px -22px color-mix(in srgb, var(--lic) 60%, transparent);
}

.card-open {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  z-index: 1;
}

.card-open:focus-visible {
  outline: 2px solid var(--lic-2);
}

.card-head,
.card-body,
.card-actions {
  position: relative;
  z-index: 2;
  pointer-events: none;
}

.card-actions {
  pointer-events: auto;
}

.card-head {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.who {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.name {
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dni {
  font-size: 0.75rem;
}

.lic-chip {
  background: var(--lic-soft);
  color: var(--lic-2);
  border-color: color-mix(in srgb, var(--lic) 30%, transparent);
}

.card-body {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.ring-txt {
  display: inline-flex;
  align-items: baseline;
  font-size: 0.95rem;
}

.ring-txt small {
  font-size: 0.65rem;
  color: var(--ink-3);
}

.facts {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.45rem;
}

.facts div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

dt {
  font-size: 0.72rem;
  color: var(--ink-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}

dd {
  font-size: 0.9rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.extra {
  height: 20px;
  font-size: 0.62rem;
}

.emerald {
  color: var(--emerald-2);
}

.pips {
  gap: 0.25rem;
}

.pip {
  width: 10px;
  height: 10px;
  border-radius: 3px;
}

.pip-t { background: var(--violet); box-shadow: 0 0 6px var(--violet); }
.pip-p { background: var(--blue); box-shadow: 0 0 6px var(--blue); }

.card-actions {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  padding-top: 0.6rem;
  border-top: 1px solid var(--line);
}

.spacer {
  flex: 1;
}
</style>
