<!-- Table Template -->
<script type="text/x-template" id="smart-cell">

  <td :class="cellData['class'] ? cellData['class'] : null">

    <!-- Sorting key -->
    <span v-if="cellData['sort']" class="hidden">
      [[ cellData["sort"] ]]
    </span>

    <!-- Icons or Emoji -->
    <span v-if="cellData['icon']" class="glyphicon" :class="cellData['icon']">
    </span>
    <span class="emoji" v-if="cellData['emoji']">
      [[ cellData["emoji"] ]]
    </span>

    <!-- Tooltip Hovers Wrapper -->
    <span :title="cellData['tooltip']"
          :data-toggle="cellData['tooltip'] ? 'tooltip' : null"
          :v-on:hover="cellData['tooltip'] ? showTooltip  : null">

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

  </td>

</script>

<!-- Table Component Behaviour -->
<script>

  // Define the component
  var smartCell = Vue.extend({
    template: '#smart-cell',
    props: {
      cellData: Object,
    },
    methods: {
      showTooltip: function(event) {
        $(event.target).tooltip('show')
      }
    },
  })

</script>
