<script setup lang="ts">
import { ref } from 'vue'
import AppIcon from './AppIcon.vue'
import ModalDialog from './ui/ModalDialog.vue'
import { resetDatabase } from '../services/api'
import { useToast } from '../composables/useToast'

defineProps<{
  healthy: boolean
  title: string
}>()

const emit = defineEmits<{ (e: 'refresh'): void }>()

const toast = useToast()
const confirmOpen = ref(false)
const resetting = ref(false)

async function doReset() {
  resetting.value = true
  try {
    await resetDatabase()
    confirmOpen.value = false
    toast.success('Demo restaurada')
    emit('refresh')
  } catch {
    toast.error('No se pudo restaurar la demo')
  } finally {
    resetting.value = false
  }
}
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <span class="logo" aria-hidden="true">
        <svg viewBox="0 0 32 32" width="34" height="34">
          <defs>
            <linearGradient id="nd-grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
              <stop stop-color="#4f8cff" />
              <stop offset="1" stop-color="#22c58b" />
            </linearGradient>
          </defs>
          <rect width="32" height="32" rx="9" fill="url(#nd-grad)" fill-opacity="0.16" />
          <rect x="0.5" y="0.5" width="31" height="31" rx="8.5" fill="none" stroke="url(#nd-grad)" stroke-opacity="0.55" />
          <circle cx="16" cy="16" r="8.5" fill="none" stroke="url(#nd-grad)" stroke-width="2.2" />
          <circle cx="16" cy="16" r="2.6" fill="url(#nd-grad)" />
          <path d="M7.5 16h6M18.5 16h6M16 18.5V24.5" stroke="url(#nd-grad)" stroke-width="2.2" stroke-linecap="round" />
        </svg>
      </span>
      <div class="brand-text">
        <span class="brand-name display">Nain<em>Drive</em></span>
        <span class="brand-view">{{ title }}</span>
      </div>
    </div>

    <div class="actions">
      <span class="status" :class="healthy ? 'on' : 'off'" :title="healthy ? 'Motor conectado' : 'Modo demo local'">
        <AppIcon :name="healthy ? 'wifi' : 'wifi-off'" :size="16" />
        <span class="status-text">{{ healthy ? 'API' : 'Demo' }}</span>
      </span>

      <button type="button" class="icon-btn" aria-label="Restaurar datos de demo" title="Restaurar demo" @click="confirmOpen = true">
        <AppIcon name="refresh" :size="18" />
      </button>

      <a class="icon-btn" href="https://github.com/Nain9Dev/NainDrive" target="_blank" rel="noopener" aria-label="Repositorio en GitHub" title="GitHub">
        <AppIcon name="github" :size="18" />
      </a>

      <a class="btn btn-soft btn-sm site" href="https://www.naindev.com" target="_blank" rel="noopener">
        naindev.com
        <AppIcon name="external" :size="14" />
      </a>
    </div>

    <ModalDialog :open="confirmOpen" title="Restaurar demo" eyebrow="Datos sintéticos" :width="420" @close="confirmOpen = false">
      <p class="muted">Vuelve a los 4 alumnos, 3 instructores y 3 convocatorias iniciales.</p>
      <template #footer>
        <button type="button" class="btn btn-ghost" @click="confirmOpen = false">Cancelar</button>
        <button type="button" class="btn btn-primary" :disabled="resetting" @click="doReset">
          <AppIcon name="refresh" :size="16" />
          Restaurar
        </button>
      </template>
    </ModalDialog>
  </header>
</template>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 0 1.4rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.logo {
  display: grid;
  place-items: center;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-name {
  font-size: 1.25rem;
  letter-spacing: 0.01em;
}

.brand-name em {
  font-style: normal;
  background: linear-gradient(135deg, var(--blue-2), var(--emerald-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.brand-view {
  font-size: 0.78rem;
  color: var(--ink-3);
  font-weight: 500;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.status {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  height: 34px;
  padding: 0 0.7rem;
  margin-right: 0.3rem;
  border-radius: var(--r-full);
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  border: 1px solid var(--line);
}

.status.on {
  color: var(--emerald-2);
  background: rgba(34, 197, 139, 0.1);
  border-color: rgba(34, 197, 139, 0.3);
}

.status.off {
  color: var(--amber-2);
  background: rgba(245, 176, 43, 0.1);
  border-color: rgba(245, 176, 43, 0.3);
}

@media (max-width: 600px) {
  .site,
  .status-text {
    display: none;
  }

  .topbar {
    padding: 0.8rem 0 1rem;
  }
}
</style>
