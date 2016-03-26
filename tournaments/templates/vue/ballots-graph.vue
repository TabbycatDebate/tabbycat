
<!-- Streaming Item Updates for TournamentOverview -->
<script type="text/x-template" id="ballots-graph">

  <div id="ballotsStatusGraph" class="d3-graph text-center" v-if="graphData"></div>
  <div v-else class="text-center">No ballots in for this round</div>

</script>

<script>

  function InitChart(vueContext){

    // Responsive width
    vueContext.width = parseInt(d3.select('#ballotsStatusGraph').style('width'), 10)
    console.log(vueContext.width);

    x = d3.scale.ordinal().rangeRoundBands([0, vueContext.width])
    y = d3.scale.linear().range([vueContext.height, 0])
    z = d3.scale.ordinal().range(["blue", "green", "gray"])

    // Create Canvas and Scales
    var svg = d3.select("#ballotsStatusGraph").append("svg:svg")
      .attr("width", vueContext.width)
      .attr("height", vueContext.height + vueContext.padding + vueContext.padding)
      .append("g")
      .attr("transform", "translate(0," + vueContext.padding + ")");

    // Data Transforms and Domains
    var matrix = vueContext.graphData; // 4 columns: time_ID,none,draft,confirmed
    // console.log(matrix)
    var remapped =["c1","c2","c3"].map(function(dat, i){
      return matrix.map(function(d, ii){
          return {x: d[0], y: d[i+1] };
      })
    });
    // console.log(remapped)
    var stacked = d3.layout.stack()(remapped)
    // console.log(stacked)

    x.domain(stacked[0].map(function(d) { return d.x; }));
    y.domain([0, d3.max(stacked[stacked.length - 1], function(d) { return d.y0 + d.y; })]);

    // show the domains of the scales
    console.log("x.domain(): " + x.domain())
    console.log("y.domain(): " + y.domain())
    console.log("------------------------------------------------------------------");

    // Add a group for each column.
    var valgroup = svg.selectAll("g.valgroup")
      .data(stacked)
      .enter().append("svg:g")
      .attr("class", "valgroup")
      .style("fill", function(d, i) { return z(i); })
      .style("stroke", "rgba(255,255,255,0.25)"); // Vertical Grid lines

    // Add a rect for each date.
    var rect = valgroup.selectAll("rect")
      .data(function(d){return d;})
      .enter().append("svg:rect")
      .attr("x", function(d) {
        return x(d.x); })
      .attr("y", function(d) {
        return y(d.y0) - y(d.y); })
      .attr("height", function(d) { return y(d.y); })
      .attr("width", x.rangeBand());

    // Add Scales
    var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .tickFormat(function(d) { return "-" + d + "m"; }) // Format result
    var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")

    svg.append("g").attr("class", "x axis")
      .attr("transform", "translate(0," + vueContext.height + ")")
      .call(xAxis)

    // disable y axis for now
    // svg.append("g").attr("class", "y axis")
    //   .call(yAxis);

    // Horizontal grid
    // svg.selectAll("line.horizontalGrid").data(y.ticks()).enter()
    // .append("line")
    //     .attr({
    //         "class":"horizontalGrid",
    //         "x1" : 0,
    //         "x2" : vueContext.width,
    //         "y1" : function(d){
    //           return y(d);},
    //         "y2" : function(d){
    //           return y(d);},
    //         "fill" : "none",
    //         "shape-rendering" : "crispEdges",
    //         "stroke" : "white",
    //         "stroke-width" : "1px"
    //     });

  };


  Vue.component('ballots-graph', {
    template: '#ballots-graph',
    props: {
      pollUrl: String,
      height: { type: Number, default: 200 },
      padding: { type: Number, default: 30 },
    },
    ready: function() {
      var xhr = new XMLHttpRequest()
      var self = this
      xhr.open('GET', this.pollUrl)
      xhr.onload = function () {
        self.graphData = JSON.parse(xhr.responseText)
        InitChart(self); // Only init if we have some info
      }
      xhr.send()
    },
  })
</script>
