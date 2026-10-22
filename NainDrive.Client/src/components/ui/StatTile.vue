<script setup lang="ts">
import AppIcon, { type IconName } from '../AppIcon.vue'

withDefaults(
  defineProps<{
    label: string
    value: string
    icon: IconName
    tone?: 'blue' | 'emerald' | 'amber' | 'rose' | 'violet'
    hint?: string
  }>(),
  { tone: 'blue' }
)
</script>

<template>
  <article class="tile" :class="`tone-${tone}`">
    <div class="tile-icon">
      <AppIcon :name="icon" :size="20" />
    </div>
    <div class="tile-body">
      <span class="eyebrow">{{ label }}</span>
      <strong class="tile-value display mono">{{ value }}</strong>
      <span v-if="hint" class="tile-hint">{{ hint }}</span>
    </div>
    <span class="tile-glow" aria-hidden="true"></span>
  </article>
</template>

<style scoped>
.tile {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.3rem;
  background: var(--panel);
  backdrop-filter: blur(18px);
  border: 1px solid var(--line);
  border-radius: var(--r-lg);
  box-shadow: var(--shadow-1);
  overflow: hidden;
  transition: border-color var(--t-med), transform var(--t-med);
}

.tile:hover {
  border-color: color-mix(in srgb, var(--tone) 40%, transparent);
  transform: translateY(-2px);
}

.tone-blue { --tone: var(--blue); --tone-2: var(--blue-2); }
.tone-emerald { --tone: var(--emerald); --tone-2: var(--emerald-2); }
.tone-amber { --tone: var(--amber); --tone-2: var(--amber-2); }
.tone-rose { --tone: var(--rose); --tone-2: var(--rose-2); }
.tone-violet { --tone: var(--violet); --tone-2: #c3b2ff; }

.tile-icon {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 13px;
  background: color-mix(in srgb, var(--tone) 16%, transparent);
  color: var(--tone-2);
  border: 1px solid color-mix(in srgb, var(--tone) 30%, transparent);
  flex-shrink: 0;
}

.tile-body {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.tile-value {
  font-size: clamp(1.45rem, 2vw, 1.9rem);
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tile-hint {
  font-size: 0.78rem;
  color: var(--ink-3);
}

.tile-glow {
  position: absolute;
  right: -40px;
  top: -40px;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--tone) 35%, transparent) 0%, transparent 70%);
  pointer-events: none;
}
</style>
