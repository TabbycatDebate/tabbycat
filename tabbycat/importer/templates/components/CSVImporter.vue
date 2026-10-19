<template>
  <div class="csv-importer">
    <slot />
  </div>
</template>

<style scoped>
.csv-importer {
  width: 100%;
}

/* Django renders form controls and errors into slots. */
:deep([hidden]) {
  display: none !important;
}

:deep(.errorlist) {
  margin-top: .5rem;
  padding-left: 1.25rem;
  color: #a71d2a;
  font-size: .875rem;
}
</style>
