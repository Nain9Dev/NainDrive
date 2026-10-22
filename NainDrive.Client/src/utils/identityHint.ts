/**
 * Live hint for the enrolment form. Mirrors the modulo 23 rule the API enforces
 * (src/domain/identity.py) so the user sees the control letter before submitting.
 * The server remains the authority: this never replaces its validation.
 */
const CONTROL_LETTERS = 'TRWAGMYFPDXBNJZSQVHLCKE'

export type IdentityHint =
  | { state: 'empty' }
  | { state: 'shape'; message: string }
  | { state: 'invalid'; expected: string; given: string }
  | { state: 'valid'; letter: string }

export function identityHint(raw: string): IdentityHint {
  const clean = raw.trim().toUpperCase().replace(/[-\s]/g, '')
  if (!clean) return { state: 'empty' }

  let digits = clean
  if (clean.startsWith('X')) digits = '0' + clean.slice(1)
  else if (clean.startsWith('Y')) digits = '1' + clean.slice(1)
  else if (clean.startsWith('Z')) digits = '2' + clean.slice(1)

  if (!/^\d{8}[A-Z]$/.test(digits)) {
    return { state: 'shape', message: '8 cifras + letra' }
  }

  const expected = CONTROL_LETTERS[Number(digits.slice(0, 8)) % 23]
  const given = digits.slice(8)
  if (given !== expected) return { state: 'invalid', expected, given }
  return { state: 'valid', letter: expected }
}
