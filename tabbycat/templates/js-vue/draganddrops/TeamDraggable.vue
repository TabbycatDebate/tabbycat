<template>

  <div draggable=true
       v-bind:class="[componentClasses, isDragging ? vue-is-dragging : '']"
       v-on:dragstart="handleDragStart"
       v-on:dragend="handleDragEnd"><!--
       v-on:mouseenter="show = true"
       v-on:mouseleave="show = false" -->

    <div class="draggable-prefix">
      <h4>{{ team.wins }}</h4>
    </div>
    <div class="draggable-title">
      <h5 class="no-top-margin no-bottom-margin">{{ team.short_name }}</h5>
      <span class="small text-muted subtitle">
        {{ team.institution_name }}
      </span>
    </div>

  </div>

</template>

<script>
import DraggableMixin from '../mixins/DraggableMixin.vue'

export default {
  mixins: [DraggableMixin],
  props: {
    'team': Object,
    // 'vc': { default: null },
    // 'vc-name': { default: null },
    // 'save-division-at': {},
    // 'isDragging': { default: false },
    'show': { default: false }
  },
  computed: {
    // hasPreferences: function () {
    //   if (this.team.institutional_preferences.length > 0 || this.team.team_preferences.length > 0) {
    //     return true;
    //   } else {
    //     return false;
    //   }
    // },
    // preference_allocated: function() {
    //   if (this.vcName === null) {
    //     return 'btn-default';
    //   } else if (typeof this.team.team_preferences !== 'undefined' && this.team.team_preferences.length > 0) {
    //     if (typeof this.team.team_preferences[0] !== 'undefined' && this.team.team_preferences[0].venue_category__id == this.vcName) {
    //       return 'btn-success';
    //     } else if (typeof this.team.team_preferences[1] !== 'undefined' && this.team.team_preferences[1].category__name == this.vcName) {
    //       return 'btn-success';
    //     } else if (typeof this.team.team_preferences[2] !== 'undefined' && this.team.team_preferences[2].category__name == this.vcName) {
    //       return 'btn-info';
    //     } else if (typeof this.team.team_preferences[3] !== 'undefined' && this.team.team_preferences[3].category__name == this.vcName) {
    //       return 'btn-info';
    //     } else {
    //       return 'btn-warning';
    //     }
    //   } else if (typeof this.team.institutional_preferences !== 'undefined' && this.team.institutional_preferences.length > 0) {
    //     if (typeof this.team.institutional_preferences[0] !== 'undefined' && this.team.institutional_preferences[0].category__name == this.vcName) {
    //       return 'btn-success';
    //     } else if (typeof this.team.institutional_preferences[1] !== 'undefined' && this.team.institutional_preferences[1].category__name == this.vcName) {
    //       return 'btn-success';
    //     } else if (typeof this.team.institutional_preferences[2] !== 'undefined' && this.team.institutional_preferences[2].category__name == this.vcName) {
    //       return 'btn-info';
    //     } else if (typeof this.team.institutional_preferences[3] !== 'undefined' && this.team.institutional_preferences[3].category__name == this.vcName) {
    //       return 'btn-info';
    //     } else {
    //       return 'btn-warning';
    //     }
    //   } else {
    //     return 'btn-default';
    //   }
    // }
  },
  methods: {
    // saveDivision: function() {
    //   var team_id = this.team.id;
    //   var division_id = this.team.division;
    //   $.ajax({
    //       url: this.saveDivisionAt,
    //       type: "POST",
    //       data: {
    //         'team': team_id,
    //         'division': division_id,
    //       },
    //       success:function(response){
    //         console.log('Saved team ' + team_id + ' to division ' + division_id)
    //       },
    //       error:function (xhr, textStatus, thrownError){
    //         alert('Failed to save ' + team_id + ' divisions change')
    //       }
    //   });
    // },
    // showPreferences: function() {
    //   this.show = !this.show;
    // },
    handleDragStart: function(event) {
      // this.$dispatch('started-dragging-team', this);
    },
    handleDragEnd: function(event) {
      // this.$dispatch('stopped-dragging-team');
    },
  }
}
</script>
