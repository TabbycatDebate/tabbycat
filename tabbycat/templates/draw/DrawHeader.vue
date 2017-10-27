<template>
  <div class="draw-header subtitle">

    <slot name="hbracket" v-if="roundInfo.roundIsPrelim">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('bracket')"
           data-toggle="tooltip" title="Debate's Bracket">
        <i data-feather="bar-chart-2" class="tooltip-trigger"></i>
        <div :class="sortClasses('bracket')">
          <span class="sorting-placeholder-for-width"></span>
          <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
        </div>
      </div>
    </slot>

    <slot name="hliveness" v-if="roundInfo.roundIsPrelim && roundInfo.teamsInDebate !== 'bp'">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('liveness')"
           data-toggle="tooltip" title="How many break categories are live in this room">
        <i data-feather="heart" class="tooltip-trigger"></i>
        <div :class="sortClasses('liveness')">
          <span class="sorting-placeholder-for-width"></span>
          <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
        </div>
      </div>
    </slot>

    <slot name="himportance">
      <div class="vue-sortable thead flex-cell flex-1 flex-horizontal-center" @click="resort('importance')"
           data-toggle="tooltip" title="The assigned priority value of this debate">
        <i data-feather="thermometer" class="tooltip-trigger"></i>
        <div :class="sortClasses('importance')">
          <span class="sorting-placeholder-for-width"></span>
          <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
        </div>
      </div>
    </slot>

    <slot name="hvenue">
      <div class="vue-sortable thead flex-cell flex-6" @click="resort('venue')"
           data-toggle="tooltip" title="The venue of this debate">
        <i data-feather="map-pin" class="tooltip-trigger"></i>
        <div :class="sortClasses('venue')">
          <span class="sorting-placeholder-for-width"></span>
          <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
        </div>
      </div>
    </slot>

    <slot name="hteams">
      <div class="vue-sortable thead flex-cell flex-6 draw-team-cell"
           v-for="position in roundInfo.teamPositions" @click="resort(position)"
           data-toggle="tooltip" :title="'The ' + position + ' team'">
        <span>{{ position }}</span>
        <div :class="sortClasses(position)">
          <span class="sorting-placeholder-for-width"></span>
          <i data-feather="chevrons-down"></i><i data-feather="chevrons-up"></i>
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
import SortableHeaderMixin from '../tables/SortableHeaderMixin.vue'

export default {
  mixins: [SortableHeaderMixin],
  props: { roundInfo: Object },
}
</script>
