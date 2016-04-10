<!-- Pie Graphs for Diversity Reports -->
<script type="text/x-template" id="pie-graph">

  <div id="[[ elementID ]]" class="d3-graph"></div>

</script>

<script>

  function InitChart(vueContext){

  }

  Vue.component('pie-graph', {
    template: '#pie-graph',
    props: {
      graphData: Array,
      width: { type: Number, default: 300 },
      height: { type: Number, default: 42 },
      padding: { type: Number, default: 5 },
    },
    computed: {
      elementID: function () {
        return "feedbackTrendForAdj" + String(this.id)
      },
    },
    ready: function() {
      if (this.graphData !== undefined) {
        InitChart(this); // Only init if we have some info
      }
    },
  })

</script>
