<script setup lang="ts">
import { computed, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import StudentCard from '../components/students/StudentCard.vue'
import EnrollModal from '../components/students/EnrollModal.vue'
import { driveData } from '../store/driveData'

const emit = defineEmits<{
  (e: 'openStudent', dni: string, action?: 'classes' | 'advance' | 'exam' | 'invoice'): void
}>()

const { state } = driveData

const query = ref('')
const licence = ref<string>('all')
const enrollOpen = ref(false)

const licences = computed(() => Array.from(new Set(state.students.map((s) => s.target_license))).sort())

const list = computed(() => {
  const q = query.value.trim().toLowerCase()
  return state.students.filter((s) => {
    if (licence.value !== 'all' && s.target_license !== licence.value) return false
    if (!q) return true
    return (
      s.dni.toLowerCase().includes(q) ||
      `${s.first_name} ${s.last_name}`.toLowerCase().includes(q) ||
      s.registration_number.toLowerCase().includes(q)
    )
  })
})
</script>

<template>
  <section class="students">
    <div class="toolbar">
      <label class="search">
        <AppIcon name="search" :size="18" />
        <input v-model="query" class="search-input" type="search" placeholder="Buscar" aria-label="Buscar alumno" />
      </label>

      <div class="segmented" role="group" aria-label="Filtrar por permiso">
        <button type="button" :aria-pressed="licence === 'all'" @click="licence = 'all'">Todos</button>
        <button v-for="l in licences" :key="l" type="button" :aria-pressed="licence === l" @click="licence = l">{{ l }}</button>
      </div>

      <button type="button" class="btn btn-primary new" @click="enrollOpen = true">
        <AppIcon name="plus" :size="18" />
        <span>Alumno</span>
      </button>
    </div>

    <div v-if="state.loading" class="grid">
      <div v-for="i in 4" :key="i" class="skeleton card-skel"></div>
    </div>

    <TransitionGroup v-else-if="list.length" name="fade" tag="div" class="grid">
      <StudentCard
        v-for="s in list"
        :key="s.dni"
        :student="s"
        :pkg="driveData.packageFor(s.target_license)"
        @open="emit('openStudent', s.dni)"
        @action="emit('openStudent', s.dni, $event)"
      />
    </TransitionGroup>

    <div v-else class="empty panel">
      <AppIcon name="users" />
      <span>{{ query ? 'Sin resultados' : 'Sin alumnos' }}</span>
    </div>

    <EnrollModal :open="enrollOpen" @close="enrollOpen = false" @created="driveData.refresh(); emit('openStudent', $event)" />
  </section>
</template>

<style scoped>
.students {
  display: flex;
  flex-direction: column;
  gap: 1.1rem;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search {
  flex: 1;
  min-width: 200px;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  height: 44px;
  padding: 0 1rem;
  border-radius: 14px;
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--ink-3);
  transition: border-color var(--t-fast), box-shadow var(--t-fast);
}

.search:focus-within {
  border-color: var(--blue);
  box-shadow: 0 0 0 4px rgba(79, 140, 255, 0.16);
  color: var(--ink-2);
}

.search-input {
  flex: 1;
  background: transparent;
  border: 0;
  outline: none;
  color: var(--ink);
  font-size: 0.95rem;
}

.search-input::placeholder {
  color: var(--ink-3);
}

.new {
  height: 44px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 1rem;
}

.card-skel {
  height: 232px;
}

@media (max-width: 560px) {
  .new span {
    display: none;
  }

  .new {
    width: 44px;
    padding: 0;
  }
}
</style>
