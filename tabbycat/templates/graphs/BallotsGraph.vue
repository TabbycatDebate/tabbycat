<template id="ballots-graph">
  <div>

    <svg id="ballotsStatusGraph" class="d3-graph"
         style="margin: 10px 0 -5px 20px; width: 100%;"
         :style="{ height: height + 'px' }"></svg>
    <div v-if="!graphData" class="text-center">
      No ballots in for this round yet
    </div>

  </div>
</template>

<script>
var d3 = require("d3");

export default {
  props: {
    height: { type: Number, default: 350 },
    padding: { type: Number, default: 10 },
    graphData: { type: Array,  default: false }
  },
  mounted: function() {
    initChart(this.padding, this.height, this.graphData)
  },
  // watch: {
  //   graphData: function (val, oldVal) {
  //     console.log('graphData new: %s, old: %s', val, oldVal)
  //     if (this.graphData.length > 0) {
  //       // Don't init if no data is present
  //       // We pass data as JSON to get rid of the reactivity
  //       initChart(this.padding, JSON.stringify(this.graphData))
  //     }
  //   }
  // }
}

function initChart(pad, height, data){
  // Based on https://bl.ocks.org/caravinden/8979a6c1063a4022cbd738b4498a0ba6
  // var data = [{"time":"2018-01-20T18:31:05.000","total":50,"confirmed":0,"none":20,"draft":5}]
  var stackKey = ["none", "draft", "confirmed"];
  var parseDate = d3.isoParse // Date is ISO; parse as such
  var colors = {
    "none": "#d1185e",
    "draft": "#17a2b8",
    "confirmed": "#00bf8a",
  }

  // Responsive width
  var bounds = d3.select('#ballotsStatusGraph').node().getBoundingClientRect()
  var width = parseInt(bounds.width - pad * 4);
  var margin = {top: pad, right: pad, bottom: pad, left: pad}

  var xScale = d3.scaleBand().range([0, width]).padding(0.1)
  var xAxis = d3.axisBottom(xScale).tickFormat(d3.timeFormat("%H:%M"))
  var yScale = d3.scaleLinear().range([height, 0])
  var yAxis = d3.axisLeft(yScale)

  var svg = d3.select("#ballotsStatusGraph").append("svg")
      .attr("width", width)
      .attr("height", height)
      .append("g")
      .attr("transform", "translate(0,-25)")

  var stack = d3.stack()
    .keys(stackKey)
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone);

  console.log(d3.max(data, function(d) { return d.total }))

  var layers = stack(data);
    // data.sort(function(a, b) {
    //   return b.total - a.total;
    // });
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
    .style("fill", function(d, i) {
      return colors[d.key];
    });

  layer.selectAll("rect")
    .data(function(d) { return d; })
    .enter().append("rect")
      .attr("x", function(d) {
        return xScale(parseDate(d.data.time));
      })
      .attr("y", function(d) {
        return yScale(d[1]);
      })
      .attr("height", function(d) {
        return yScale(d[0]) - yScale(d[1]);
      })
      .attr("width", xScale.bandwidth());

  svg.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + (height) + ")")
    .call(xAxis);

  // svg.append("g")
  //   .attr("class", "axis axis--y")
  //   .attr("transform", "translate(0, 0)")
  //   .call(yAxis);

}
</script>
