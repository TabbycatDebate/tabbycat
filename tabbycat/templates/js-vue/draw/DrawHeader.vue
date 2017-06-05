<template>
  <div class="draw-header subtitle">

    <slot name="hbacket">
      <div class="thead flex-cell flex-1" data-toggle="tooltip" title="Debate's Bracket">
        <span class="glyphicon glyphicon-stats"></span>
      </div>
    </slot>

    <slot name="hcats">
      <div class="thead flex-cell flex-1" data-toggle="tooltip" title="How many break categories are live in this room">
        <span class="glyphicon glyphicon-heart"></span>
      </div>
    </slot>

    <slot name="himportance">
      <div class="thead flex-cell flex-1" data-toggle="tooltip" title="The assigned priority value of this debate">
        <span class="glyphicon glyphicon-stats"></span>
      </div>
    </slot>

    <slot name="hvenue">
      <div class="thead flex-cell flex-3" data-toggle="tooltip" title="The venue of this debate">
        <span class="glyphicon glyphicon-map-marker"></span>
      </div>
    </slot>

    <slot name="hteams">
      <div class="thead flex-cell flex-6 debate-team" data-toggle="tooltip" title="test"
        v-for="position in positions">
      {{ position }}
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
export default {
  props: {
    positions: Array,
  }
}
</script>