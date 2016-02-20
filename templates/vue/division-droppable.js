<!-- Table Template -->
<script type="text/x-template" id="division-droppable">

  <div class="col-md-3">
    <div class="panel panel-default">

      <div class="panel-heading division-heading">

        <h4>[[ division.name ]]</h4>

        <select name="select" class="form-control" v-model="division.venue_group">

          <option value=""></option>
          <option v-for="vg in vgs" value="[[ vg.id ]]" v-bind:value="vg.id">
            [[ vg.short_name ]] (x/[[ vg.team_capacity ]])
          </option>

        </select>

      </div>

      <div class="panel-body division-droppable" v-on:dragover.prevent v-on:drop="receiveTeam"
        v-on:dragenter="handleDragEnter" v-on:dragleave="handleDragLeave"
        v-bind:class="{ 'vue-is-drag-enter': isDroppable }" data-id="[[ division.id ]]">

        <template v-for="team in teams" track-by="id">
          <team-draggable :team="team"></team-draggable>
        </template>

      </div>

    </div>
  </div>

</script>

<!-- Division Droppable Component Behaviour -->
<script>
  Vue.component('division-droppable', {
    props: {
      'division': {}, 'vgs': {}, 'teams': {}, 'save-vg-at': {}, isDroppable: { default: false }
    },
    template: '#division-droppable',
    watch: {
      'division.venue_group': function (newVal, oldVal) {
        var vg_id = this.division.venue_group;
        var division_id = this.division.id;
        $.ajax({
            url: this.saveVgAt,
            type: "POST",
            data: {
              'venueGroup': vg_id,
              'division': division_id,
            },
            success:function(response){
              console.log('Saved division ' + division_id + ' to venue group ' + vg_id)
            },
            error:function (xhr, textStatus, thrownError){
              alert('Failed to save a division ' + division_id + '\s venue group change')
            }
        });
      },
    },
    methods: {
      handleDragEnter: function(elem) {
        // console.log('handleDragStart', elem);
        this.isDroppable = true;
      },
      handleDragLeave: function(elem) {
        this.isDroppable = false;
      },
      receiveTeam: function(ev) {
        // This calls up to the parent component
        console.log('child component (' + this.division.id + ') received a team');
        this.$dispatch('assign-team-to-division', this.division);
        this.isDroppable = false;
      }

    }
  })
</script>
