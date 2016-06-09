<!-- Pie Graphs for Diversity Reports -->
<script type="text/x-template" id="donut-chart">

  <div :style="{
    width: this.radius * 2 + this.padding + this.padding + 'px',
    display: 'inline-block'
  }">

    <h5 class="text-center">[[ title ]] ([[ total ]])</h5

  </div>

</script>

<script>

  function InitChart(vueContext){

    // Female - Male - Other - Unknown

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
        .attr("class", function(d, i) { return "d3-hoverable gender-graph " + vueContext.graphData[i].label.toLowerCase(); })
        .attr("d", arc)

    var tooltip = d3.select("body").append("div")
      .attr("class", "d3-tooltip tooltip")
      .style("opacity", 0);

    path.on('mouseover', function(d, i) {
      tooltip.html("<div class='tooltip-inner'>" + vueContext.graphData[i].count + "</div>")
        .style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px")
        .style('opacity', 1)
      d3.select(this).style('opacity', 0.5);
    });

    path.on('mouseout', function(d) {
      tooltip.style('opacity', 0)
      d3.select(this).style('opacity', 1);
    });

  }

  Vue.component('donut-chart', {
    template: '#donut-chart',
    props: {
      title: String,
      graphData: Array,
      radius: { type: Number, default: 60 },
      padding: { type: Number, default: 2 },
    },
    ready: function() {
      if (this.graphData !== undefined) {
        InitChart(this); // Only init if we have some info
      }
    },
    computed: {
      total: function() {
        total = 0;
        for (var i = 0; i < this.graphData.length; i++) {
          total += this.graphData[i].count;
        }
        return total
      }
    }
  })

</script>
