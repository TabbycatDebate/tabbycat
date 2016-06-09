<!-- Pie Graphs for Diversity Reports -->
<script type="text/x-template" id="text-display">

  <div class="row">

    <template v-for="(index, d) in graphData">

      <div class="col-md-4 text-center">
        <h3 class="no-bottom-margin text-body gender-text [[ d.label.toLowerCase() ]]">
          [[ offset(d.count) ]]
        </h3>
      </div>

      <template v-if="datum && index == 0">
        <div class="col-md-4 text-center">
          <h3 class="no-bottom-margin text-body">
          [[ round(datum) ]]
          </h3>
        </div>
      </template>

    </template>

  </div>

  <div class="row">
   <h5 class="text-center">[[ title ]]</h5>
  </div>

</script>

<script>

  Vue.component('text-display', {
    template: '#text-display',
    props: {
      title: String,
      graphData: Array,
      datum: Number,
    },
    methods: {
      round: function(value) {
        return parseFloat(Math.round(value * 100) / 100).toFixed(2);
      },
      offset: function(value) {
        var off = this.datum - value
        if (off > 0) {
          return "+" + this.round(off)
        } else {
          return this.round(off)
        }
      }
    }
  })

</script>
