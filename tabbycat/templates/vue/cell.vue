<!-- Table Template -->
<script type="text/x-template" id="smart-cell">

  <td :class="cellData['cell-class'] ? cellData['cell-class'] : null">

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

      <!-- Text (with link if needed) -->
      <a v-if="cellData['link']" :href="cellData['link']" >
        <span v-html="cellData['text']"></span>
      </a>
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
