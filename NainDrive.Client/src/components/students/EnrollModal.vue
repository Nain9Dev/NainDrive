<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppIcon from '../AppIcon.vue'
import ModalDialog from '../ui/ModalDialog.vue'
import { createStudent } from '../../services/api'
import type { NewStudentPayload } from '../../types/contracts'
import { identityHint } from '../../utils/identityHint'
import { useToast } from '../../composables/useToast'
import { driveData } from '../../store/driveData'
import { formatEuro } from '../../utils/format'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'created', dni: string): void }>()

const toast = useToast()

const LICENCES = ['B', 'A2', 'C'] as const

function blank(): NewStudentPayload {
  return { dni: '', first_name: '', last_name: '', phone: '', target_license: 'B', total_advances_paid: 0 }
}

const form = ref<NewStudentPayload>(blank())
const submitting = ref(false)

const hint = computed(() => identityHint(form.value.dni))
const canSubmit = computed(
  () => hint.value.state === 'valid' && form.value.first_name.trim() && form.value.last_name.trim() && !submitting.value
)

const pkg = computed(() => driveData.packageFor(form.value.target_license))

watch(
  () => props.open,
  (v) => {
    if (v) form.value = blank()
  }
)

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  try {
    const created = await createStudent({
      ...form.value,
      dni: form.value.dni.trim().toUpperCase(),
      phone: form.value.phone.trim() || '600000000',
      total_advances_paid: Number(form.value.total_advances_paid) || 0,
    })
    toast.success(`${created.first_name} matriculado`)
    emit('created', created.dni)
    emit('close')
  } catch (err: unknown) {
    toast.error(err instanceof Error ? err.message : 'No se pudo matricular')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <ModalDialog :open="open" title="Nuevo alumno" eyebrow="Matrícula" :width="560" @close="emit('close')">
    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label class="field-label" for="enroll-dni">DNI / NIE</label>
        <div class="dni-wrap" :class="hint.state">
          <input
            id="enroll-dni"
            v-model="form.dni"
            class="input lg"
            placeholder="12345678Z"
            autocomplete="off"
            spellcheck="false"
            maxlength="10"
          />
          <span class="dni-mark" aria-hidden="true">
            <AppIcon v-if="hint.state === 'valid'" name="check" :size="20" />
            <AppIcon v-else-if="hint.state === 'invalid'" name="x" :size="20" />
          </span>
        </div>
        <span class="hint" aria-live="polite">
          <template v-if="hint.state === 'invalid'">Letra esperada <strong class="mono">{{ hint.expected }}</strong></template>
          <template v-else-if="hint.state === 'shape'">{{ hint.message }}</template>
          <template v-else-if="hint.state === 'valid'">Checksum módulo 23 correcto</template>
          <template v-else>&nbsp;</template>
        </span>
      </div>

      <div class="row">
        <div class="field">
          <label class="field-label" for="enroll-first">Nombre</label>
          <input id="enroll-first" v-model="form.first_name" class="input" required autocomplete="off" />
        </div>
        <div class="field">
          <label class="field-label" for="enroll-last">Apellidos</label>
          <input id="enroll-last" v-model="form.last_name" class="input" required autocomplete="off" />
        </div>
      </div>

      <div class="field">
        <span class="field-label">Permiso</span>
        <div class="lic-grid" role="radiogroup" aria-label="Permiso">
          <button
            v-for="l in LICENCES"
            :key="l"
            type="button"
            role="radio"
            class="lic-opt"
            :class="[`lic-${l}`, { on: form.target_license === l }]"
            :aria-checked="form.target_license === l"
            @click="form.target_license = l"
          >
            <span class="lic-code display">{{ l }}</span>
            <span class="lic-name">{{ l === 'B' ? 'Turismo' : l === 'A2' ? 'Moto' : 'Camión' }}</span>
          </button>
        </div>
        <span v-if="pkg" class="hint dim">
          {{ formatEuro(pkg.enrollment_fee) }} · {{ pkg.included_practical_classes }} clases incluidas · extra {{ formatEuro(pkg.extra_class_price) }}
        </span>
      </div>

      <div class="row">
        <div class="field">
          <label class="field-label" for="enroll-phone">Teléfono</label>
          <input id="enroll-phone" v-model="form.phone" class="input mono" inputmode="tel" autocomplete="off" />
        </div>
        <div class="field">
          <label class="field-label" for="enroll-adv">Entrega inicial</label>
          <div class="money">
            <input id="enroll-adv" v-model.number="form.total_advances_paid" class="input mono" type="number" min="0" step="10" />
            <span class="money-unit">€</span>
          </div>
        </div>
      </div>

      <button type="submit" class="sr-only" :disabled="!canSubmit">Matricular</button>
    </form>

    <template #footer>
      <button type="button" class="btn btn-ghost" @click="emit('close')">Cancelar</button>
      <button type="button" class="btn btn-primary" :disabled="!canSubmit" @click="submit">
        <AppIcon name="plus" :size="16" />
        Matricular
      </button>
    </template>
  </ModalDialog>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.dni-wrap {
  position: relative;
}

.dni-wrap .input {
  padding-right: 3rem;
  text-transform: uppercase;
}

.dni-wrap.valid .input {
  border-color: var(--emerald);
  box-shadow: 0 0 0 4px rgba(34, 197, 139, 0.16);
}

.dni-wrap.invalid .input {
  border-color: var(--rose);
  box-shadow: 0 0 0 4px rgba(255, 77, 109, 0.14);
}

.dni-mark {
  position: absolute;
  right: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
}

.valid .dni-mark { background: rgba(34, 197, 139, 0.18); color: var(--emerald-2); }
.invalid .dni-mark { background: rgba(255, 77, 109, 0.18); color: var(--rose-2); }

.hint {
  font-size: 0.78rem;
  color: var(--ink-3);
  min-height: 1.2em;
}

.valid + .hint { color: var(--emerald-2); }

.lic-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
}

.lic-opt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
  padding: 0.75rem 0.5rem;
  border-radius: 14px;
  border: 1px solid var(--line-2);
  background: rgba(7, 11, 22, 0.6);
  color: var(--ink-2);
  transition: border-color var(--t-fast), background var(--t-fast), color var(--t-fast);
}

.lic-opt:hover {
  border-color: var(--line-3);
}

.lic-opt.on {
  background: var(--lic-soft);
  border-color: var(--lic);
  color: var(--ink);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--lic) 18%, transparent);
}

.lic-code {
  font-size: 1.4rem;
  color: var(--lic-2);
}

.lic-name {
  font-size: 0.72rem;
  font-weight: 600;
}

.money {
  position: relative;
}

.money .input {
  padding-right: 2.2rem;
}

.money-unit {
  position: absolute;
  right: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--ink-3);
  font-weight: 600;
}

@media (max-width: 520px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
