<template>

  <div class="panel panel-info slideover-info" v-if="team">
    <div class="list-group">
      <li class="list-group-item">
        <h4 class="no-bottom-margin no-top-margin text-center">
          {{ team.long_name }}
        </h4>
      </li>
      <li class="list-group-item flex-horizontal">
        <div class="flex-1 btn-toolbar">
          <div class="btn-group btn-group-sm " role="group">
            <template v-for="speaker in team.speakers">
              <div :class="'btn btn-default gender-display gender-' + speaker.gender">
                {{ speaker.name }}
              </div>
            </template>
          </div>
          <div class="btn-group btn-group-sm" role="group">
            <div :class="'btn btn-default region-display region-' + team.region.seq">
              <span class="glyphicon glyphicon-globe"></span>
                {{ team.institution.name }} {{ team.region.name }}
            </div>
          </div>
        </div>
        <div class="btn-toolbar pull-right">
          <div class="btn-group btn-group-sm pull-right" role="group" v-for="bc in team.break_categories">
            <div :class="'btn category-display category-' + bc.seq">
              <span class="glyphicon glyphicon-globe"></span> {{ bc.name }}
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
  mixins: [],
  props: {
    'team': Object,
  },
  computed: {
  },
  methods: {
  }
}
</script>
