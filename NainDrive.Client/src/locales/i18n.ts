import { ref } from 'vue'

export type Locale = 'es' | 'en'

const STORAGE_KEY = 'nain_locale'
const EVENT_NAME = 'nain:locale-change'

function getInitialLocale(): Locale {
  if (typeof window === 'undefined') return 'es'
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'es' || stored === 'en') return stored
  return 'es'
}

export const currentLocale = ref<Locale>(getInitialLocale())

export function setLocale(locale: Locale) {
  if (currentLocale.value === locale) return
  currentLocale.value = locale
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, locale)
    window.dispatchEvent(new CustomEvent(EVENT_NAME, { detail: { locale } }))
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener(EVENT_NAME, (event: Event) => {
    const custom = event as CustomEvent<{ locale?: Locale }>
    const target = custom.detail?.locale
    if (target === 'es' || target === 'en') {
      currentLocale.value = target
    }
  })
}

export const translations = {
  es: {
    brandTagline: 'Autoescuela',
    demoTitle: 'Datos sintéticos',
    apiOnline: 'API',
    demoMode: 'Demo',
    restoreDemo: 'Restaurar demo',
    restoreDesc: 'Vuelve a los 4 alumnos, 3 instructores y 3 convocatorias iniciales.',
    cancel: 'Cancelar',
    restore: 'Restaurar',
    demoRestored: 'Demo restaurada',
    demoRestoreFailed: 'No se pudo restaurar la demo',
  },
  en: {
    brandTagline: 'Driving School',
    demoTitle: 'Synthetic Data',
    apiOnline: 'API',
    demoMode: 'Demo',
    restoreDemo: 'Reset Demo',
    restoreDesc: 'Reverts to the 4 initial students, 3 instructors, and 3 exam sessions.',
    cancel: 'Cancel',
    restore: 'Reset',
    demoRestored: 'Demo restored',
    demoRestoreFailed: 'Failed to restore demo',
  },
} as const

export type TranslationKey = keyof typeof translations.es

export function t(key: TranslationKey): string {
  const loc = currentLocale.value
  return translations[loc][key] ?? translations.es[key] ?? key
}
