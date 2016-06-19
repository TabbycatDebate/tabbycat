// Libraries
var Vue = require('vue')

// Components
import TextDisplay from '../js-vue/graphs/TextDisplay.vue'
import DonutChart from  '../js-vue/graphs/DonutChart.vue'

if (typeof graphsData !== 'undefined') {
  new Vue({
    el: 'body',
    components: {
      TextDisplay, DonutChart
    },
    data: {
      dataSets: graphsData // Set in the template
    }
  });
}