<!-- Table Template -->
<script type="text/x-template" id="team-draggable">

  <div class="vue-draggable" v-drag-and-drop v-drag-start="handleDragStart" v-drag-end="handleDragEnd" data-id="[[ team.id ]]">
    <span>[[ team.institution__code ]] [[ team.short_reference ]]</span>
  </div>

</script>

<!-- Team Draggable Component Behaviour -->
<script>
  Vue.component('team-draggable', {
    props: ['team'],
    template: '#team-draggable',
    methods: {
      handleDragStart: function(elem) {
        console.log('handleDragStart', elem);
      },
      handleDragEnd: function(elem) {
        console.log('handleDragEnd', elem);
      },
    }
  })
</script>
