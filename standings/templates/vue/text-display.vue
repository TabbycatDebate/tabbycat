<!-- Pie Graphs for Diversity Reports -->
<script type="text/x-template" id="text-display">

  <div class="row">
    <template v-for="d in graphData">
      <div class="col-md-4 text-center ">
        <h3 class="no-bottom-margin text-body gender-text [[ d.label.toLowerCase() ]]">
          <template v-if="d.label != 'Overall' && d.count > 0">+</template>[[ round(d.count) ]]
        </h3>
      </div>
    </template>
  </div>

  <div class="row">
   <h5 class="text-center">[[ title ]]</h5>
  </div>

</script>

<script>

  Vue.component('text-display', {
    template: '#text-display',
    props: {
      title: String,
      graphData: Array,
    },
    methods: {
      round: function(value) {
        return parseFloat(Math.round(value * 100) / 100).toFixed(2);
      }
    }
  })

</script>
