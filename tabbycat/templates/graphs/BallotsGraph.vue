<template id="ballots-graph">
  <div>

    <svg id="ballotsStatusGraph" class="d3-graph"
         style="margin-top: -15px; margin-bottom: -15px; width: 100%;"></svg>
    <div v-if="!graphData" class="text-center">
      No ballots in for this round yet
    </div>

  </div>
</template>

<script>
var d3 = require("d3");

export default {
  props: {
    height: { type: Number, default: 200 },
    padding: { type: Number, default: 10 },
    graphData: { type: Array,  default: false }
  },
  mounted: function() {
    initChart(this) // Don't init if no data is present
  },
  watch: {
    graphData: function (val, oldVal) {
      console.log('graphData new: %s, old: %s', val, oldVal)
      if (this.graphData.length > 0) {
        initChart(this) // Don't init if no data is present
      }
    }
  }
}

function initChart(vueContext){

  // Based on https://bl.ocks.org/caravinden/8979a6c1063a4022cbd738b4498a0ba6

  // Responsive width
  var pad = vueContext.padding
  var bounds = d3.select('#ballotsStatusGraph').node().getBoundingClientRect()
  var width = parseInt(bounds.width - (pad * 2));
  var height = parseInt(bounds.height);
  var margin = {top: pad, right: pad, bottom: pad, left: pad}

  var stackKey = ["none", "draft", "confirmed"];
  var data = [
    {"time":"2018-01-20T18:31:05.000","total":50,"confirmed":0,"none":20,"draft":5},
    {"time":"2018-01-20T18:42:05.000","total":50,"confirmed":1,"none":10,"draft":9},
    {"time":"2018-01-20T18:45:05.000","total":50,"confirmed":1,"none":10,"draft":6},
    {"time":"2018-01-20T18:54:05.000","total":50,"confirmed":5,"none":10,"draft":2},
    {"time":"2018-01-20T18:55:05.000","total":50,"confirmed":2,"none":1,"draft":13},
    {"time":"2018-01-20T18:59:06.000","total":50,"confirmed":8,"none":8,"draft":7}
  ]

  var parseDate = d3.isoParse // Date is ISO; parse as such
  var color = d3.scaleOrdinal(d3.schemeCategory20)

  var xScale = d3.scaleBand().range([0, width]).padding(0.1)
  var yScale = d3.scaleLinear().range([height, 0])
  var xAxis = d3.axisBottom(xScale).tickFormat(d3.timeFormat("%H:%M"))
  var yAxis = d3.axisLeft(yScale)

  var svg = d3.select("#ballotsStatusGraph").append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", "translate(" + pad * 2.5 + "," + pad * -2.5 + ")");

  var stack = d3.stack()
    .keys(stackKey)
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone);

  console.log(d3.max(data, function(d) { return d.total }))

  var layers = stack(data);
    data.sort(function(a, b) { return b.total - a.total; });
    xScale.domain(data.map(function(d) {
      return parseDate(d.time); // x-scale derives from time sequence
    }));
    yScale.domain([0, d3.max(data, function(d) {
      return d.total; // y-scale is total ballots reported
    })]).nice();

  var layer = svg.selectAll(".layer")
    .data(layers)
    .enter().append("g")
    .attr("class", "layer")
    .style("fill", function(d, i) { return color(i); });

  layer.selectAll("rect")
    .data(function(d) { return d; })
    .enter().append("rect")
      .attr("x", function(d) { return xScale(parseDate(d.data.time)); })
      .attr("y", function(d) { return yScale(d[1]); })
      .attr("height", function(d) { return yScale(d[0]) - yScale(d[1]); })
      .attr("width", xScale.bandwidth());

  svg.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + (height) + ")")
    .call(xAxis);

  svg.append("g")
    .attr("class", "axis axis--y")
    .attr("transform", "translate(0, 0)")
    .call(yAxis);

}
</script>
