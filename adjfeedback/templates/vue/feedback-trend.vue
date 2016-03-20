<!-- Adjudicator's Mini Feedback Graph -->
<script type="text/x-template" id="feedback-trend">

  <div id="[[ elementID ]]" class="d3-graph d3-feedback-trend"></div>

</script>

<script>
  Vue.component('feedback-trend', {
    template: '#feedback-trend',
    props: {
      id: Number,
      minScore: Number,
      maxScore: Number,
      roundSeq: Number,
      graphData: Array,
      width: { type: Number, default: 200 },
      height: { type: Number, default: 50 },
      padding: { type: Number, default: 5 },
    },
    computed: {
      elementID: function () {
        return "feedbackTrendForAdj" + String(this.id)
      },
    },
    ready: function() {
      var vueContext = this;
      if (vueContext.graphData !== undefined) {
        InitChart(); // Only init if we have some info
      }

      function InitChart(){

        // Range is the pixel coordinates; domain is the axes range
        var xScale = d3.scale.linear()
          .range([0, vueContext.width])
          .domain([0, vueContext.roundSeq])

        var yScale = d3.scale.linear()
          .range([vueContext.height, 0])
          .domain([vueContext.minScore, vueContext.maxScore])

        // Scale axis to fit the range specified
        var xAxis = d3.svg.axis()
          .scale(xScale)
          .orient("bottom")
          .innerTickSize(-vueContext.height)
          .outerTickSize(0)
          .tickFormat(function (d) { return ''; }) // Hide ticks
          .tickValues(d3.range(0, vueContext.roundSeq + 0.5, 1)) // Set tick increments

        var yAxis = d3.svg.axis()
          .scale(yScale)
          .orient("left")
          .innerTickSize(-vueContext.width)
          .outerTickSize(0)
          .tickPadding(10)
          .tickFormat(function (d) { return ''; }) // Hide ticks
          .tickValues(d3.range(vueContext.minScore, vueContext.maxScore + 0.5, 1))  // Set tick increments

        // Define the div for the tooltip
        var div = d3.select("body").append("div")
          .attr("class", "d3-tooltip tooltip")
          .style("opacity", 0);

        var svg = d3.select("#" + vueContext.elementID).append("svg")
            .attr("width", vueContext.width + vueContext.padding + vueContext.padding)
            .attr("height", vueContext.height + vueContext.padding + vueContext.padding)
          .append("g")
            .attr("transform", "translate(" + vueContext.padding + "," + vueContext.padding + ")");

        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + vueContext.height + ")")
            .call(xAxis)

        svg.append("g")
            .attr("class", "y axis")
            .call(yAxis)

        var circles = svg.selectAll("circle").data(vueContext.graphData)

        circles
          .enter().append('circle')
          .attr("cx", function (d) { return xScale (d.x); })
          .attr("cy", function (d) { return yScale (d.y); })
          .attr("r", 5) // Size of circle
          .attr("class", "d3-hoverable")
          .attr("fill", function (d) {
            if (d.position === "Chair") {
              return 'green';
            } else if (d.position === "Panellist") {
              return 'orange';
            } else if (d.position === "Trainee") {
              return 'red';
            } else {
              return 'grey'; // Test
            }
            return yScale (d.position);
          })
          .on("mouseover", function(d) {
            div.transition()
                .duration(200)
                .style("opacity", .9);
            div.html("<div class='tooltip-inner'>Received a " + d.y + " as a " + d.position + " in R" + d.x + "</div>")
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
          })
          .on("mouseout", function(d) {
            div.transition()
              .duration(500)
              .style("opacity", 0);
          });
      }
    },
  })
</script>
