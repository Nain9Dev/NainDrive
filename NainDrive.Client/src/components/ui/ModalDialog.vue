<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '../AppIcon.vue'

const props = withDefaults(
  defineProps<{
    open: boolean
    title: string
    eyebrow?: string
    width?: number
  }>(),
  { width: 520 }
)

const emit = defineEmits<{ (e: 'close'): void }>()

const card = ref<HTMLElement | null>(null)

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.open) emit('close')
}

function focusFirst() {
  nextTick(() => {
    const el = card.value?.querySelector<HTMLElement>('input, select, textarea, button:not(.close)')
    el?.focus()
  })
}

watch(
  () => props.open,
  (v) => {
    document.body.style.overflow = v ? 'hidden' : ''
    if (v) focusFirst()
  }
)

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="pop">
      <div v-if="open" class="backdrop-modal" @click.self="emit('close')">
        <div
          ref="card"
          class="modal panel"
          role="dialog"
          aria-modal="true"
          :aria-label="title"
          :style="{ maxWidth: `${width}px` }"
        >
          <header class="modal-head">
            <div>
              <span v-if="eyebrow" class="eyebrow">{{ eyebrow }}</span>
              <h2 class="display modal-title">{{ title }}</h2>
            </div>
            <button type="button" class="icon-btn close" aria-label="Cerrar" @click="emit('close')">
              <AppIcon name="x" :size="18" />
            </button>
          </header>
          <div class="modal-body">
            <slot />
          </div>
          <footer v-if="$slots.footer" class="modal-foot">
            <slot name="footer" />
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.backdrop-modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(3, 6, 14, 0.7);
  backdrop-filter: blur(6px);
}

.modal {
  width: 100%;
  background: rgba(12, 18, 34, 0.96);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-2);
  max-height: calc(100vh - 2rem);
  display: flex;
  flex-direction: column;
}

.modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.4rem 1.5rem 0.75rem;
}

.modal-title {
  font-size: 1.3rem;
  margin-top: 0.15rem;
}

.modal-body {
  padding: 0.75rem 1.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-y: auto;
}

.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  padding: 1rem 1.5rem 1.4rem;
  border-top: 1px solid var(--line);
}
</style>
