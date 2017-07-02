<template>
  <div class="draw-header subtitle">

    <slot name="hbacket">
      <div class="thead flex-cell flex-1 flex-horizontal-center" data-toggle="tooltip" title="Debate's Bracket">
        <span class="glyphicon glyphicon-stats"></span>
        <span class="glyphicon vue-sort-key" :class="sortClasses"></span>
      </div>
    </slot>

    <slot name="hcats">
      <div class="thead flex-cell flex-1 flex-horizontal-center" data-toggle="tooltip" title="How many break categories are live in this room">
        <span class="glyphicon glyphicon-heart"></span>
        <span class="glyphicon vue-sort-key" :class="sortClasses"></span>
      </div>
    </slot>

    <slot name="himportance">
      <div class="thead flex-cell flex-1 flex-horizontal-center" data-toggle="tooltip" title="The assigned priority value of this debate">
        <span class="glyphicon glyphicon-fire"></span>
        <span class="glyphicon vue-sort-key" :class="sortClasses"></span>
      </div>
    </slot>

    <slot name="hvenue">
      <div class="thead flex-cell flex-6" data-toggle="tooltip" title="The venue of this debate">
        <span class="glyphicon glyphicon-map-marker"></span>
        <span class="glyphicon vue-sort-key" :class="sortClasses"></span>
      </div>
    </slot>

    <slot name="hteams">
      <div class="thead flex-cell flex-6 draw-team-cell" data-toggle="tooltip" title="test"
        v-for="position in positions">
        <div class="cell-padding-helper">
          {{ position }}
          <span class="glyphicon vue-sort-key" :class="sortClasses"></span>
        </div>
      </div>
    </slot>

    <slot name="hpanel">
      <div class="thead flex-cell flex-12" data-toggle="tooltip" title="test">
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
