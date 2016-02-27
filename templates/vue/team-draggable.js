<!-- Table Template -->
<script type="text/x-template" id="team-draggable">

  <div class="vue-draggable btn btn-sm" v-bind:class="[preference_allocated, isDragging ? vue-is-dragging : '']"
    draggable=true v-on:dragstart="handleDragStart" v-on:dragend="handleDragEnd" data-id="[[ team.id ]]"
    v-on:mouseenter="show = true" v-on:mouseleave="show = false">
    <span>
      <span v-if="team.institution__code != 'Byes'">[[ team.institution__code ]]</span>
      [[ team.short_reference ]]
    </span>
  </div>

  <div class="panel panel-info slideover-info" v-show="show" transition="expand">
    <div class="panel-body" v-if="hasPreferences">
      <div class="btn-group" role="group">
        <button class="btn btn-sm btn-link" v-if="team.institutional_preferences.length > 0">
          Institutional
        </button>
        <button class="btn tbn-sm btn-default" v-for="preference in team.institutional_preferences">
          [[ preference.venue_group__short_name ]] <span class="badge">[[ preference.priority]]</span>
        </button>
      </div>
      <div class="btn-group pull-right" role="group">
        <button class="btn btn-sm btn-link" v-if="team.team_preferences.length > 0">
          Individual
        </button>
        <button class="btn tbn-sm btn-default" v-for="preference in team.team_preferences">
          [[ preference.venue_group__short_name ]] <span class="badge">[[ preference.priority]]</span>
        </button>
      </div>
    </div>
    <div class="panel-body" v-else="hasPreferences">
      No division preferences set
    </div>
  </div>

</script>

<!-- Team Draggable Component Behaviour -->
<script>
  Vue.component('team-draggable', {
    props: {
      'team': {},
      'vg': { default: null },
      'save-division-at': {},
      'isDragging': { default: false },
      'show': { default: false }
    },
    template: '#team-draggable',
    computed: {
      hasPreferences: function () {
        if (this.team.institutional_preferences.length > 0 || this.team.team_preferences.length > 0) {
          return true;
        } else {
          return false;
        }
      },
      preference_allocated: function() {
        if (this.vg === null) {
          return '';
        } else if (typeof this.team.team_preferences !== 'undefined' && this.team.team_preferences.length > 0) {
          if (typeof this.team.team_preferences[0] !== 'undefined' && this.team.team_preferences[0].venue_group__id == this.vg) {
            return 'btn-success';
          } else if (typeof this.team.team_preferences[1] !== 'undefined' && this.team.team_preferences[1].venue_group__id == this.vg) {
            return 'btn-success';
          } else if (typeof this.team.team_preferences[2] !== 'undefined' && this.team.team_preferences[2].venue_group__id == this.vg) {
            return 'btn-info';
          } else if (typeof this.team.team_preferences[3] !== 'undefined' && this.team.team_preferences[3].venue_group__id == this.vg) {
            return 'btn-info';
          } else {
            return 'btn-warning';
          }
        } else if (typeof this.team.institutional_preferences !== 'undefined' && this.team.institutional_preferences.length > 0) {
          if (typeof this.team.institutional_preferences[0] !== 'undefined' && this.team.institutional_preferences[0].venue_group__id == this.vg) {
            return 'btn-success';
          } else if (typeof this.team.institutional_preferences[1] !== 'undefined' && this.team.institutional_preferences[1].venue_group__id == this.vg) {
            return 'btn-success';
          } else if (typeof this.team.institutional_preferences[2] !== 'undefined' && this.team.institutional_preferences[2].venue_group__id == this.vg) {
            return 'btn-info';
          } else if (typeof this.team.institutional_preferences[3] !== 'undefined' && this.team.institutional_preferences[3].venue_group__id == this.vg) {
            return 'btn-info';
          } else {
            return 'btn-warning';
          }
        } else {
          return 'btn-default';
        }
      }
    },
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
