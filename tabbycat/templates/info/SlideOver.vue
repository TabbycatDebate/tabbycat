<template>
  <transition name="slide-over">
    <div class="panel slideover-info" v-if="subject">
      <div v-for="tier in subject.tiers" class="list-group-item flex-horizontal flex-justify">

        <div class="btn-toolbar flex-align-start">
          <div class="btn-group btn-group-sm">
            <div v-for="item in tier.features[0]" :class="[item.class, 'btn btn-primary']" >
              <span v-if="item.icon" :class="[item.icon, 'glyphicon']"></span>
              {{ item.title }}
            </div>
          </div>
          <div class="btn-group btn-group-sm">
            <div v-for="item in tier.features[1]" :class="[item.class, 'btn btn-primary']" >
              <span v-if="item.icon" :class="[item.icon, 'glyphicon']"></span>
              {{ item.title }}
            </div>
          </div>
        </div>

        <div class="btn-toolbar">
          <div class="btn-group btn-group-sm">
            <div v-for="item in tier.features[2]" :class="[item.class, 'btn btn-primary']" >
              <span v-if="item.icon" :class="[item.icon, 'glyphicon']"></span>
              {{ item.title }}
            </div>
          </div>
        </div>

      </div>
    </div>
  </transition>
</template>

<script>
export default {
  props: {
    'subject': Object,
  }
}
</script>
