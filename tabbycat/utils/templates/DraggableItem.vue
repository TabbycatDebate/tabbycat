<template>

  <div draggable=true class="d-flex m-1 align-items-center vue-draggable">

    <slot>
      <h4 class="mb-0 px-2 py-1 text-monospace vc-draggable-number vc-number">
        <slot name="number"></slot>
      </h4>
      <div class="py-1 pr-2">
        <h5 class="mb-0 vc-title no-wrap">
          <slot name="title"></slot>
        </h5>
        <h6 class="mb-0 vue-draggable-muted vc-subtitle no-wrap">
          <slot name="subtitle"></slot>
        </h6>
      </div>
    </slot>

  </div>

</template>

<script>
export default {

}
</script>

<style scoped>
  .vc-title {
    line-height: 0.9;
    font-size: 1.1rem;
  }
  .vc-number {
    letter-spacing: -3px;
  }
  .vc-subtitle {
    font-weight: normal;
    font-size: 0.7rem;
  }
</style>
