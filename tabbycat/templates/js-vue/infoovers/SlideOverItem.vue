<template>

  <div class="panel panel-info slideover-info" v-if="subject">
    <div class="list-group">

      <li class="list-group-item">
        <h4 class="no-bottom-margin no-top-margin text-center">
          {{ subject.title }}
        </h4>
      </li>

      <li v-for="tier in subject.tiers" class="list-group-item flex-horizontal">

        <div class="flex-1 btn-toolbar">
          <div class="btn-group btn-group-sm">
            <div v-for="item in tier.features[0]" :class="[item.class, 'btn btn-default']" >
              <span v-if="item.icon" :class="[item.icon, 'glyphicon']"></span>
              {{ item.title }}
            </div>
          </div>
        </div>

        <div class="flex-1 btn-toolbar">
          <div class="btn-group btn-group-sm pull-right">
            <div v-for="item in tier.features[2]" :class="[item.class, 'btn btn-default']" >
              <span v-if="item.icon" :class="[item.icon, 'glyphicon']"></span>
              {{ item.title }}
            </div>
          </div>
          <div class="btn-group btn-group-sm pull-right">
            <div v-for="item in tier.features[1]" :class="[item.class, 'btn btn-default']" >
              <span v-if="item.icon" :class="[item.icon, 'glyphicon']"></span>
              {{ item.title }}
            </div>
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
    'subject': Object,
  }
}
</script>
