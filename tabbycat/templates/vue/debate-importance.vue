<!-- Table Template -->
<script type="text/x-template" id="debate-importance">

  <td>

    <span class="hidden">
      [[ importance ]]
    </span>

    <select class="form-control input-sm" v-model="importance">
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
      importance: Number,
      id: Number,
      url: String
    },
    computed: {
      example: function () {
        console.log(this.importance);
        $.ajax({
          type: "POST",
          url: this.id,
          data: {
            debate_id: this.id,
            value: this.importance
          },
        });
      }
    }
  })

  pluginComponents.push({
    template: 'debate-importance',
    reference: debateImportance
  })

</script>
