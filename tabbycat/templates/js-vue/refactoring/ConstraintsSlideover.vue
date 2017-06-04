<template>

    <div class="panel panel-info slideover-info" v-if="venue">
      <div class="list-group">
        <li class="list-group-item">
          <h4 class="no-bottom-margin no-top-margin text-center">
            {{ venue.name }}
            <span v-if="!venue.categories.length">(No Categories)</span>
            <span v-else>
              (<span v-for="category in venue.categories">{{ category.name }}, </span>)
            </span>
          </h4>
        </li>
        <li class="list-group-item flex-horizontal" v-if="constraints">
          <div class="btn-toolbar center-block">
            <div class="btn-group btn-group-sm" role="group">
              <div class="btn btn-default">Teams</div>
              <div class="btn btn-danger" v-for="constraint in teamConstraints">
                {{ constraint.priority }} {{ constraint.subject_name }}
              </div>
              <div class="btn btn-default text-muted" v-if="!teamConstraints.length">No constraints</div>
            </div>
            <div class="btn-group btn-group-sm" role="group">
              <div class="btn btn-default">Adjudicators</div>
              <div class="btn btn-danger" v-for="constraint in adjudicatorConstraints">
                {{ constraint.priority }} {{ constraint.subject_name }}
              </div>
              <div class="btn btn-default text-muted" v-if="!adjudicatorConstraints.length">No constraints</div>
            </div>
            <div class="btn-group btn-group-sm " role="group">
              <div class="btn btn-default">Institutions</div>
              <div class="btn btn-danger" v-for="constraint in institutionConstraints">
                {{ constraint.priority }} {{ constraint.subject_name }}
              </div>
              <div class="btn btn-default text-muted" v-if="!institutionConstraints.length">No constraints</div>
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
    'venue': Object,
    'constraints': Array
  },
  computed: {
    teamConstraints: function(type) {
      return _.filter(this.constraints, function(c) {
        return c.subject_type == 'team'
      })
    },
    adjudicatorConstraints: function(type) {
      return _.filter(this.constraints, function(c) {
        return c.subject_type == 'adjudicator'
      })
    },
    institutionConstraints: function(type) {
      return _.filter(this.constraints, function(c) {
        return c.subject_type == 'institution'
      })
    }
  },
  methods: {
  }
}
</script>
