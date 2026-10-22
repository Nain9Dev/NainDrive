<script setup lang="ts">
import { computed } from 'vue'

export interface DonutSlice {
  key: string
  label: string
  value: number
  color: string
}

const props = withDefaults(
  defineProps<{
    slices: DonutSlice[]
    size?: number
    thickness?: number
    centerLabel?: string
    centerValue?: string
  }>(),
  { size: 180, thickness: 18 }
)

const radius = computed(() => (props.size - props.thickness) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const total = computed(() => props.slices.reduce((acc, s) => acc + s.value, 0))

const arcs = computed(() => {
  let offset = 0
  const gap = total.value > 0 && props.slices.length > 1 ? 3 : 0
  return props.slices.map((s) => {
    const share = total.value > 0 ? s.value / total.value : 0
    const length = Math.max(0, share * circumference.value - gap)
    const arc = { ...s, share, length, offset }
    offset += share * circumference.value
    return arc
  })
})
</script>

<template>
  <div class="donut" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg :viewBox="`0 0 ${size} ${size}`" role="img" :aria-label="centerLabel ? `${centerLabel}: ${centerValue}` : 'Distribución'">
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        stroke="rgba(255,255,255,0.06)"
        :stroke-width="thickness"
      />
      <circle
        v-for="a in arcs"
        :key="a.key"
        class="arc"
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="a.color"
        :stroke-width="thickness"
        stroke-linecap="round"
        :stroke-dasharray="`${a.length} ${circumference - a.length}`"
        :stroke-dashoffset="-a.offset"
        :transform="`rotate(-90 ${size / 2} ${size / 2})`"
      />
    </svg>
    <div class="donut-center">
      <strong class="display mono">{{ centerValue }}</strong>
      <span class="eyebrow">{{ centerLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.donut {
  position: relative;
  flex-shrink: 0;
}

svg {
  width: 100%;
  height: 100%;
  display: block;
}

.arc {
  transition: stroke-dasharray 600ms var(--ease), stroke-dashoffset 600ms var(--ease);
  filter: drop-shadow(0 0 6px color-mix(in srgb, currentColor 40%, transparent));
}

.donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
  pointer-events: none;
}

.donut-center strong {
  font-size: 2rem;
  line-height: 1;
}
</style>
