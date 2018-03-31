<template>
  <div class="draw-header subtitle">

    <slot name="hbracket" v-if="roundInfo.roundIsPrelim">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center"
           @click="resort('bracket')" data-toggle="tooltip"
           title="Debate's Bracket">
        <div class="d-flex align-items-end">
          <i data-feather="bar-chart-2" class="header-icon tooltip-trigger"></i>
          <div :class="sortClasses('bracket')">
            <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
          </div>
        </div>
      </div>
    </slot>

    <slot name="hliveness" v-if="roundInfo.roundIsPrelim">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center"
           @click="resort('liveness')" data-toggle="tooltip"
           title="How many break categories are live in this room">
        <div class="d-flex align-items-end">
          <i data-feather="star" class="header-icon tooltip-trigger"></i>
          <div :class="sortClasses('liveness')">
            <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
          </div>
        </div>
      </div>
    </slot>

    <slot name="himportance">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center"
           @click="resort('importance')" data-toggle="tooltip"
           title="The assigned priority value of this debate">
        <div class="d-flex align-items-end">
          <i data-feather="thermometer" class="header-icon tooltip-trigger"></i>
          <div :class="sortClasses('importance')">
            <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
          </div>
        </div>
      </div>
    </slot>

    <slot name="hvenue">
      <div class="vue-sortable thead flex-cell flex-6" @click="resort('venue')"
           data-toggle="tooltip" title="The venue of this debate">
        <div class="d-flex align-items-end">
          <i data-feather="map-pin" class="header-icon tooltip-trigger"></i>
          <div :class="sortClasses('venue')">
            <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
          </div>
        </div>
      </div>
    </slot>

    <slot name="hteams">
      <div class="vue-sortable thead flex-cell flex-6 draw-team-cell"
           v-for="position in roundInfo.teamPositions" @click="resort(position)"
           data-toggle="tooltip" :title="'The ' + position.toUpperCase() + ' team'">
        <div class="d-flex align-items-end">
          <span>{{ position.toUpperCase() }}</span>
          <div :class="sortClasses(position)">
            <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
          </div>
        </div>
      </div>
    </slot>

    <slot name="hpanel">
      <div class="thead flex-cell flex-12">
        <div class="d-flex align-items-end">
          Panel
        </div>
      </div>
    </slot>

    <slot name="hextra"></slot>

  </div>
</template>

<script>
import SortableHeaderMixin from '../tables/SortableHeaderMixin.vue'

export default {
  mixins: [SortableHeaderMixin],
  props: { roundInfo: Object },
}
</script>
