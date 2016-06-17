<!-- Table Template -->
<script type="text/x-template" id="debate-importance">

  <td>

    <span class="hidden">
      [[ componentData.importance ]]
    </span>

    <select class="form-control input-sm" v-model="componentData.importance" v-on:change="updateImportance">
      <option value="1">1</option>
      <option value="2">2</option>
      <option value="3">3</option>
      <option value="4">4</option>
      <option value="5">5</option>
    </select>

  </td>

</script>

<!-- Table Component Behaviour -->
<script>

  // Define the component
  var debateImportance = Vue.extend({
    template: '#debate-importance',
    props: {
      componentData: Object,
    },
    methods: {
      updateImportance: function () {
        $.ajax({
          type: "POST",
          url: this.componentData.url,
          data: {
            debate_id: this.componentData.id,
            importance: this.componentData.importance
          },
          error: function(XMLHttpRequest, textStatus, errorThrown) {
            $('#modalAlert').modal();
            $('#modalAlert').find('.modal-title').text('Save Failed')
            $('#modalAlert').find('.modal-body').text(
              'Failed to save a change to a debates importance. ' +
              'Try making the change again, otherwise try refreshing the page.'
            )
            console.log("Status: " + textStatus);
            console.log("Error: " + errorThrown);
          }
        });
      }
    }
  })
  pluginComponents.push({
    template: 'debate-importance',
    reference: debateImportance
  })

</script>
