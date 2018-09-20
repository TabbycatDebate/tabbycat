<template>

  <td class="unpadded-cell">
    <div class="d3-graph d3-feedback-trend"></div>
  </td>

</template>

<script>
import * as d3 from 'd3'

// returns slope, intercept and r-square of the line
function leastSquares (xSeries, ySeries) {
  const reduceSumFunc = function (prev, cur) { return prev + cur }

  const xBar = (xSeries.reduce(reduceSumFunc) * 1.0) / xSeries.length
  const yBar = (ySeries.reduce(reduceSumFunc) * 1.0) / ySeries.length

  const ssXX = xSeries.map(d => (d - xBar) ** 2).reduce(reduceSumFunc)
  const ssYY = ySeries.map(d => (d - yBar) ** 2).reduce(reduceSumFunc)
  const ssXY = xSeries.map((d, i) => (d - xBar) * (ySeries[i] - yBar)).reduce(reduceSumFunc)

  const slope = ssXY / ssXX
  const intercept = yBar - (xBar * slope)
  const rSquare = (ssXY ** 2) / (ssXX * ssYY)

  return [slope, intercept, rSquare]
}

function initChart (vueContext) {
  // Range is the pixel coordinates; domain is the axes range
  const xScale = d3.scaleLinear()
    .range([0, vueContext.width])
    .domain([0, vueContext.cellData.roundSeq])

  const yScale = d3.scaleLinear()
    .range([vueContext.height, 0])
    .domain([vueContext.cellData.minScore, vueContext.cellData.maxScore])

  // Scale axis to fit the range specified
  const xAxis = d3.axisBottom(xScale)
    .tickSizeInner(-vueContext.height)
    .tickSizeOuter(0)
    .tickFormat('') // Hide ticks
    .tickValues(d3.range(0, vueContext.cellData.roundSeq + 0.5, 1)) // Set tick increments

  const yAxis = d3.axisLeft(yScale)
    .tickSizeInner(-vueContext.width)
    .tickSizeOuter(0)
    .tickPadding(10)
    .tickFormat('') // Hide ticks
    // Set tick increments
    .tickValues(d3.range(vueContext.cellData.minScore, vueContext.cellData.maxScore + 0.5, 1))

  // Define the div for the tooltip
  const div = d3.select('body').append('div')
    .attr('class', 'd3-tooltip tooltip')
    .style('opacity', 0)

  const element = $(vueContext.$el).children('.d3-graph')[0]
  const svg = d3.select(element).insert('svg', ':first-child')
    .attr('width', vueContext.width + vueContext.padding + vueContext.padding)
    .attr('height', vueContext.height + vueContext.padding + vueContext.padding)
    .append('g')
    .attr('transform', `translate(${vueContext.padding},${vueContext.padding})`)

  svg.append('g')
    .attr('class', 'x axis')
    .attr('transform', `translate(0,${vueContext.height})`)
    .call(xAxis)

  svg.append('g')
    .attr('class', 'y axis')
    .call(yAxis)

  // Create series for regression
  const xLabels = vueContext.graphData.map(d => d.x)
  const xSeries = d3.range(1, xLabels.length + 1)
  const ySeries = vueContext.graphData.map(d => parseFloat(d.y))
  const leastSquaresCoeff = leastSquares(xSeries, ySeries)

  if (!isNaN(leastSquaresCoeff[0]) && !isNaN(leastSquaresCoeff[1])) {
    // Apply the reults of the least squares regression (if there are enough data points for it)
    const x1 = xLabels[0]
    const y1 = leastSquaresCoeff[0] + leastSquaresCoeff[1]

    const x2 = xLabels[xLabels.length - 1]
    const y2 = (leastSquaresCoeff[0] * xSeries.length) + leastSquaresCoeff[1]

    const trendData = [[x1, y1, x2, y2]]
    const trendline = svg.selectAll('.trendline').data(trendData)

    trendline.enter()
      .append('line')
      .attr('class', 'trendline')
      .attr('x1', d => xScale(d[0]))
      .attr('y1', d => yScale(d[1]))
      .attr('x2', d => xScale(d[2]))
      .attr('y2', d => yScale(d[3]))
      .attr('stroke', '#999')
      .attr('stroke-width', 2)
  }

  const circles = svg.selectAll('circle').data(vueContext.graphData)
  circles
    .enter().append('circle')
    .attr('cx', d => xScale(d.x))
    .attr('cy', d => yScale(d.y))
    .attr('r', 5) // Size of circle
    .attr('class', d => `hoverable position-display d3-hover-black ${d.position_class}`)
    .on('mouseover', (d) => {
      div.style('opacity', 0.9)
      div.html(`<div class='tooltip-inner'>Received a ${d.y} as a ${d.position} in R${d.x}</div>`)
        .style('left', `${d3.event.pageX}px`)
        .style('top', `${d3.event.pageY - 28}px`)
    })
    .on('mouseout', () => {
      div.style('opacity', 0)
    })
}

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
    },
  },
  mounted: function () {
    if (typeof this.graphData !== 'undefined' && this.graphData.length > 0) {
      initChart(this) // Only init if we have some info
    }
  },
  watch: {
    graphData: function () {
      if (typeof this.graphData !== 'undefined' && this.graphData.length > 0) {
        // Just remove and remake it as I cbf figuring out the in place update
        const element = $(this.$el).children('.d3-graph')[0]
        $(element).children('svg').remove()
        initChart(this)
      }
    },
  },
}

</script>
