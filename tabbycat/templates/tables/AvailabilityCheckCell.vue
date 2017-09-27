<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <span v-if="cellData['sort']" hidden>
      {{ cellData.available }}
    </span>
    <label class="custom-control custom-checkbox" @click="checkUpdate">
      <input type="checkbox" class="custom-control-input" v-model="cellData.available">
      <span class="custom-control-indicator"></span>
    </label>

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