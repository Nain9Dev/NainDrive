<script setup lang="ts">
import type { KPIDashboardSummary } from '../types/contracts'

defineProps<{
  summary: KPIDashboardSummary
}>()

function formatCurrency(amount: number | string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(num || 0)
}
</script>

<template>
  <div class="kpi-section">
    <!-- Top KPI Cards Grid -->
    <div class="kpi-grid">
      <!-- Card 1: Gross -->
      <article class="glass-panel kpi-card kpi-blue">
        <div class="kpi-head">
          <span class="kpi-label">Ingresos Brutos Facturables</span>
          <svg class="kpi-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="kpi-val font-mono">{{ formatCurrency(summary.total_gross) }}</div>
        <div class="kpi-foot">Base imponible sin impuestos</div>
      </article>

      <!-- Card 2: VAT -->
      <article class="glass-panel kpi-card kpi-emerald">
        <div class="kpi-head">
          <span class="kpi-label">IVA Legal Recaudable</span>
          <span class="tax-tag font-mono">21%</span>
        </div>
        <div class="kpi-val font-mono">{{ formatCurrency(summary.total_vat) }}</div>
        <div class="kpi-foot">Cuota tributaria estatal calculada</div>
      </article>

      <!-- Card 3: Pending Balance -->
      <article class="glass-panel kpi-card kpi-amber">
        <div class="kpi-head">
          <span class="kpi-label">Saldo Pendiente de Cobro</span>
          <svg class="kpi-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="kpi-val font-mono">{{ formatCurrency(summary.total_pending) }}</div>
        <div class="kpi-foot">Descontando anticipos entregados</div>
      </article>

      <!-- Card 4: Practical Lessons -->
      <article class="glass-panel kpi-card kpi-violet">
        <div class="kpi-head">
          <span class="kpi-label">Total Clases Prácticas</span>
          <svg class="kpi-icon" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="kpi-val font-mono">{{ summary.completed_lessons_sum }} <small>clases</small></div>
        <div class="kpi-foot">Impartidas por la flota activa</div>
      </article>
    </div>

    <!-- Secondary operational distribution banner -->
    <div class="glass-panel distribution-bar">
      <div class="dist-left">
        <h4 class="dist-title">Distribución de Matriculaciones por Permiso</h4>
        <div class="dist-pills">
          <div
            v-for="(count, license) in summary.license_distribution"
            :key="license"
            class="dist-pill"
          >
            <span class="pill-dot" :class="license.includes('B') ? 'dot-blue' : license.includes('A2') ? 'dot-emerald' : 'dot-amber'"></span>
            <span class="pill-name">{{ license }}:</span>
            <strong class="font-mono">{{ count }}</strong>
          </div>
        </div>
      </div>

      <div class="dist-right">
        <div class="op-stat">
          <span class="op-label">Alumnos Activos</span>
          <strong class="op-num font-mono">{{ summary.total_students }}</strong>
        </div>
        <div class="op-stat">
          <span class="op-label">Instructores</span>
          <strong class="op-num font-mono">{{ summary.total_instructors }}</strong>
        </div>
        <div class="op-stat">
          <span class="op-label">Media Clases / Alumno</span>
          <strong class="op-num font-mono">{{ summary.average_lessons_per_student }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.kpi-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.kpi-card {
  padding: 1.25rem 1.4rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.kpi-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.kpi-label {
  font-size: 0.775rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-icon {
  width: 18px;
  height: 18px;
  opacity: 0.6;
}

.tax-tag {
  font-size: 0.725rem;
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 700;
}

.kpi-blue .kpi-icon { color: var(--accent-blue); }
.kpi-emerald .kpi-icon { color: var(--accent-emerald); }
.kpi-amber .kpi-icon { color: var(--accent-amber); }
.kpi-violet .kpi-icon { color: var(--accent-violet); }

.kpi-val {
  font-size: 1.95rem;
  font-weight: 700;
  color: var(--color-text-main);
  line-height: 1.1;
  margin: 0.35rem 0;
}

.kpi-val small {
  font-size: 0.95rem;
  color: var(--color-text-dim);
  font-weight: 500;
}

.kpi-foot {
  font-size: 0.775rem;
  color: var(--color-text-dim);
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
}

.distribution-bar {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.dist-left {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.dist-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.dist-pills {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-wrap: wrap;
}

.dist-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  background: rgba(10, 15, 33, 0.8);
  border: 1px solid var(--color-border);
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.825rem;
}

.pill-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.dot-blue { background: var(--accent-blue); }
.dot-emerald { background: var(--accent-emerald); }
.dot-amber { background: var(--accent-amber); }

.dist-right {
  display: flex;
  align-items: center;
  gap: 2rem;
  border-left: 1px solid var(--color-border);
  padding-left: 2rem;
}

.op-stat {
  display: flex;
  flex-direction: column;
}

.op-label {
  font-size: 0.725rem;
  color: var(--color-text-dim);
  text-transform: uppercase;
}

.op-num {
  font-size: 1.25rem;
  color: var(--color-text-main);
}

@media (max-width: 1024px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .distribution-bar { flex-direction: column; align-items: flex-start; }
  .dist-right { border-left: none; padding-left: 0; border-top: 1px solid var(--color-border); padding-top: 1rem; width: 100%; justify-content: space-between; }
}

@media (max-width: 600px) {
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
