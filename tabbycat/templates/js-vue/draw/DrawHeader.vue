<template>
  <div class="draw-header subtitle">

    <slot name="hbacket">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('bracket')"
           data-toggle="tooltip" title="Debate's Bracket">
        <i data-feather="bar-chart-2"></i>
        <span :class="sortClasses('bracket')"></span>
      </div>
    </slot>

    <slot name="hcats">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('liveness')"
           data-toggle="tooltip" title="How many break categories are live in this room">
        <span class="glyphicon glyphicon-heart"></span>
        <span :class="sortClasses('liveness')"></span>
      </div>
    </slot>

    <slot name="himportance">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('importance')"
           data-toggle="tooltip" title="The assigned priority value of this debate">
        <span class="glyphicon glyphicon-fire"></span>
        <span :class="sortClasses('importance')"></span>
      </div>
    </slot>

    <slot name="hvenue">
      <div class="vue-sortable thead flex-cell flex-6" @click="resort('venue')"
           data-toggle="tooltip" title="The venue of this debate">
        <span class="glyphicon icon-venue-location"></span>
        <span :class="sortClasses('venue')"></span>
      </div>
    </slot>

    <slot name="hteams">
      <div class="vue-sortable thead flex-cell flex-6 draw-team-cell"
           v-for="position in positions" @click="resort(position.side)"
           data-toggle="tooltip" :title="'The ' + position.full + ' team'">
        <div class="cell-padding-helper">
          <span>{{ position.abbr }}</span>
          <span :class="sortClasses(position.side)"></span>
        </div>
      </div>
    </slot>

    <slot name="hpanel">
      <div class="thead flex-cell flex-12">
        Panel
      </div>
    </slot>

  </div>
</template>

<script>
import SortableHeaderMixin from '../../tables/SortableHeaderMixin.vue'

export default {
  mixins: [SortableHeaderMixin],
  props: {
    positions: Array,
  },
}
</script>
