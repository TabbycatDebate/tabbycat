<template>
  <div class="draw-header subtitle">

    <slot name="hbracket" v-if="roundInfo.roundIsPrelim">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('bracket')">
        <span data-toggle="tooltip" title="Debate's Bracket">
          <span><i data-feather="bar-chart-2"></i></span>
          <span :class="sortClasses('bracket')"></span>
        </span>
      </div>
    </slot>

    <slot name="hliveness" v-if="roundInfo.roundIsPrelim">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('liveness')">
        <span data-toggle="tooltip" title="How many break categories are live in this room">
          <span><i data-feather="heart"></i></span>
          <span :class="sortClasses('liveness')"></span>
        </span>
      </div>
    </slot>

    <slot name="himportance">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('importance')">
        <span data-toggle="tooltip" title="The assigned priority value of this debate">
          <span><i data-feather="thermometer"></i></span>
          <span :class="sortClasses('importance')"></span>
        </span>
      </div>
    </slot>

    <slot name="hvenue">
      <div class="vue-sortable thead flex-cell flex-6" @click="resort('venue')">
        <span data-toggle="tooltip" title="The venue of this debate">
          <span><i data-feather="map-pin"></i></span>
          <span :class="sortClasses('venue')"></span>
        </span>
      </div>
    </slot>

    <slot name="hteams">
      <div class="vue-sortable thead flex-cell flex-6 draw-team-cell"
           v-for="position in positions" @click="resort(position.side)">
        <div class="cell-padding-helper"
             data-toggle="tooltip" :title="'The ' + position.position + ' team'">
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

    <slot name="hextra"></slot>

  </div>
</template>

<script>
import SortableHeaderMixin from '../../tables/SortableHeaderMixin.vue'

export default {
  mixins: [SortableHeaderMixin],
  props: { positions: Array, roundInfo: Object },
}
</script>
