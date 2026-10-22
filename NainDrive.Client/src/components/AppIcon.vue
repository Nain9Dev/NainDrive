<script setup lang="ts">
import { computed } from 'vue'

export type IconName =
  | 'dashboard' | 'users' | 'calendar' | 'car' | 'plus' | 'euro' | 'file' | 'download'
  | 'search' | 'refresh' | 'x' | 'check' | 'fuel' | 'flag' | 'trash' | 'chevron-right'
  | 'alert' | 'github' | 'external' | 'steering' | 'award' | 'clock' | 'shield' | 'book'
  | 'minus' | 'wifi' | 'wifi-off' | 'info'

const PATHS: Record<IconName, string> = {
  dashboard: 'M4 5a1 1 0 0 1 1-1h5v7H4V5Zm0 9h6v6H5a1 1 0 0 1-1-1v-5Zm10-10h5a1 1 0 0 1 1 1v3h-6V4Zm0 7h6v8a1 1 0 0 1-1 1h-5v-9Z',
  users: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm13 10v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
  calendar: 'M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z',
  car: 'M5 17h14M5 17a2 2 0 1 1-2-2m2 2a2 2 0 1 0 2-2m10 2a2 2 0 1 0 2-2m-2 2a2 2 0 1 1-2-2M3 15l1.5-6A2 2 0 0 1 6.4 7.5h11.2a2 2 0 0 1 1.9 1.5L21 15v2H3v-2Z',
  plus: 'M12 5v14M5 12h14',
  minus: 'M5 12h14',
  euro: 'M18.5 6.5A7.5 7.5 0 0 0 6.6 10M18.5 17.5A7.5 7.5 0 0 1 6.6 14M4 10h10M4 14h10',
  file: 'M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Zm0 0v5h5M9 13h6M9 17h6',
  download: 'M12 4v12m0 0 4-4m-4 4-4-4M4 20h16',
  search: 'M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm10 2-4.3-4.3',
  refresh: 'M3 12a9 9 0 0 1 15.5-6.3L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.3L3 16M3 21v-5h5',
  x: 'M18 6 6 18M6 6l12 12',
  check: 'm5 12 5 5L20 7',
  fuel: 'M4 21V5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v16M3 21h12M14 10h2a2 2 0 0 1 2 2v4a1.5 1.5 0 0 0 3 0V9l-3-3M7 7h4v4H7V7Z',
  flag: 'M5 21V4m0 0h12l-2 4 2 4H5',
  trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 13a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-13M9 7V4h6v3',
  'chevron-right': 'm9 6 6 6-6 6',
  alert: 'M12 9v4m0 4h.01M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z',
  github: 'M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12.3 12.3 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21',
  external: 'M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5',
  steering: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm-9-3h6m6 0h6m-9 3v6',
  award: 'M12 15a6 6 0 1 0 0-12 6 6 0 0 0 0 12Zm-3.5-1.5L7 22l5-3 5 3-1.5-8.5',
  clock: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-13v5l3 2',
  shield: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Zm-3-10 2 2 4-4',
  book: 'M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 19.5A2.5 2.5 0 0 0 6.5 22H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15Z',
  wifi: 'M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0M12 20h.01M2 9a14 14 0 0 1 20 0',
  'wifi-off': 'M2 2l20 20M8.5 16a5 5 0 0 1 7 0M12 20h.01M5 12.5a10 10 0 0 1 5.3-2.8M16 10.5a10 10 0 0 1 3 2M2 9a14 14 0 0 1 4.7-3.2M14 5.2A14 14 0 0 1 22 9',
  info: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Zm0-5v-4m0-4h.01',
}

const props = withDefaults(
  defineProps<{
    name: IconName
    size?: number | string
    stroke?: number
  }>(),
  { size: 20, stroke: 1.9 }
)

const d = computed(() => PATHS[props.name])
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="stroke"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <path :d="d" />
  </svg>
</template>
