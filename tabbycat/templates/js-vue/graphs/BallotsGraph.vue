<template id="ballots-graph">

  <svg id="ballotsStatusGraph" class="d3-graph" style="margin-top: -15px; margin-bottom: -15px;" width="100%"></svg>
  <div v-if="graphData.length === 0" class="text-center">No ballots in for this round yet</div>

</template>

<script>
var d3 = require("d3");

export default {
  props: {
    pollUrl: String,
    height: { type: Number, default: 200 },
    padding: { type: Number, default: 30 },
    pollFrequency: { type: Number, default: 30000 }, // 30s
    graphData: { type: Number,  default: function () { return [] } }
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
}

function initChart(vueContext){

  // Responsive width
  vueContext.width = parseInt(d3.select('#ballotsStatusGraph').style('width'), 10)

  var x = d3.scale.linear().range([0, vueContext.width])
  var y = d3.scale.linear().range([0, vueContext.height])
  var z = d3.scale.ordinal().range(["#e34e42", "#f0c230", "#43ca75"]) // red-orange-green

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
          return {x: d[0], w: d[1], y: d[i+2]};
      })
  });
  var stacked = d3.layout.stack()(remapped)

  x.domain([stacked[0][0].x - stacked[0][0].w, stacked[0][stacked[0].length - 1].x]);
  y.domain([0, d3.max(stacked[stacked.length - 1], function(d) { return d.y0 + d.y; })]);

  // var area = d3.area()
  //   .x(function(d) {return x(d.x); })
  //   .y0(function(d) {return -y(d.y0); })
  //   .y1(function(d) {return -y(d.y0); });

  // Add a group for each column.
  var valgroup = svg.selectAll("g.valgroup")
    .data(stacked)
    .enter().append("svg:g")
    .attr("class", "valgroup")
    .style("fill", function(d, i) { return z(i); });

  // Add a rect for each date.
  var rect = valgroup.selectAll("rect")
    .data(function(d){return d;})
    .enter().append("svg:rect")
    .attr("x", function(d) { return x(d.x - d.w); })
    .attr("y", function(d) { return -y(d.y0) - y(d.y); })
    .attr("height", function(d) { return y(d.y); })
    .attr("width", function (d) { return x(d.x - d.w) - x(d.x); });

  function formatTimeAgo(time) {
    var formatted = "-";
    if (time > 86400)
      formatted += Math.floor(time / 86400) + "d";
    if (time > 3600)
      formatted += Math.floor((time % 86400) / 3600) + "h";
    if (time > 60)
      formatted += Math.floor((time % 3600) / 60) + "m";
    formatted += (time % 60) + "s";
    console.log(time + " " + formatted);
    return formatted;
  }

  // Add Scales
  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom")
    .tickFormat(function(d) { return formatTimeAgo(d) }) // Format result

  svg.append("g").attr("class", "x axis")
    .call(xAxis)

};

</script>