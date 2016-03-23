
<!-- Streaming Item Updates for TournamentOverview -->
<script type="text/x-template" id="ballots-graph">

  <div id="ballotsStatusGraph" class="d3-graph"></div>

</script>

<script>

  function InitChart(vueContext){

    var dataSize = vueContext.graphData.length

    var xScale = d3.scale.linear()
      .range([0, vueContext.width])
      .domain([vueContext.graphData[0].time, vueContext.graphData[dataSize - 1].time])

    var yScale = d3.scale.linear()
      .range([vueContext.height, 0])
      .domain([0, (vueContext.graphData[dataSize - 1].count + vueContext.graphData[dataSize - 2].count)])

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, vueContext.width], 10);

    var y = d3.scale.linear()
        .rangeRound([vueContext.height, 0]);

    var color = d3.scale.ordinal()
      .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);

    var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom");

    var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")

    var svg = d3.select("#ballotsStatusGraph").append("svg")
      .attr("width", vueContext.width + vueContext.padding + vueContext.padding)
      .attr("height", vueContext.height + vueContext.padding + vueContext.padding)
      .append("g")
      .attr("transform", "translate(" + vueContext.padding + "," + vueContext.padding + ")");

    var xLabels = vueContext.graphData.map(function (d) { return d.time; })
    var xSeries = d3.range(1, xLabels.length + 1);
		var ySeries = vueContext.graphData.map(function(d) { return parseFloat(d.count); });

    var circles = svg.selectAll("circle").data(vueContext.graphData)
    circles
      .enter().append('circle')
      .attr("cx", function (d) { return xScale (d.time); })
      .attr("cy", function (d) { return yScale (d.count); })
      .attr("r", 5) // Size of circle

    svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + vueContext.height + ")")
      .call(xAxis);

    svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  }

  Vue.component('ballots-graph', {
    template: '#ballots-graph',
    props: {
      pollUrl: String,
      width: { type: Number, default: 900 },
      height: { type: Number, default: 250 },
      padding: { type: Number, default: 35 },
    },
    ready: function () {
      this.fetchData(this.pollUrl, 'actions');
    },
    methods: {
      fetchData: function (apiURL, resource) {
        var xhr = new XMLHttpRequest()
        var self = this
        xhr.open('GET', apiURL)
        xhr.onload = function () {
          self.graphData = JSON.parse(xhr.responseText)
          console.log(JSON.parse(xhr.responseText))
          InitChart(self); // Only init if we have some info
        }
        xhr.send()
      }
    },
  })
</script>
