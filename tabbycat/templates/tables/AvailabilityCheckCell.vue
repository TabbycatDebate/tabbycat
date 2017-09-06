<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData.available }}
    </span>
    <input type="checkbox" v-model="cellData.available" @click="checkUpdate">

  </td>

</template>

<script>

export default {
  props: { cellData: Object },
  methods: {
    checkUpdate: function () {
      this.$eventHub.$emit('toggle-availability', this.cellData.id,
                                                  this.cellData.available)
    },
  },
}

</script>