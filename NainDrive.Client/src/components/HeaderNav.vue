<script setup lang="ts">
import { ref } from 'vue'
import { resetDatabase } from '../services/api'

defineProps<{
  apiHealthy: boolean
}>()

const emit = defineEmits<{
  (e: 'reset'): void
}>()

const isResetting = ref(false)

async function handleReset() {
  if (!confirm('¿Restaurar la base de datos a los perfiles y figuras sintéticas iniciales?')) return
  isResetting.value = true
  try {
    await resetDatabase()
    emit('reset')
  } catch (err) {
    alert('Error al resetear base de datos')
  } finally {
    isResetting.value = false
  }
}
</script>

<template>
  <header class="header-nav">
    <div class="container nav-content">
      <div class="brand">
        <svg class="brand-logo" viewBox="0 0 32 32" aria-hidden="true">
          <defs>
            <linearGradient id="driveLogoGrad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
              <stop stop-color="#3b82f6" />
              <stop offset="1" stop-color="#10b981" />
            </linearGradient>
          </defs>
          <rect width="32" height="32" rx="8" fill="url(#driveLogoGrad)" fill-opacity="0.15" />
          <rect x="0.5" y="0.5" width="31" height="31" rx="7.5" fill="none" stroke="url(#driveLogoGrad)" stroke-opacity="0.5" />
          <circle cx="16" cy="16" r="8" fill="none" stroke="url(#driveLogoGrad)" stroke-width="2" />
          <circle cx="16" cy="16" r="2.5" fill="url(#driveLogoGrad)" />
          <line x1="8" y1="16" x2="13.5" y2="16" stroke="url(#driveLogoGrad)" stroke-width="2" />
          <line x1="18.5" y1="16" x2="24" y2="16" stroke="url(#driveLogoGrad)" stroke-width="2" />
          <line x1="16" y1="18.5" x2="16" y2="24" stroke="url(#driveLogoGrad)" stroke-width="2" />
        </svg>
        <div class="brand-meta">
          <div class="brand-title">
            <span class="brand-name">NAIN</span><span class="brand-highlight">DRIVE</span>
            <span class="brand-badge">Python 3.12</span>
          </div>
          <span class="brand-sub">Gestión de Autoescuela & Facturación Determinista · Clean Architecture</span>
        </div>
      </div>

      <div class="nav-actions">
        <!-- API Status Pill -->
        <div class="status-pill" title="Estado de conexión con el backend FastAPI">
          <span class="pill-dot" :class="apiHealthy ? 'dot-online' : 'dot-offline'"></span>
          <span class="pill-text">{{ apiHealthy ? 'FastAPI 8150' : 'Desconectado' }}</span>
        </div>

        <!-- Reset Button -->
        <button
          type="button"
          class="btn btn-secondary btn-sm"
          :disabled="isResetting"
          @click="handleReset"
          title="Restaura la base de datos a los 4 alumnos y 3 instructores sintéticos originales"
        >
          <svg viewBox="0 0 20 20" fill="currentColor" width="13" height="13">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          Reset Demo
        </button>

        <!-- OpenAPI Scalar Link -->
        <a class="btn btn-ghost btn-sm" href="/docs" target="_blank" rel="noopener">
          <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
            <path d="M2 4h12M2 8h12M2 12h8" />
          </svg>
          Scalar /docs
        </a>

        <!-- Portfolio Link -->
        <a class="btn btn-secondary btn-sm" href="https://www.naindev.com" target="_blank" rel="noopener">
          NainDev.com
          <svg viewBox="0 0 16 16" width="11" height="11" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 3h7v7M13 3L5 11" />
          </svg>
        </a>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(6, 9, 19, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid var(--color-border);
  padding: 0.75rem 0;
}

.nav-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.brand-logo {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.brand-meta {
  display: flex;
  flex-direction: column;
}

.brand-title {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}

.brand-name {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.2rem;
  letter-spacing: 0.04em;
  color: var(--color-text-main);
}

.brand-highlight {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.2rem;
  letter-spacing: 0.04em;
  color: var(--accent-blue);
}

.brand-badge {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.brand-sub {
  font-size: 0.75rem;
  color: var(--color-text-dim);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(14, 21, 44, 0.8);
  border: 1px solid var(--color-border);
  padding: 0.35rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.pill-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-online {
  background: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald);
}

.dot-offline {
  background: var(--accent-rose);
  box-shadow: 0 0 8px var(--accent-rose);
}

@media (max-width: 860px) {
  .brand-sub { display: none; }
}
</style>
