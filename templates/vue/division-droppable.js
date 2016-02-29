<!-- Table Template -->
<script type="text/x-template" id="division-droppable">

  <div class="col-md-3">
    <div class="panel panel-default" v-bind:class="{ 'panel-danger': hasEvenNumbers }">

      <div class="panel-heading division-heading">

        <h5>D[[ division.name ]] ([[ teams.length ]])</h5>

        <select name="select" class="form-control" v-model="division.venue_group">

          <option value=""></option>
          <option v-for="vg in vgs" value="[[ vg.id ]]" v-bind:value="vg.id">
            [[ vg.short_name ]]
          </option>

        </select>

      </div>

      <div class="panel-body division-droppable" v-on:dragover.prevent v-on:drop="receiveTeam"
        v-on:dragenter="handleDragEnter" v-on:dragleave="handleDragLeave"
        v-bind:class="{ 'vue-is-drag-enter': isDroppable }" data-id="[[ division.id ]]">
        <template v-for="team in teams" track-by="id">
          <team-draggable :team="team" :vg="division.venue_group" :save-division-at="saveDivisionAt"></team-draggable>
        </template>

      </div>

    </div>
  </div>

</script>

<!-- Division Droppable Component Behaviour -->
<script>
  Vue.component('division-droppable', {
    props: {
      'division': {},
      'vgs': {},
      'teams': {},
      'save-vg-at': {},
      'save-division-at': {},
      'isDroppable': { default: false },
      'dragCounter': { default: 0 }
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
    computed: {
      // a computed getter
      hasEvenNumbers: function () {
        // `this` points to the vm instance
        return (this.teams.length % 2) == 1;
      }
    },
    methods: {
      handleDragEnter: function(elem) {
        // console.log('handleDragStart', elem);
        this.dragCounter++;
        console.log(this.dragCounter);
        this.isDroppable = true;
      },
      handleDragLeave: function(elem) {
        this.dragCounter--;
        console.log(this.dragCounter);
        if (this.dragCounter == 0) {
          this.isDroppable = false;
        }
      },
      receiveTeam: function(ev) {
        // This calls up to the parent component
        console.log('child component (' + this.division.id + ') received a team');
        this.$dispatch('assign-team-to-division', this.division);
        this.isDroppable = false;
        this.dragCounter = 0;
      }

    }
  })
</script>
