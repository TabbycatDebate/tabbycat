<template id="ballots-graph">
  <div>

    <div id="ballotsStatusGraph" class="d3-graph"
         :style="{ height: height + 'px' }"></div>
    <div v-if="!graphData" class="text-center">
      No ballots in for this round yet
    </div>

  </div>
</template>

<script>
import * as d3 from "d3";


export default {
  props: {
    height: { type: Number, default: 350 },
    padding: { type: Number, default: 10 },
    graphData: { type: Array,  default: false }
  },
  mounted: function () {
    var total = this.graphData[0].none +
      this.graphData[0].draft + this.graphData[0].confirmed;
    initChart(this.padding, this.graphData, total);
  },
  watch: {
    graphData: function (val, oldVal) {
      var total = this.graphData[0].none +
        this.graphData[0].draft + this.graphData[0].confirmed;
      initChart(this.padding, this.graphData, total);
    }
  }
}

function initChart(pad, data, total) {
  // Based on https://bl.ocks.org/mbostock/3885211
  // var data = [{"time":"2018-01-20T18:31:05.000","confirmed":0,"none":20,"draft":5}]

  if (data.length === 0) { return; } // Don't init with blank data
  var d3_data = data.map(type);
  d3.selectAll("#ballotsStatusGraph > *").remove(); // Remove prior graph

  var stackKey = ["none", "draft", "confirmed"];
  var colors = {
    "none": "#e34e42",
    "draft": "#f0c230",
    "confirmed": "#43ca75",
  };

  var chartDiv = document.getElementById("ballotsStatusGraph");
  var margin = {top: 20, right: 20, bottom: 30, left: 50};
  var width = chartDiv.clientWidth - margin.left - margin.right,
      height = chartDiv.clientHeight - margin.top - margin.bottom;

  var svg = d3.select("#ballotsStatusGraph")
    .append("svg")
    .attr("viewbox", "0 0 " + width + " " + height)
    .attr("height", "100%")
    .attr("width", "100%");

  var x = d3.scaleTime().range([0, width]),
      y = d3.scaleLinear().range([height, 0]),
      z = d3.scaleOrdinal(colors);

  var stack = d3.stack()
    .keys(stackKey)
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone);

  x.domain(d3.extent(d3_data, function(d) { return d.time; }));
  y.domain([0, total]);
  // The graph starts when the first ballot is submitted
  z.domain(stackKey);

  var area = d3.area()
      .x(function(d, i) { return x(d.data.time); })
      .y0(function(d) { return y(d[0]); })
      .y1(function(d) { return y(d[1]); });

  var g = svg.append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var layer = g.selectAll(".layer")
    .data(stack(d3_data))
    .enter().append("g")
      .attr("class", "layer");

  layer.append("path")
      .attr("class", "area")
      .style("fill", function(d) { return colors[d.key]; })
      .attr("d", area);

  g.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

  g.append("g")
      .attr("class", "axis axis--y")
      .call(d3.axisLeft(y));

  function type(d) {
    d.time = d3.isoParse(d.time); // date is ISO
    d.none = +d.none;
    d.draft = +d.draft;
    d.confirmed = +d.confirmed;
    return d;
  }

}
</script>
