<template>
  <div class="navbar-light fixed-bottom d-flex border-top flex-column p-0 vc-unallocated-container">

    <droppable-item class="d-flex flex-column pt-2 px-2" :handle-drop="handleUnusedDrop"
                    :drop-context="{ 'assignment': null, 'position': null }">

      <section class="flex-fill pb-1 px-1 d-flex justify-content-between">
        <div class="small text-muted pb-1">{{ unallocatedItems.length }} unallocated and available</div>
        <i data-feather="menu" class="vc-resize-handler align-self-center mx-auto"
           data-toggle="tooltip" :title="gettext('Drag to resize')"></i>
        <div class="small pb-1">
          <span v-for="(value, key) in sorts" v-text="gettext(value.label)" @click="setSort(key)"
                :class="['text-muted pl-3', value.active === true ? 'font-weight-bold' : 'hoverable']"></span>
        </div>
      </section>
      <section class="d-flex flex-wrap pb-2">
        <div v-for="item in currentSortingMethod" :is="unallocatedComponent" :item="item" :key="item.id"
             :drag-payload="{ 'item': item.id, 'assignment': null, 'position': null }"></div>
      </section>

    </droppable-item>

  </div>
</template>

<script>
import DroppableMixin from './DroppableMixin.vue'
import DroppableItem from './DroppableItem.vue'

export default {
  mixins: [DroppableMixin],
  components: { DroppableItem },
  data: function () {
    return {
      sorts: {
        drag: {
          label: 'Sort By Drag Order', active: true, property: 'sortedUnallocatedItemsByOrder',
        },
        name: {
          label: 'Sort By Name', active: false, property: 'sortedUnallocatedItemsByName',
        },
        score: {
          label: 'Sort By Score', active: false, property: 'sortedUnallocatedItemsByScore',
        },
      },
    }
  },
  props: ['unallocatedItems', 'unallocatedComponent', 'handleUnusedDrop'],
  computed: {
    currentSortingMethod: function () {
      const activeKey = Object.values(this.sorts).filter(value => value.active)
      return this[activeKey[0].property]
      // if (this.sorts.drag.active) { return this.sortedUnallocatedItemsByOrder }
      // if (this.sorts.drag.active) { return this.sortedUnallocatedItemsByName }
      // if (this.sorts.drag.active) { return this.sortedUnallocatedItemsByOrder }
    },
    sortedUnallocatedItemsByOrder: function () {
      return this.unallocatedItems.slice(0).sort((itemA, itemB) => itemA.vue_last_modified - itemB.vue_last_modified).reverse()
    },
    sortedUnallocatedItemsByName: function () {
      // Note slice makes a copy so we are not mutating
      return this.unallocatedItems.slice(0).sort((itemA, itemB) => itemA.name.localeCompare(itemB.name))
    },
    sortedUnallocatedItemsByScore: function () {
      return this.unallocatedItems.slice(0).sort((itemA, itemB) => itemA.score - itemB.score).reverse()
    },
  },
  methods: {
    setSort: function (selectedKey) {
      Object.keys(this.sorts).forEach(key => {
        this.sorts[key].active = selectedKey === key
      })
    },
  },
}
</script>

<style scoped>
  .vc-unallocated-container {
    max-height: 50vh; /* Don't ever be more than 50% of the screen */
  }
  .vc-resize-handler:hover {
    cursor: ns-resize;
  }
</style>
