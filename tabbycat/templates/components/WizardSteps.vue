<script setup>
import { useDjangoI18n } from '../composables/useDjangoI18n.js'

// Complete steps may supply a link or a value submitted to the wizard form.
// Current/upcoming steps remain labels, so navigation cannot bypass validation.
defineProps({
  steps: { type: Array, required: true },
  formId: { type: String, default: undefined },
  submitName: { type: String, default: 'wizard_goto_step' },
})

const { gettext } = useDjangoI18n()
</script>

<template>
  <ol
    class="wizard-steps mb-4"
    :aria-label="gettext('Wizard steps')"
  >
    <li
      v-for="(step, index) in steps"
      :key="step.key || index"
      class="wizard-step"
      :class="`wizard-step-${step.state}`"
      :aria-current="step.state === 'current' ? 'step' : undefined"
    >
      <span
        class="wizard-step-number"
        aria-hidden="true"
      >
        {{ step.state === 'complete' ? '✓' : index + 1 }}
      </span>
      <a
        v-if="step.state === 'complete' && step.href"
        :href="step.href"
        class="wizard-step-action"
      >
        {{ step.label }}
      </a>
      <button
        v-else-if="step.state === 'complete' && step.value != null && formId"
        type="submit"
        :form="formId"
        :name="submitName"
        :value="step.value"
        class="wizard-step-action"
        formnovalidate
      >
        {{ step.label }}
      </button>
      <span v-else>{{ step.label }}</span>
    </li>
  </ol>
</template>

<style scoped>
.wizard-steps {
  display: flex;
  flex-wrap: wrap;
  gap: .75rem 1.5rem;
  padding: 1rem 0;
  list-style: none;
  border-bottom: 1px solid #dee2e6;
}
.wizard-step {
  display: flex;
  align-items: center;
  gap: .5rem;
  font-size: .875rem;
  color: #6c757d;
}
.wizard-step-current {
  font-weight: 600;
  color: #663da0;
}
.wizard-step-number {
  display: inline-flex;
  width: 1.75rem;
  height: 1.75rem;
  align-items: center;
  justify-content: center;
  border: 1px solid currentColor;
  border-radius: 50%;
  flex-shrink: 0;
}
.wizard-step-current .wizard-step-number {
  background: #663da0;
  color: white;
}
.wizard-step-complete .wizard-step-number {
  background: #f0ebf6;
  color: #663da0;
  border-color: transparent;
}
.wizard-step-action {
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  cursor: pointer;
}
.wizard-step-action:hover, .wizard-step-action:focus {
  color: #663da0;
  text-decoration: underline;
}
@media (max-width: 575px) {
  .wizard-step {
    font-size: .75rem;
  }
}
</style>
