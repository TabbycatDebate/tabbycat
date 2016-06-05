<!-- Pie Graphs for Diversity Reports -->
<script type="text/x-template" id="donut-chart">

  <div :style="{
    width: this.radius * 2 + this.padding + this.padding + 'px',
    display: 'inline-block'
  }">

    <h5 class="text-center">[[ title ]]</h5

  </div>

</script>

<script>

  function InitChart(vueContext){

    var color = d3.scale.ordinal()
      .range(["#4182c4", "#ff17c4", "#00ff00", "#cbcbcb"]);

    var pie = d3.layout.pie()
        .value(function(d) { return d.count; })
        .sort(null);

    var arc = d3.svg.arc()
        .innerRadius(vueContext.radius - (vueContext.radius / 2))
        .outerRadius(vueContext.radius - vueContext.padding * 2);

    var svg = d3.select(vueContext.$el).insert("svg", ":first-child")
        .attr("width", (vueContext.radius * 2) + vueContext.padding + vueContext.padding)
        .attr("height", (vueContext.radius * 2) + vueContext.padding + vueContext.padding)
        .append("g")
        .attr("transform", "translate(" + (vueContext.radius + vueContext.padding) + "," + (vueContext.radius + vueContext.padding) + ")");

    var path = svg.selectAll("path")
        .data(pie(vueContext.graphData))
      .enter().append("path")
        .attr("fill", function(d, i) { return color(i); }) // Get color based on index of data
        .attr("d", arc);
  }

  Vue.component('donut-chart', {
    template: '#donut-chart',
    props: {
      title: String,
      graphData: Array,
      radius: { type: Number, default: 80 },
      padding: { type: Number, default: 5 },
    },
    ready: function() {
      if (this.graphData !== undefined) {
        InitChart(this); // Only init if we have some info
      }
    },
  })

</script>
