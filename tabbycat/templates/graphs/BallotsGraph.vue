<template id="ballots-graph">
  <div>

    <div v-if="ballotStream.length === 0" class="text-center py-1">
      No ballots in for this round yet
    </div>
    <div id="statusGraph" class="d3-graph" :style="{ height: graphHeight }"></div>

  </div>
</template>

<script>
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

export default {
  props: {
    height: { type: Number, default: 350 },
    padding: { type: Number, default: 35 },
    graphData: { type: Array, default: function () { return false } },
    totalDebates: Number,
  },
  mounted: function () {
    initChart(this.padding, this.ballotStream, this.totalDebates, this.height)
  },
  methods: {
    addSeries: function (confirmed, draft, time) {
      return {
        confirmed: confirmed,
        draft: draft,
        none: this.totalDebates - confirmed - draft,
        unix_time: time,
      }
    },
  },
  computed: {
    graphHeight: function () {
      // We need the statusGraph to grow once chart has been mounted
      if (this.ballotStream.length > 1) {
        return `${this.height}px`
      }
      return 0
    },
    timePadding: function () {
      // Ammount to pad the start and end of the graph by to show state
      const defaultTime = 1000 * 60
      if (this.earliestBallotTime && this.lastestBallotTime) {
        return Math.max(
          Math.abs((this.lastestBallotTime - this.earliestBallotTime) * 0.02),
          defaultTime,
        )
      }
      return defaultTime
    },
    ballots: function () {
      // All ballots (including duplicates) sortest oldest to newest
      const filteredBallots = []
      const allBallots = this.graphData.map(item => item.ballot).sort((a, b) => {
        // Need to sort by whatever timestamp is latest
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
        return allBallots // Empty state
      }

      // Remove discarded ballots
      allBallots.filter(ballot => ballot.discarded !== true)

      // Check for previous ballots; only take most recent
      allBallots.forEach((ballot) => {
        const hasMatch = filteredBallots.findIndex(testBallot =>
          testBallot.debate_id === ballot.debate_id)
        if (hasMatch !== -1) filteredBallots.splice(hasMatch, 1)

        // Need to parse the dates into unix time to get around TZ format issues
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
    },
    earliestBallotTime: function () {
      if (this.ballots.length === 0) {
        return null
      }
      return this.ballots[0].created_timestamp
    },
    lastestBallotTime: function () {
      if (this.ballots.length === 0) {
        return null
      }
      const latestBallot = this.ballots[this.ballots.length - 1]
      if (latestBallot.confirmed_timestamp === null) {
        return latestBallot.created_timestamp
      }
      return latestBallot.confirmed_timestamp
    },
    uniqueTimes: function () {
      const createdTimes = this.ballots.map(item => item.created_timestamp)
      const confirmedTimes = this.ballots.map(item => item.confirmed_timestamp)
      const uniqueTimes = [...new Set([...createdTimes, ...confirmedTimes])]
      // Remove null and sort by time
      const uniqueFilteredTimes = uniqueTimes.filter(obj => obj).sort()
      return uniqueFilteredTimes
    },
    ballotStream: function () {
      // Formats ballots into a time series based on status
      // Note this time series has essentially a duplicative structure, in that
      // there are two items with the same status in the array; one with the
      // start of that time period and one with the end

      const ballotsSeries = []
      if (this.ballots.length === 0) {
        return ballotsSeries
      }

      for (let i = 0; i < this.uniqueTimes.length; i += 1) {
        const periodStart = this.uniqueTimes[i]
        let periodEnd
        if (i === this.uniqueTimes.length - 1) {
          periodEnd = periodStart + this.timePadding
        } else {
          periodEnd = this.uniqueTimes[i + 1]
        }

        // Calculate ballot status backwards
        const draftByThen = this.ballots.reduce((count, ballot) => {
          // If the created timestamp exists in it is AFTER the start of this time period
          if (ballot.created_timestamp < periodEnd) {
            // If the ballot is yet to be confirmed
            if (ballot.confirmed_timestamp === null) {
              return count + 1
            }
            // If the confirmed timestamp is yet to be confirmed
            if (ballot.confirmed_timestamp + 1 > periodEnd) {
              return count + 1
            }
          }
          return count
        }, 0)
        const confirmedByThen = this.ballots.reduce((count, ballot) => {
          // If the confirming timestamp exists in it is AFTER the start of this time period
          if (ballot.confirmed_timestamp <= periodStart &&
              ballot.confirmed_timestamp !== null) {
            return count + 1
          }
          return count
        }, 0)
        // First measure
        ballotsSeries.push(this.addSeries(confirmedByThen, draftByThen, periodStart))
        // Second measure
        ballotsSeries.push(this.addSeries(confirmedByThen, draftByThen, periodEnd))
      }

      // Add extra initial row so there is always the null state shown
      ballotsSeries.splice(0, 0, this.addSeries(
        0, 0,
        ballotsSeries[0].unix_time,
      ))
      ballotsSeries.splice(0, 0, this.addSeries(
        0, 0,
        ballotsSeries[0].unix_time - this.timePadding,
      ))

      return ballotsSeries
    },
  },
  watch: {
    ballotStream: function () {
      initChart(this.padding, this.ballotStream, this.totalDebates, this.height)
    },
  },
}

</script>
