<!-- Table Template -->
<script type="text/x-template" id="team-draggable">

  <div class="vue-draggable" v-drag-and-drop v-drag-start="handleDragStart" data-index="[[ id ]]">
    <span>[[ name ]]</span>
  </div>

</script>

<!-- Team Draggable Component Behaviour -->
<script>
  Vue.component('team-draggable', {
    props: ['name', 'id'],
    template: '#team-draggable',
  })
</script>
