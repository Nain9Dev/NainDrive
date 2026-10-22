<script setup lang="ts">
import AppIcon, { type IconName } from './AppIcon.vue'

export type ViewKey = 'dashboard' | 'students' | 'exams' | 'fleet'

export interface NavItem {
  key: ViewKey
  label: string
  icon: IconName
  count?: number
}

defineProps<{
  items: NavItem[]
  active: ViewKey
}>()

const emit = defineEmits<{ (e: 'select', key: ViewKey): void }>()
</script>

<template>
  <nav class="rail" aria-label="Secciones">
    <ul>
      <li v-for="item in items" :key="item.key">
        <button
          type="button"
          class="rail-btn"
          :class="{ active: item.key === active }"
          :aria-current="item.key === active ? 'page' : undefined"
          @click="emit('select', item.key)"
        >
          <span class="rail-icon">
            <AppIcon :name="item.icon" :size="22" />
            <span v-if="item.count !== undefined && item.count > 0" class="rail-count mono">{{ item.count }}</span>
          </span>
          <span class="rail-label">{{ item.label }}</span>
        </button>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.rail {
  position: sticky;
  top: calc(var(--eco-bar-h) + 1rem);
  align-self: flex-start;
  width: var(--rail-w);
  flex-shrink: 0;
}

ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.5rem;
  background: var(--panel);
  backdrop-filter: blur(18px);
  border: 1px solid var(--line);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow-1);
}

.rail-btn {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 0.7rem 0.25rem 0.6rem;
  border-radius: 18px;
  color: var(--ink-3);
  transition: background var(--t-fast), color var(--t-fast);
}

.rail-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--ink-2);
}

.rail-btn.active {
  background: linear-gradient(160deg, rgba(79, 140, 255, 0.22), rgba(79, 140, 255, 0.08));
  color: var(--ink);
  box-shadow: inset 0 0 0 1px rgba(79, 140, 255, 0.35);
}

.rail-btn.active::before {
  content: '';
  position: absolute;
  left: -0.5rem;
  top: 22%;
  height: 56%;
  width: 3px;
  border-radius: 3px;
  background: var(--blue-2);
  box-shadow: 0 0 10px var(--blue);
}

.rail-icon {
  position: relative;
  display: grid;
  place-items: center;
}

.rail-count {
  position: absolute;
  top: -7px;
  right: -12px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  background: var(--bg-3);
  border: 1px solid var(--line-2);
  color: var(--ink-2);
  font-size: 0.66rem;
  font-weight: 700;
  display: grid;
  place-items: center;
}

.rail-btn.active .rail-count {
  background: var(--blue);
  border-color: var(--blue);
  color: #fff;
}

.rail-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

@media (max-width: 860px) {
  .rail {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: auto;
    width: 100%;
    z-index: 900;
    padding: 0 0.6rem calc(0.6rem + env(safe-area-inset-bottom));
  }

  ul {
    flex-direction: row;
    justify-content: space-around;
    border-radius: 22px;
    padding: 0.35rem;
  }

  li {
    flex: 1;
  }

  .rail-btn {
    padding: 0.5rem 0.25rem 0.45rem;
    border-radius: 16px;
  }

  .rail-btn.active::before {
    display: none;
  }
}
</style>
