<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 0..1 share of the ring to fill. Values above 1 are clamped and flagged `over`. */
    ratio: number
    size?: number
    thickness?: number
    color?: string
    label?: string
  }>(),
  { size: 64, thickness: 6, color: 'var(--blue)' }
)

const r = computed(() => (props.size - props.thickness) / 2)
const c = computed(() => 2 * Math.PI * r.value)
const clamped = computed(() => Math.min(1, Math.max(0, props.ratio)))
const dash = computed(() => `${clamped.value * c.value} ${c.value}`)
const over = computed(() => props.ratio > 1)
</script>

<template>
  <div class="ring" :class="{ over }" :style="{ width: `${size}px`, height: `${size}px`, '--ring-color': color }">
    <svg :viewBox="`0 0 ${size} ${size}`" aria-hidden="true">
      <circle :cx="size / 2" :cy="size / 2" :r="r" fill="none" stroke="rgba(255,255,255,0.07)" :stroke-width="thickness" />
      <circle
        class="fill"
        :cx="size / 2"
        :cy="size / 2"
        :r="r"
        fill="none"
        :stroke="color"
        :stroke-width="thickness"
        stroke-linecap="round"
        :stroke-dasharray="dash"
        :transform="`rotate(-90 ${size / 2} ${size / 2})`"
      />
    </svg>
    <div class="ring-center">
      <slot>
        <span v-if="label" class="ring-label mono">{{ label }}</span>
      </slot>
    </div>
  </div>
</template>

<style scoped>
.ring {
  position: relative;
  flex-shrink: 0;
}

svg {
  width: 100%;
  height: 100%;
  display: block;
}

.fill {
  transition: stroke-dasharray 500ms var(--ease);
}

.over .fill {
  filter: drop-shadow(0 0 5px var(--ring-color));
}

.ring-center {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  pointer-events: none;
}

.ring-label {
  font-size: 0.78rem;
  font-weight: 600;
}
</style>
