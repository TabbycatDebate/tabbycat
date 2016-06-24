<style lang="sass">

.adj-draggable {
  text-align: left;
  div {
    float: left;
  }
  .h4 {
    margin: 0;
    padding: 2px 6px 3px 2px; // Center the Score
  }
  span {
    border-bottom: none;
  }
  .small {
    text-transform: uppercase;
    font-size: 70%;
    display: block;
    line-height: 3px;
  }
}

</style>

<template>

  <div
    draggable=true
    v-on:dragstart="handleDragStart"
    v-on:dragend="handleDragEnd"
    v-bind:class="[isDragging ? vue-is-dragging : '']"
    class="vue-draggable adj-draggable btn btn-default"
    data-toggle="tooltip"
    title="{{ adj.name }} of {{ adj.institution.name }}">

    <div class="h4">
      {{ adj.score }}
    </div>

    <div>
      <span>
        {{ short_name }}
      </span>
      <span class="small text-muted">
        <template v-if="adj.institution.code">
          {{ adj.institution.code }}
        </template>
        <template v-else>
          {{ adj.institution.name }}
        </template>
      </span>
    </div>

  </div>

</template>

<script>
import DraggableMixin from '../mixins/DraggableMixin.vue'

export default {
  mixins: [DraggableMixin],
  props: {
    adj: Object
  },
  computed: {
    short_name: function() {
      var names = this.adj.name.split(" ")
      return names[0] + " " + names[1][0] + ".";
    }
  }
}
</script>
