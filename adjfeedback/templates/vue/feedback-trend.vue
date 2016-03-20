<!-- Adjudicator's Mini Feedback Graph -->
<script type="text/x-template" id="feedback-trend">

  <svg id="[[ elementID ]]" width="100" height="50"></svg>

</script>

<script>
  Vue.component('feedback-trend', {
    template: '#feedback-trend',
    props: ['data', 'id'],
    computed: {
      elementID: function () {
        return "feedbackTrendForAdj" + String(this.id)
      }
    },
    ready: function() {
      var vueData = this.data;
      var graphElement = "#" + this.elementID;

      InitChart();
      function InitChart(){
        var vis = d3.select(graphElement);

        // Range is the pixel coordinates; domain is the axes range
        var xRange = d3.scale.linear()
          .range([40, 400])
          .domain([0, vueData.roundSeq])
        var yRange = d3.scale.linear()
          .range([400, 40])
          .domain([vueData.minScore, vueData.maxScore])

        // Scale axis to fit the range specified
        var xAxis = d3.svg.axis()
          .scale(xRange)
          .tickValues(d3.range(0, vueData.roundSeq + 1, 1)) // Set increments
          .tickFormat(d3.format("d")); // Format as integers
        var yAxis = d3.svg.axis()
          .scale(yRange).orient("left")
          .tickValues(d3.range(vueData.minScore, vueData.maxScore + 1, 1))
          .tickFormat(d3.format("d"));

        vis.append("svg:g").call(xAxis).attr("transform", "translate(0,400)");
        vis.append("svg:g").call(yAxis).attr("transform", "translate(40,0)");

        var circles = vis.selectAll("circle").data(vueData.graphData);
        circles
          .enter().append('circle')
          .attr("cx", function (d) { return xRange (d.x); })
          .attr("cy", function (d) { return yRange (d.y); })
          .attr("r", 10) // Size of circle
      }

    },
  })
</script>
