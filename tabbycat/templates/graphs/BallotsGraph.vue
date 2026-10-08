<script setup>
import { computed, onMounted, watch } from 'vue'
import * as d3 from 'd3'

function initChart (padding, data, total, setHeight) {
  // Based on https://bl.ocks.org/mbostock/3885211
  // var data = [{"time":"2018-01-20T18:31:05.000","confirmed":0,"none":20,"draft":5}]

  function type (d) {
    d.time = d3.isoParse(d.unix_time) // date is ISO
    d.none = +d.none
    d.draft = +d.draft
    d.confirmed = +d.confirmed
    return d
  }

  if (data.length <= 1) { return } // Need at least two data points for time series
  const d3DataSet = data.map(type)
  d3.selectAll('#statusGraph > *').remove() // Remove prior graph

  const stackKey = ['none', 'draft', 'confirmed']
  const colors = {
    none: '#d1185e',
    draft: '#17a2b8',
    confirmed: '#00bf8a',
  }

  const chartDiv = document.getElementById('statusGraph')
  const margin = {
    top: padding - 15, right: padding, bottom: padding, left: padding,
  }
  const width = chartDiv.clientWidth - margin.left - margin.right
  const height = setHeight - margin.top - margin.bottom

  const svg = d3.select('#statusGraph')
    .append('svg')
    .attr('viewbox', `0 0 ${width} ${height}`)
    .attr('height', '100%')
    .attr('width', '100%')

  const x = d3.scaleTime().range([0, width])
  const y = d3.scaleLinear().range([height, 0])
  const z = d3.scaleOrdinal(colors)

  const stack = d3.stack()
    .keys(stackKey)
    .order(d3.stackOrderNone)
    .offset(d3.stackOffsetNone)

  x.domain(d3.extent(d3DataSet, d => d.time))
  y.domain([0, total])
  // The graph starts when the first ballot is submitted
  z.domain(stackKey)

  const area = d3.area()
    .x(d => x(d.data.time))
    .y0(d => y(d[0]))
    .y1(d => y(d[1]))

  const g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  const layer = g.selectAll('.layer')
    .data(stack(d3DataSet))
    .enter().append('g')
    .attr('class', 'layer')

  layer.append('path')
    .attr('class', 'area')
    .style('fill', d => colors[d.key])
    .attr('d', area)

  g.append('g')
    .attr('class', 'axis axis--x')
    .attr('transform', `translate(0,${height})`)
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%H:%M')))

  const yAxisTicks = y.ticks().filter(tick => Number.isInteger(tick))
  g.append('g')
    .attr('class', 'axis axis--y')
    .call(d3.axisLeft(y).tickValues(yAxisTicks).tickFormat(d3.format('d')))

  g.append('g')
    .attr('class', 'axis axis--y')
    .attr('transform', `translate(${width} ,0)`)
    .call(d3.axisRight(y).tickValues(yAxisTicks).tickFormat(d3.format('d')))
}

const props = defineProps({
  height: { type: Number, default: 350 },
  padding: { type: Number, default: 35 },
  graphData: { type: Array, default: function () { return [] } },
  totalDebates: Number,
})

const addSeries = (confirmed, draft, time) => {
  return {
    confirmed: confirmed,
    draft: draft,
    none: props.totalDebates - confirmed - draft,
    unix_time: time,
  }
}

const ballots = computed(() => {
  const filteredBallots = []

  const graphData = Array.isArray(props.graphData) ? props.graphData : []
  const allBallots = graphData.map(item => item.ballot).sort((a, b) => {
    let aLatestTimeStamp = a.created_timestamp
    if (a.confirmed_timestamp !== null) {
      aLatestTimeStamp = a.confirmed_timestamp
    }
    let bLatestTimeStamp = b.created_timestamp
    if (b.confirmed_timestamp !== null) {
      bLatestTimeStamp = b.confirmed_timestamp
    }
    return aLatestTimeStamp < bLatestTimeStamp
  })

  if (allBallots.length === 0) {
    return allBallots
  }

  allBallots.filter(ballot => ballot.discarded !== true)

  allBallots.forEach((ballot) => {
    const hasMatch = filteredBallots.findIndex(testBallot =>
      testBallot.debate_id === ballot.debate_id)
    if (hasMatch !== -1) filteredBallots.splice(hasMatch, 1)

    let created = null
    if (ballot.created_timestamp !== null) {
      created = new Date(ballot.created_timestamp).getTime()
    }
    let confirmed = null
    if (ballot.confirmed_timestamp !== null) {
      confirmed = new Date(ballot.confirmed_timestamp).getTime()
    }

    filteredBallots.push({
      created_timestamp: created,
      confirmed_timestamp: confirmed,
      debate_id: ballot.debate_id,
    })
  })
  return filteredBallots
})

