<template>
  <div class="draw-container allocation-container">

    <div id="messages-container"><!-- Messages container--></div>

    <section>
      <slot name="actions"></slot><!-- Actions -->
    </section>

    <section>
      <slot name="headers"></slot><!-- Debates Header -->
      <slot name="debates"></slot><!-- Debates -->
    </section>

    <section>
      <slot name="unallocated"></slot><!-- Unallocated Items -->
    </section>

    <slot name=""></slot><!-- SlideOver Item -->
    <slot name="modal"></slot><!-- Modals -->

  </div>
</template>

<script>
// The master layout for drag and drop screens; to using slots for content
export default {
  mixins: [],
}
</script>
