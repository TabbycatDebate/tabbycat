<!-- Table Template -->
<script type="text/x-template" id="team-draggable">

  <div class="vue-draggable" v-bind:class="{ 'vue-is-dragging': isDragging }"
    draggable=true v-on:dragstart="handleDragStart" v-on:dragend="handleDragEnd" data-id="[[ team.id ]]"
    v-on:mouseenter="show = true" v-on:mouseleave="show = false"
    title="Popover title" data-content="And here's some amazing content. It's very engaging. Right?"
  >
    <span>[[ team.institution__code ]] [[ team.short_reference ]]</span>
  </div>

  <div class="panel panel-info slideover-info" v-show="show" transition="expand">
    <div class="panel-body">
      Panel content
    </div>
  </div>

</script>

<!-- Team Draggable Component Behaviour -->
<script>
  Vue.component('team-draggable', {
    props: {
      'team': {},
      'save-division-at': {},
      'isDragging': { default: false },
      'show': { default: false }
    },
    template: '#team-draggable',
    methods: {
      saveDivision: function() {
        console.log('test');
        var team_id = this.team.id;
        var division_id = this.team.division;
        $.ajax({
            url: this.saveDivisionAt,
            type: "POST",
            data: {
              'team': team_id,
              'division': division_id,
            },
            success:function(response){
              console.log('Saved team ' + team_id + ' to division ' + division_id)
            },
            error:function (xhr, textStatus, thrownError){
              alert('Failed to save ' + team_id + ' divisions change')
            }
        });
      },
      showPreferences: function() {
        this.show = !this.show;
      },
      handleDragStart: function(elem) {
        // console.log('handleDragStart', elem);
        this.isDragging = true;
        this.$dispatch('dragging-team', this);
      },
      handleDragEnd: function(elem) {
        this.isDragging = false;
        // console.log('handleDragEnd', elem);
        this.$dispatch('stopped-dragging');
      },

    }

  })
</script>
