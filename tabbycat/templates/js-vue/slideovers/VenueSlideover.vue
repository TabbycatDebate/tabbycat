<template>

  <transition name="expand">

    <div class="panel panel-info slideover-info" v-if="venue !== null">
      <div class="list-group">
        <li class="list-group-item">
          <h4 class="no-bottom-margin no-top-margin text-center">
            {{ venue.name }}
            (<span v-for="category in venue.categories">{{ category.name }}</span>)
          </h4>
        </li>
        <li class="list-group-item flex-horizontal">
          <div class="flex-1 btn-toolbar">
            <div class="btn-group btn-group-sm " role="group">
              <div class="'btn btn-default'">
                Team constraints
              </div>
            </div>
          </div>
          <div class="flex-1 btn-toolbar">
            <div class="btn-group btn-group-sm " role="group">
              <div class="'btn btn-default'">
                Adj constraints
              </div>
            </div>
          </div>
          <div class="flex-1 btn-toolbar">
            <div class="btn-group btn-group-sm " role="group">
              <div class="'btn btn-default'">
                Institution constraints
              </div>
            </div>
          </div>
        </li>
      </div>
    </div>

  </transition>

</template>

<script>

export default {
  mixins: [],
  props: {
    'venue': Object,
  },
  computed: {
  },
  methods: {
  }
}
</script>
