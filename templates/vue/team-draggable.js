<!-- Table Template -->
<script type="text/x-template" id="team-draggable">

  <div class="vue-draggable" v-drag-and-drop v-drag-start="handleDragStart" v-drag-end="handleDragEnd" data-id="[[ team.id ]]">
    <span>[[ team.institution__code ]] [[ team.short_reference ]]</span>
  </div>

</script>

<!-- Team Draggable Component Behaviour -->
<script>
  Vue.component('team-draggable', {
    props: ['team', 'division', 'save-division-at'],
    template: '#team-draggable',
    methods: {

      saveDivision: function(event) {
        $.ajax({
            url: this.saveDivisionAt,
            type: "POST",
            data: {
              'team': this.team.id,
              'division': this.division.id,
            },
            success:function(response){
              console.log('Saved teams\'s division')
            },
            error:function (xhr, textStatus, thrownError){
              alert('Failed to save a teams division change')
            }
        });
      },

      handleDragStart: function(elem) {
        // console.log('handleDragStart', elem);
        if (this.division != undefined ) {
          this.team.division = this.division;
        }
        this.$dispatch('dragging-team', this.team);
      },
      handleDragEnd: function(elem) {
        // console.log('handleDragEnd', elem);
        this.$dispatch('stopped-dragging');
      },
      //
      // handleDrop: function(draggedItem, droppedArea) {
      //   console.log('team component (' + draggedItem + ') was dropped on :' + droppedArea);
      //
      //   var droppedTeamID = draggedItem.getAttribute('data-id');
      //   var droppedTeam = $.grep(this.teams, function(e){ return e.id == droppedTeamID; })[0];
      //
      //   // Add team to the division
      //   this.divisions[0].teams.push(droppedTeam);
      //   this.teams = this.teams.filter(function (item) {
      //     return item.id != droppedTeamID;
      //   });
      //
      // }
    }
  })
</script>
