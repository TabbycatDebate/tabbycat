<template>
  <div class="navbar-light fixed-bottom d-flex border-top flex-column p-0 vc-unallocated-container">

    <droppable-item class="d-flex flex-column px-2" :handle-drop="handleUnusedDrop"
                    :drop-context="{ 'assignment': null, 'position': null }">

      <section class="flex-fill mb-2 d-flex">
        <div class="small mt-2 pl-1 text-muted text-unselectable">
          <span v-for="(value, key) in sorts" v-text="gettext(value.label)" @click="setSort(key)"
                :class="['pr-2', value.active ? 'font-weight-bold' : 'hoverable']"></span>
        </div>
        <div class="vc-resize-handler flex-grow-1 mt-2 text-center"
             data-toggle="tooltip" :title="gettext('Drag to resize')">
          <i data-feather="menu" class="mx-auto d-block"></i>
        </div>
        <div class="small text-muted mt-2 mx-1 text-unselectable">
          <span @click="showUnavailable = false"
                :class="['', !showUnavailable ? 'font-weight-bold' : 'hoverable']">
              Show Available ({{ filteredAvailable.length }})
          </span>
          <span @click="showUnavailable = true"
                :class="['pl-2', showUnavailable ? 'font-weight-bold' : 'hoverable']">
              Show All ({{ filteredAll.length }})
          </span>
        </div>
      </section>
      <section class="d-flex flex-wrap pb-2 pt-2">
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
      showUnavailable: false,
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
    filtedUnallocatedItems: function () {
      return this.showUnavailable ? this.filteredAll : this.filteredAvailable
    },
    filteredAll: function () {
      return this.unallocatedItems
    },
    filteredAvailable: function () {
      return this.unallocatedItems.slice(0).filter((item) => item.available)
    },
    currentSortingMethod: function () {
      const activeKey = Object.values(this.sorts).filter(value => value.active)
      return this[activeKey[0].property]
    },
    sortedUnallocatedItemsByOrder: function () {
      return this.filtedUnallocatedItems.slice(0).sort((itemA, itemB) => {
        return itemA.vue_last_modified - itemB.vue_last_modified
      }).reverse()
    },
    sortedUnallocatedItemsByName: function () {
      // Note slice makes a copy so we are not mutating
      return this.filtedUnallocatedItems.slice(0).sort((itemA, itemB) => {
        return itemA.name.localeCompare(itemB.name)
      })
    },
    sortedUnallocatedItemsByScore: function () {
      return this.filtedUnallocatedItems.slice(0).sort((itemA, itemB) => {
        return itemA.score - itemB.score
      }).reverse()
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
    max-height: 300px; /* Don't ever be more than 50% of the screen */
  }
  .vc-resize-handler:hover {
    cursor: ns-resize;
  }
</style>
