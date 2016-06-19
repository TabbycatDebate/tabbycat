<template>
  <div :style="{ width: '49.5%', display: 'inline-block' }">
    <h5 class="text-center no-top-padding vertical-spacing">
      {{ title }}<br>({{ total }})
    </h5>
  </div>
</template>

<script>
var d3 = require("d3");

export default {
  props: {
    title: String,
    graphData: Array,
    radius: { type: Number, default: 60 },
    padding: { type: Number, default: 1 },
    regions: Array,
  },
  ready: function() {
    if (this.graphData !== undefined) {
      InitChart(this); // Only init if we have some info
    }
  },
  computed: {
    total: function() {
      var total = 0;
      for (var i = 0; i < this.graphData.length; i++) {
        total += this.graphData[i].count;
      }
      return total
    }
  },
  methods: {
    colorclass: function(label) {
      if (this.regions == null) {
        return "gender-display " + label.toLowerCase();
      } else {
        var regionid = this.regions.map(function(obj, index) {
            if(obj[label] == label) {
                return index;
            }
        }).filter(isFinite)
        return "region-display region-" + String(Number(regionid) + 1);
      }
    },
    nicelabel: function (label) {
      if (label == "Male") {
        return "Male identifying";
      } else if (label == "NM") {
        return "Female identifying or non-binary";
      } else if (label == "Unknown") {
        return "Unspecified";
      } else {
        return label;
      }
    },
    percentage: function(quantity) {
      return " (" + Math.round(quantity / this.total * 100) + "%)";
    }
  }
}


function InitChart(vueContext){

  // Female - Male - Other - Unknown

  var pie = d3.layout.pie()
      .value(function(d) { return d.count; })
      .sort(null);

  var arc = d3.svg.arc()
      .innerRadius(vueContext.radius - (vueContext.radius / 2))
      .outerRadius(vueContext.radius - vueContext.padding * 2);

  var svg = d3.select(vueContext.$el).insert("svg", ":first-child")
      .attr("width", (vueContext.radius * 2) + vueContext.padding + vueContext.padding)
      .attr("height", (vueContext.radius * 2) + vueContext.padding + vueContext.padding)
      .append("g")
      .attr("transform", "translate(" + (vueContext.radius + vueContext.padding) + "," + (vueContext.radius + vueContext.padding) + ")");

  var path = svg.selectAll("path")
      .data(pie(vueContext.graphData))
    .enter().append("path")
      .attr("class", function(d, i) { return "d3-hoverable " + vueContext.colorclass(vueContext.graphData[i].label); })
      .attr("d", arc)

  var tooltip = d3.select("body").append("div")
    .attr("class", "d3-tooltip tooltip")
    .style("opacity", 0);

  path.on('mouseover', function(d, i) {
    tooltip.html("<div class='tooltip-inner'>" +
      vueContext.graphData[i].count + " " +
      vueContext.percentage(vueContext.graphData[i].count) +
      "<br>" +
      vueContext.nicelabel(vueContext.graphData[i].label) +
      "</div>")
      .style("left", (d3.event.pageX) + "px")
      .style("top", (d3.event.pageY - 28) + "px")
      .style('opacity', 1)
    d3.select(this).style('opacity', 0.5);
  });

  path.on('mouseout', function(d) {
    tooltip.style('opacity', 0)
    d3.select(this).style('opacity', 1);
  });
}
</script>
