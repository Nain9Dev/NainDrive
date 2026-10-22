const euroFormatter = new Intl.NumberFormat('es-ES', {
  style: 'currency',
  currency: 'EUR',
})

const MONTHS_ES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]

const MONTHS_ES_SHORT = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']

export function toNumber(value: number | string | null | undefined): number {
  if (value === null || value === undefined) return 0
  const n = typeof value === 'string' ? parseFloat(value) : value
  return Number.isFinite(n) ? n : 0
}

export function formatEuro(value: number | string | null | undefined): string {
  return euroFormatter.format(toNumber(value))
}

/** Parses the API's `DD-MM-YYYY` (or ISO `YYYY-MM-DD`) into a local Date. */
export function parseEsDate(value: string | null | undefined): Date | null {
  if (!value) return null
  const dmy = /^(\d{2})-(\d{2})-(\d{4})$/.exec(value)
  if (dmy) return new Date(Number(dmy[3]), Number(dmy[2]) - 1, Number(dmy[1]))
  const iso = /^(\d{4})-(\d{2})-(\d{2})/.exec(value)
  if (iso) return new Date(Number(iso[1]), Number(iso[2]) - 1, Number(iso[3]))
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? null : d
}

/** Serialises a `<input type="date">` value (`YYYY-MM-DD`) to the API's `DD-MM-YYYY`. */
export function isoToEsDate(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  return m ? `${m[3]}-${m[2]}-${m[1]}` : iso
}

export function todayIso(): string {
  const d = new Date()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd}`
}

export function monthLabel(date: Date): string {
  return `${MONTHS_ES[date.getMonth()]} ${date.getFullYear()}`
}

export function monthShort(date: Date): string {
  return MONTHS_ES_SHORT[date.getMonth()]
}

export function daysUntil(date: Date | null): number | null {
  if (!date) return null
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return Math.round((date.getTime() - now.getTime()) / 86_400_000)
}

export function initials(first: string, last: string): string {
  const a = first.trim().charAt(0)
  const b = last.trim().charAt(0)
  return `${a}${b}`.toUpperCase()
}

export function licenceClass(licence: string): string {
  return ['B', 'A2', 'C'].includes(licence) ? `lic-${licence}` : 'lic-other'
}

const LICENCE_COLORS: Record<string, string> = {
  B: '#4f8cff',
  A2: '#22c58b',
  C: '#f5b02b',
}

export function licenceColor(licence: string): string {
  return LICENCE_COLORS[licence] ?? '#9b7dff'
}
