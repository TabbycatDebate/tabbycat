
<!-- Streaming Item Updates for TournamentOverview -->
<script type="text/x-template" id="ballots-graph">

  <div id="ballotsStatusGraph" class="d3-graph" style="text-align: center;"></div>

</script>

<script>

  function InitChart(vueContext){

    // Create canvas
    var svg = d3.select("#ballotsStatusGraph").append("svg:svg")
      .attr("class", "chart")
      .attr("width", vueContext.width)
      .attr("height", vueContext.height)
      .append("svg:g")
      .attr("transform", "translate(10,470)");

    x = d3.scale.ordinal().rangeRoundBands([0, vueContext.width - vueContext.padding])
    y = d3.scale.linear().range([0, vueContext.height - vueContext.padding])
    z = d3.scale.ordinal().range(["red", "orange", "green"])

    console.log("RAW MATRIX---------------------------");
    // 4 columns: ID,c1,c2,c3
    var matrix = [
      [ 5475,  10, 1, 0],
      [ 5477, 5, 5, 1],
      [ 5479, 4, 6, 1],
      [ 5480,   0,  10, 1],
      [ 5481,   0,  5, 6],
      [ 5482,   0,  0, 11]
    ];
    console.log(matrix)

    console.log("REMAP---------------------------");
    var remapped =["c1","c2","c3"].map(function(dat,i){
      return matrix.map(function(d,ii){
          return {x: ii, y: d[i+1] };
      })
    });
    console.log(remapped)

    console.log("LAYOUT---------------------------");
    var stacked = d3.layout.stack()(remapped)
    console.log(stacked)

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
    .style("stroke", function(d, i) { return d3.rgb(z(i)).darker(); });

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
      .ticks(4);


    svg.append("g")
      .attr("class", "x axis")
      .call(xAxis);

    // var yAxis = d3.svg.axis()
    //   .scale(x)
    //   .orient("left");
    // svg.append("g")
    //   .attr("class", "y axis")
    //   .call(yAxis);

  };


  Vue.component('ballots-graph', {
    template: '#ballots-graph',
    props: {
      pollUrl: String,
      width: { type: Number, default: 900 },
      height: { type: Number, default: 500 },
      padding: { type: Number, default: 35 },
    },
    ready: function () {
      InitChart(this); // Only init if we have some info
    },
  })
</script>
