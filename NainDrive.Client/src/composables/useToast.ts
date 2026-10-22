import { reactive } from 'vue'

export type ToastKind = 'success' | 'error' | 'info'

export interface Toast {
  id: number
  kind: ToastKind
  text: string
}

const state = reactive<{ items: Toast[] }>({ items: [] })
let nextId = 1

function push(kind: ToastKind, text: string, ttl = 3200) {
  const id = nextId++
  state.items.push({ id, kind, text })
  window.setTimeout(() => dismiss(id), ttl)
}

function dismiss(id: number) {
  const idx = state.items.findIndex((t) => t.id === id)
  if (idx !== -1) state.items.splice(idx, 1)
}

export function useToast() {
  return {
    toasts: state,
    success: (text: string) => push('success', text),
    error: (text: string) => push('error', text, 4500),
    info: (text: string) => push('info', text),
    dismiss,
  }
}
