<!-- Table Template -->
<template>

  <td :class="cellData['class'] ? cellData['class'] : null">

    <!-- Sorting key -->
    <span v-if="cellData['sort']" class="hidden">
      {{ cellData["sort"] }}
    </span>

    <!-- Icons or Emoji -->
    <span v-if="cellData['icon']" class="glyphicon" :class="cellData['icon']">
    </span>
    <span class="emoji" v-if="cellData['emoji']">
      {{ cellData["emoji"] }}
    </span>

    <!-- Tooltip Hovers Wrapper -->
    <span
      :title="cellData['tooltip']"
      :data-toggle="cellData['tooltip'] ? 'tooltip' : null">

      <!-- Links and modals -->
      <template v-if="cellData['link'] || cellData['modal']">
        <a v-if="cellData['link']" :href="cellData['link']" >
          <span v-html="cellData['text']"></span>
        </a>
        <a v-if="cellData['modal']" :data-target="cellData['modal']" >
          <span v-html="cellData['text']"></span>
        </a>
      </template>

      <span v-else v-html="cellData['text']"></span>

    </span>

    <template v-if="cellData['subtext']">
      <br><span class="small" v-html="cellData['subtext']"></span>
    </template>

  </td>

</template>

<script>
export default {
  props: {
    cellData: Object,
  }
}
</script>
