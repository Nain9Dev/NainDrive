<script setup lang="ts">
defineProps<{ plate: string }>()
</script>

<template>
  <span class="plate mono" :aria-label="`Matrícula ${plate}`">
    <span class="eu" aria-hidden="true">
      <span class="stars">✦</span>
      <span class="country">E</span>
    </span>
    <span class="number">{{ plate }}</span>
  </span>
</template>

<style scoped>
.plate {
  display: inline-flex;
  align-items: stretch;
  height: 30px;
  border-radius: 6px;
  overflow: hidden;
  background: #f4f6fa;
  color: #101826;
  border: 1.5px solid #0f172b;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.25) inset, 0 2px 6px rgba(0, 0, 0, 0.4);
  font-weight: 700;
  font-size: 0.82rem;
  letter-spacing: 0.08em;
}

.eu {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 16px;
  background: #003399;
  color: #ffcc00;
  font-size: 0.5rem;
  line-height: 1;
  gap: 2px;
}

.country {
  color: #fff;
  font-size: 0.5rem;
  font-weight: 700;
}

.number {
  display: flex;
  align-items: center;
  padding: 0 0.55rem;
}
</style>
