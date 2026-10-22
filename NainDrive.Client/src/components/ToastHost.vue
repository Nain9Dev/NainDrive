<script setup lang="ts">
import AppIcon from './AppIcon.vue'
import { useToast } from '../composables/useToast'

const { toasts, dismiss } = useToast()
</script>

<template>
  <Teleport to="body">
    <div class="toast-host" aria-live="polite" aria-atomic="false">
      <TransitionGroup name="toast">
        <div v-for="t in toasts.items" :key="t.id" class="toast" :class="`toast-${t.kind}`" role="status">
          <AppIcon :name="t.kind === 'success' ? 'check' : t.kind === 'error' ? 'alert' : 'info'" :size="18" />
          <span>{{ t.text }}</span>
          <button type="button" class="icon-btn sm" aria-label="Cerrar aviso" @click="dismiss(t.id)">
            <AppIcon name="x" :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-host {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: min(380px, calc(100vw - 2rem));
}

.toast {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.7rem 0.6rem 0.7rem 0.9rem;
  border-radius: 14px;
  background: rgba(12, 18, 34, 0.96);
  border: 1px solid var(--line-2);
  box-shadow: var(--shadow-2);
  font-size: 0.875rem;
  font-weight: 500;
}

.toast span {
  flex: 1;
}

.toast-success { border-color: rgba(34, 197, 139, 0.45); color: var(--emerald-2); }
.toast-error { border-color: rgba(255, 77, 109, 0.45); color: var(--rose-2); }
.toast-info { border-color: rgba(79, 140, 255, 0.45); color: var(--blue-2); }

.toast span {
  color: var(--ink);
}

.toast-enter-active,
.toast-leave-active {
  transition: all var(--t-med);
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}

@media (max-width: 720px) {
  .toast-host {
    bottom: 84px;
  }
}
</style>
