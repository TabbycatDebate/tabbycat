<script setup>
import { computed, getCurrentInstance, onMounted } from 'vue'
import * as d3 from 'd3'

function InitChart (vueContext) {
  // Female - Male - Other - Unknown

  const pie = d3.pie()
    .value(d => d.count)
    .sort(null)

  const arc = d3.arc()
    .innerRadius(vueContext.radius - (vueContext.radius / 2))
    .outerRadius(vueContext.radius - (vueContext.padding * 2))

  const svg = d3.select(vueContext.$el).insert('svg', ':first-child')
    .attr('width', (vueContext.radius * 2) + vueContext.padding + vueContext.padding)
    .attr('height', (vueContext.radius * 2) + vueContext.padding + vueContext.padding)
    .append('g')
    .attr('transform', `translate(${vueContext.radius + vueContext.padding
    },${vueContext.radius + vueContext.padding})`)

  const path = svg.selectAll('path')
    .data(pie(vueContext.graphData.reverse()))
    .enter().append('path')
    .attr('class', (d, i) => `hoverable ${vueContext.colorclass(vueContext.graphData[i].label)}`)
    .style('stroke', 'white')
    .style('stroke-width', '1')
    .attr('d', arc)

  const tooltip = d3.select('body').append('div')
    .attr('class', 'd3-tooltip tooltip')
    .style('opacity', 0)

  path.on('mouseover', function (event, d) {
    const e = path.nodes()
    const i = e.indexOf(this)
    tooltip.html(`<div class='tooltip-inner'>${
      vueContext.graphData[i].count} ${
      vueContext.percentage(vueContext.graphData[i].count)
    }<br>${
      vueContext.nicelabel(vueContext.graphData[i].label)
    }</div>`)
      .style('left', `${event.pageX}px`)
      .style('top', `${event.pageY - 28}px`)
      .style('opacity', 1)
    d3.select(this).style('opacity', 0.5)
  })

  path.on('mouseout', function () {
    tooltip.style('opacity', 0)
    d3.select(this).style('opacity', 1)
  })
}


const props = defineProps({
  title: String,
  graphData: Array,
  radius: { type: Number, default: 60 },
  padding: { type: Number, default: 1 },
  regions: Array,
})

const instance = getCurrentInstance()
const proxy = instance?.proxy

const total = computed(() => {
  const graphData = Array.isArray(props.graphData) ? props.graphData : []
  let total = 0
  for (let i = 0; i < graphData.length; i += 1) {
    total += graphData[i].count
  }
  return total
})

const colorclass = (label) => {
  if (props.regions === undefined) {
    return `gender-display gender-${label.toLowerCase()}`
  }
  return `region-display region-${label}`
}

const nicelabel = (label) => {
  if (label === 'Male') {
    return 'Male identifying'
  } else if (label === 'NM') {
    return 'Non-cis male identifying'
  } else if (label === 'Unknown') {
    return 'Unspecified or unrecorded'
  }
  return props.regions[label].name
}

const percentage = (quantity) => {
  return ` (${Math.round((quantity / total.value) * 100)}%)`
}

onMounted(() => {
  if (props.graphData !== undefined && total.value > 0 && proxy?.$el) {
    InitChart({
      $el: proxy.$el,
      radius: props.radius,
      padding: props.padding,
      graphData: props.graphData,
      colorclass,
      percentage,
      nicelabel,
    })
  }
})
</script>

<template>
  <div :style="{ width: '49.5%', display: 'inline-block' }">
    <h6
      v-if="total > 0"
      class="text-center text-muted pt-0 mb-3"
    >
      {{ title }}<br>({{ total }})
    </h6>
    <h6
      v-if="total === 0"
      class="text-center text-muted pt-1 mb-1"
    >
      no data for<br> {{ title }}
    </h6>
  </div>
</template>