const earliestBallotTime = computed(() => {
  if (ballots.value.length === 0) {
    return null
  }
  return ballots.value[0].created_timestamp
})

const lastBallotTime = computed(() => {
  if (ballots.value.length === 0) {
    return null
  }
  const latestBallot = ballots.value[ballots.value.length - 1]
  if (latestBallot.confirmed_timestamp === null) {
    return latestBallot.created_timestamp
  }
  return latestBallot.confirmed_timestamp
})

const timePadding = computed(() => {
  const defaultTime = 1000 * 60
  if (earliestBallotTime.value && lastBallotTime.value) {
    return Math.max(
      Math.abs((lastBallotTime.value - earliestBallotTime.value) * 0.02),
      defaultTime,
    )
  }
  return defaultTime
})

const uniqueTimes = computed(() => {
  const createdTimes = ballots.value.map(item => item.created_timestamp)
  const confirmedTimes = ballots.value.map(item => item.confirmed_timestamp)
  const uniqueTimes = [...new Set([...createdTimes, ...confirmedTimes])]
  const uniqueFilteredTimes = uniqueTimes.filter(obj => obj).sort()
  return uniqueFilteredTimes
})

const ballotStream = computed(() => {
  const ballotsSeries = []
  if (ballots.value.length === 0) {
    return ballotsSeries
  }

  for (let i = 0; i < uniqueTimes.value.length; i += 1) {
    const periodStart = uniqueTimes.value[i]
    let periodEnd
    if (i === uniqueTimes.value.length - 1) {
      periodEnd = periodStart + timePadding.value
    } else {
      periodEnd = uniqueTimes.value[i + 1]
    }

    const draftByThen = ballots.value.reduce((count, ballot) => {
      if (ballot.created_timestamp < periodEnd) {
        if (ballot.confirmed_timestamp === null) {
          return count + 1
        }
        if (ballot.confirmed_timestamp + 1 > periodEnd) {
          return count + 1
        }
      }
      return count
    }, 0)
    const confirmedByThen = ballots.value.reduce((count, ballot) => {
      if (ballot.confirmed_timestamp <= periodStart &&
          ballot.confirmed_timestamp !== null) {
        return count + 1
      }
      return count
    }, 0)

    ballotsSeries.push(addSeries(confirmedByThen, draftByThen, periodStart))
    ballotsSeries.push(addSeries(confirmedByThen, draftByThen, periodEnd))
  }

  ballotsSeries.splice(0, 0, addSeries(
    0, 0,
    ballotsSeries[0].unix_time,
  ))
  ballotsSeries.splice(0, 0, addSeries(
    0, 0,
    ballotsSeries[0].unix_time - timePadding.value,
  ))

  return ballotsSeries
})

const graphHeight = computed(() => {
  if (ballotStream.value.length > 1) {
    return `${props.height}px`
  }
  return 0
})

const render = () => {
  initChart(props.padding, ballotStream.value, props.totalDebates, props.height)
}

onMounted(() => {
  render()
})

watch(ballotStream, () => {
  render()
})
</script>

<template id="ballots-graph">
  <div>
    <div
      v-if="ballotStream.length === 0"
      class="text-center py-1"
    >
      No ballots in for this round yet
    </div>
    <div
      id="statusGraph"
      class="d3-graph"
      :style="{ height: graphHeight }"
    />
  </div>
</template>
