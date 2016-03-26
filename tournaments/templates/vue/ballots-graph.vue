
<!-- Streaming Item Updates for TournamentOverview -->
<script type="text/x-template" id="ballots-graph">

  <svg id="ballotsStatusGraph" class="d3-graph" style="margin-top: -15px; margin-bottom: -15px;" width="100%"></svg>
  <div v-if="graphData.length === 0" class="text-center">No ballots in for this round yet</div>

</script>

<script>

  function initChart(vueContext){

    // Responsive width
    vueContext.width = parseInt(d3.select('#ballotsStatusGraph').style('width'), 10)

    x = d3.scale.ordinal().rangeRoundBands([0, vueContext.width])
    y = d3.scale.linear().range([0, vueContext.height])
    z = d3.scale.ordinal().range(["#e34e42", "#f0c230", "#43ca75"]) // red-orange-green

    d3.selectAll("svg > *").remove(); // Remove prior graph

    // Create Canvas and Scales
    var svg = d3.select("#ballotsStatusGraph")
      .attr("width", vueContext.width)
      .attr("height", vueContext.height + vueContext.padding + vueContext.padding)
      .append("g")
      .attr("transform", "translate(0," + (vueContext.height + vueContext.padding) + ")");

    // Data Transforms and Domains
    var matrix = vueContext.graphData; // 4 columns: time_ID,none,draft,confirmed
    var remapped =["c1","c2","c3"].map(function(dat,i){
        return matrix.map(function(d,ii){
            return {x: d[0], y: d[i+1] };
        })
    });
    var stacked = d3.layout.stack()(remapped)

    x.domain(stacked[0].map(function(d) { return d.x; }));
    y.domain([0, d3.max(stacked[stacked.length - 1], function(d) { return d.y0 + d.y; })]);

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
      .attr("x", function(d) { return x(d.x); })
      .attr("y", function(d) { return -y(d.y0) - y(d.y); })
      .attr("height", function(d) { return y(d.y); })
      .attr("width", x.rangeBand());

    // Add Scales
    var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .tickFormat(function(d) { return "-" + d + "m"; }) // Format result


    svg.append("g").attr("class", "x axis")
      .call(xAxis)

    // disable y axis for now
    // var yAxis = d3.svg.axis()
    //   .scale(y)
    //   .orient("left")
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
      pollFrequency: { type: Number, default: 30000 }, // 30s
      graphData: { type: Number, default: [] }
    },
    methods: {
      fetchData: function () {
        var xhr = new XMLHttpRequest()
        var self = this
        xhr.open('GET', self.pollUrl)
        xhr.onload = function () {
          self.graphData = JSON.parse(xhr.responseText)
          if (self.graphData.length > 0) {
            initChart(self); // Don't init if no data is present
          }
          setTimeout(self.fetchData, self.pollFrequency);
        }
        xhr.send()
      }
    },
    created: function() {
      this.fetchData();
    },
  })
</script>
