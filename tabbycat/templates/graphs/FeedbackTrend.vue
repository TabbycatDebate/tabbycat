<template>

  <td class="unpadded-cell">
    <div class="d3-graph d3-feedback-trend"></div>
  </td>

</template>

<script>
import * as d3shape from "d3-shape";
import * as d3scale from "d3-scale";
import * as d3selection from "d3-selection";
import * as d3array from "d3-array";
import * as d3axis from "d3-axis";

export default {
  props: {
    cellData: Object,
    width: { type: Number, default: 425 },
    height: { type: Number, default: 55 },
    padding: { type: Number, default: 6 },
  },
  computed: {
    graphData: function () {
      return this.cellData.graphData
    }
  },
  mounted: function () {
    if (typeof this.graphData !== 'undefined' && this.graphData.length > 0) {
      initChart(this); // Only init if we have some info
    }
  },
  watch: {
    graphData: function () {
      if (typeof this.graphData !== 'undefined' && this.graphData.length > 0) {
        // Just remove and remake it as I cbf figuring out the in place update
        var element = $(this.$el).children(".d3-graph")[0]
        $(element).children("svg").remove()
        initChart(this)
      }
    }
  }
}

// returns slope, intercept and r-square of the line
function leastSquares(xSeries, ySeries) {
  var reduceSumFunc = function (prev, cur) { return prev + cur; };

  var xBar = xSeries.reduce(reduceSumFunc) * 1.0 / xSeries.length;
  var yBar = ySeries.reduce(reduceSumFunc) * 1.0 / ySeries.length;

  var ssXX = xSeries.map(function (d) { return Math.pow(d - xBar, 2); })
    .reduce(reduceSumFunc);

  var ssYY = ySeries.map(function (d) { return Math.pow(d - yBar, 2); })
    .reduce(reduceSumFunc);

  var ssXY = xSeries.map(function (d, i) { return (d - xBar) * (ySeries[i] - yBar); })
    .reduce(reduceSumFunc);

  var slope = ssXY / ssXX;
  var intercept = yBar - (xBar * slope);
  var rSquare = Math.pow(ssXY, 2) / (ssXX * ssYY);

  return [slope, intercept, rSquare];
}

function initChart(vueContext){

  // Range is the pixel coordinates; domain is the axes range
  var xScale = d3scale.scaleLinear()
    .range([0, vueContext.width])
    .domain([0, vueContext.cellData.roundSeq])

  var yScale = d3scale.scaleLinear()
    .range([vueContext.height, 0])
    .domain([vueContext.cellData.minScore, vueContext.cellData.maxScore])

  // Scale axis to fit the range specified
  var xAxis = d3axis.axisBottom(xScale)
    .tickSizeInner(-vueContext.height)
    .tickSizeOuter(0)
    .tickFormat(function (d) { return ''; }) // Hide ticks
    .tickValues(d3array.range(0, vueContext.cellData.roundSeq + 0.5, 1)) // Set tick increments

  var yAxis = d3axis.axisLeft(yScale)
    .tickSizeInner(-vueContext.width)
    .tickSizeOuter(0)
    .tickPadding(10)
    .tickFormat(function (d) { return ''; }) // Hide ticks
    // Set tick increments
    .tickValues(d3array.range(vueContext.cellData.minScore, vueContext.cellData.maxScore + 0.5, 1))

  // Define the div for the tooltip
  var div = d3selection.select("body").append("div")
    .attr("class", "d3-tooltip tooltip")
    .style("opacity", 0);

  var element = $(vueContext.$el).children(".d3-graph")[0]
  var svg = d3selection.select(element).insert("svg", ":first-child")
      .attr("width", vueContext.width + vueContext.padding + vueContext.padding)
      .attr("height", vueContext.height + vueContext.padding  + vueContext.padding)
    .append("g")
      .attr("transform", "translate(" + vueContext.padding + "," + vueContext.padding + ")");

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + vueContext.height + ")")
      .call(xAxis)

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)

  // Create series for regression
  var xLabels = vueContext.graphData.map(function (d) { return d['x']; })
  var xSeries = d3array.range(1, xLabels.length + 1);
  var ySeries = vueContext.graphData.map(function (d) {
    return parseFloat(d['y']);
  });
  var leastSquaresCoeff = leastSquares(xSeries, ySeries);

  if (!isNaN(leastSquaresCoeff[0]) && !isNaN(leastSquaresCoeff[1])) {
    // apply the reults of the least squares regression (if there are enough data points for it)
    var x1 = xLabels[0];
    var y1 = leastSquaresCoeff[0] + leastSquaresCoeff[1];

    var x2 = xLabels[xLabels.length - 1];
    var y2 = leastSquaresCoeff[0] * xSeries.length + leastSquaresCoeff[1];

    var trendData = [[x1,y1,x2,y2]];
    var trendline = svg.selectAll(".trendline").data(trendData);

    trendline.enter()
      .append("line")
      .attr("class", "trendline")
      .attr("x1", function (d) { return xScale(d[0]); })
      .attr("y1", function (d) { return yScale(d[1]); })
      .attr("x2", function (d) { return xScale(d[2]); })
      .attr("y2", function (d) { return yScale(d[3]); })
      .attr("stroke", "#999")
      .attr("stroke-width", 2);
  }


  var circles = svg.selectAll("circle").data(vueContext.graphData)
  circles
    .enter().append('circle')
    .attr("cx", function (d) { return xScale (d.x); })
    .attr("cy", function (d) { return yScale (d.y); })
    .attr("r", 5) // Size of circle
    .attr("class", function (d) {
      return "hoverable position-display d3-hover-black " + d.position_class
    })
    .on("mouseover", function (d, i) {
      div.style("opacity", .9);
      div.html(`<div class='tooltip-inner'>Received a ${d.y} as a ${d.position} in R${d.x}</div>`)
          .style("left", (d3selection.event.pageX) + "px")
          .style("top", (d3selection.event.pageY - 28) + "px");
    })
    .on("mouseout", function (d, i) {
      div.style("opacity", 0);
    });
}
</script>
