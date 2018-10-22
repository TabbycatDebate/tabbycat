<template>
  <div class="navbar-light fixed-bottom d-flex flex-column p-0">

    <div :class="['vue-droppable d-flex flex-column pb-2']">

      <section class="vc-resize-handler mx-auto mt-1 text-center"
               data-toggle="tooltip" :title="gettext('Drag to resize')">
        <i data-feather="menu" class="align-self-center mx-auto"></i>
      </section>
      <div class="d-flex">
        <div v-for="item in unallocatedItems" :is="unallocatedComponent"
             :item="item" :key="item.id"></div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  mixins: [],
  props: ['unallocatedItems', 'unallocatedComponent'],
  methods: {},
}
</script>

<style scoped>
  .vc-resize-handler {
    height: 20px;
    width: 100%;
  }
  .vc-resize-handler:hover {
    cursor: ns-resize;
  }
</style>
