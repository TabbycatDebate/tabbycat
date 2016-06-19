<!-- Adjudicator's Mini Feedback Graph -->
<template>
  <td class="unpadded-cell">
    <div class="d3-graph d3-feedback-trend"></div>
  </td>
</template>

<script>

  var d3 = require("d3");
  export default {
    props: {
      componentData: Object,
      width: { type: Number, default: 320 },
      height: { type: Number, default: 42 },
      padding: { type: Number, default: 5 },
    },
    ready: function() {
      if (this.componentData.graphData !== undefined) {
        InitChart(this); // Only init if we have some info
      }
    },
  }

  // returns slope, intercept and r-square of the line
  function leastSquares(xSeries, ySeries) {
    var reduceSumFunc = function(prev, cur) { return prev + cur; };

    var xBar = xSeries.reduce(reduceSumFunc) * 1.0 / xSeries.length;
    var yBar = ySeries.reduce(reduceSumFunc) * 1.0 / ySeries.length;

    var ssXX = xSeries.map(function(d) { return Math.pow(d - xBar, 2); })
      .reduce(reduceSumFunc);

    var ssYY = ySeries.map(function(d) { return Math.pow(d - yBar, 2); })
      .reduce(reduceSumFunc);

    var ssXY = xSeries.map(function(d, i) { return (d - xBar) * (ySeries[i] - yBar); })
      .reduce(reduceSumFunc);

    var slope = ssXY / ssXX;
    var intercept = yBar - (xBar * slope);
    var rSquare = Math.pow(ssXY, 2) / (ssXX * ssYY);

    return [slope, intercept, rSquare];
  }

  function InitChart(vueContext){
    // Range is the pixel coordinates; domain is the axes range
    var xScale = d3.scale.linear()
      .range([0, vueContext.width])
      .domain([0, vueContext.componentData.roundSeq])

    var yScale = d3.scale.linear()
      .range([vueContext.height, 0])
      .domain([vueContext.componentData.minScore, vueContext.componentData.maxScore])

    // Scale axis to fit the range specified
    var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient("bottom")
      .innerTickSize(-vueContext.height)
      .outerTickSize(0)
      .tickFormat(function (d) { return ''; }) // Hide ticks
      .tickValues(d3.range(0, vueContext.componentData.roundSeq + 0.5, 1)) // Set tick increments

    var yAxis = d3.svg.axis()
      .scale(yScale)
      .orient("left")
      .innerTickSize(-vueContext.width)
      .outerTickSize(0)
      .tickPadding(10)
      .tickFormat(function (d) { return ''; }) // Hide ticks
      .tickValues(d3.range(vueContext.componentData.minScore, vueContext.componentData.maxScore + 0.5, 1))  // Set tick increments

    // Define the div for the tooltip
    var div = d3.select("body").append("div")
      .attr("class", "d3-tooltip tooltip")
      .style("opacity", 0);

    var element = $(vueContext.$el).children(".d3-graph")[0]
    var svg = d3.select(element).insert("svg", ":first-child")
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


    // create series for regression
    var xLabels = vueContext.componentData.graphData.map(function (d) { return d['x']; })
    var xSeries = d3.range(1, xLabels.length + 1);
		var ySeries = vueContext.componentData.graphData.map(function(d) { return parseFloat(d['y']); });
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
        .attr("x1", function(d) { return xScale(d[0]); })
        .attr("y1", function(d) { return yScale(d[1]); })
        .attr("x2", function(d) { return xScale(d[2]); })
        .attr("y2", function(d) { return yScale(d[3]); })
        .attr("stroke", "#999")
        .attr("stroke-width", 2);
    }


    var circles = svg.selectAll("circle").data(vueContext.componentData.graphData)
    circles
      .enter().append('circle')
      .attr("cx", function (d) { return xScale (d.x); })
      .attr("cy", function (d) { return yScale (d.y); })
      .attr("r", 5) // Size of circle
      .attr("class", function(d) { return "d3-hoverable position-display d3-hover-black " + d.position.toLowerCase()})
      .on("mouseover", function(d, i) {
        div.transition()
            .duration(200)
            .style("opacity", .9);
        div.html("<div class='tooltip-inner'>Received a " + d.y + " as a " + d.position + " in R" + d.x + "</div>")
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
      })
      .on("mouseout", function(d, i) {
        div.transition()
          .duration(500)
          .style("opacity", 0);
      });
  }
</script>