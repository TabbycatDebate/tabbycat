
<script type="text/x-template" id="unallocated-droppable">

    <adj-draggable v-for="adj in adjs" :adj="adj"></adj-draggable>

</script>

<script>
  Vue.component('unallocated-droppable', {
    props: {
        adjs: Array
    },
    template: 'unallocated-droppable',
  })
</script>