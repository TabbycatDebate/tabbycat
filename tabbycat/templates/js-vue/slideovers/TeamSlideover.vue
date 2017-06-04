<template>

  <div class="panel panel-info slideover-info" v-if="team">
    <div class="list-group">
      <li class="list-group-item">
        <h4 class="no-bottom-margin no-top-margin text-center">
          {{ team.long_name }}
        </h4>
      </li>
      <li class="list-group-item flex-horizontal">
        <div class="flex-3 btn-toolbar">
          <div class="btn-group btn-group-sm">
            <template v-for="speaker in team.speakers">
              <div :class="'btn btn-default gender-display gender-' + speaker.gender">
                {{ speaker.name }}
              </div>
            </template>
          </div>
        </div>

        <div class="flex-1 btn-toolbar">
          <div class="btn-group btn-group-sm center-block">
            <div :class="'btn btn-default region-display ' + regionClass">
              <span class="glyphicon glyphicon-globe"></span>
                {{ team.institution.name }}
                <span v-if="team.region">{{ team.region.name }}</span>
            </div>
          </div>
        </div>

        <div class="flex-3 btn-toolbar">
          <div class="btn-group btn-group-sm pull-right" v-for="bc in break_categories">
            <div :class="'btn category-display category-' + bc.class">
              <span class="glyphicon glyphicon-globe"></span> {{ bc.name }} Break
            </div>
        <!--     <div class="btn btn-success" v-if="bc.will_break === true">
              SAFE ({{ team.wins }} Wins)
            </div>
            <div class="btn btn-default" v-if="bc.will_break === false">
              DEAD ({{ team.wins }} Wins)
            </div>
            <div class="btn btn-danger" v-if="bc.will_break === null">
              LIVE ({{ team.wins }} Wins)
            </div> -->
          </div>
        </div>
      </li>

    </div>
  </div>

</template>

<script>
import _ from 'lodash'

export default {
  props: {
    'team': Object,
  },
  computed: {
    'break_categories': function() {
      // Buttons go right to left; so order needs to reverse
      return _.reverse(this.team.break_categories)
    },
    'regionClass': function() {
      if (this.team.region) {
        return 'region-' + this.team.region.class
      } else {
        return ''
      }
    }
  }
}
</script>
