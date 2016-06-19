// The base template with universal or near-universal functionality (imported on all pages)

// jQuery and Bootstrap
window.$ = window.jQuery = require('jquery');
var bootstrapjs = require('bootstrap-sass');

// Mount global jquery stuff here
$(document).ready(function(){
  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    'html': true,
    'placement': 'bottom'
  });
  // Disable buttons post submission
  $('.submit-disable').on('click', function () {
    var $btn = $(this).button('loading');
  });
});

// Vue and the main app
var Vue = require('vue')
// Plugin mounting points for components/data
var vueComponents = {}
var vueData = {}

// Table-based Views
import TablesContainer from '../js-vue/tables/TablesContainer.vue'
if (typeof tablesData !== 'undefined' && tablesData !== null) {
  // All vue data table views must provide this base tablesData in the template
  vueComponents['TablesContainer'] = TablesContainer;
  vueData['tablesData'] = tablesData;
}

// Graph-based Views
import TextDisplay from '../js-vue/graphs/TextDisplay.vue'
import DonutChart from  '../js-vue/graphs/DonutChart.vue'
if (typeof graphsData !== 'undefined' && graphsData !== null) {
  vueComponents['TextDisplay'] = TextDisplay;
  vueComponents['DonutChart'] = DonutChart;
  vueData['graphsData'] = graphsData;
}

if (typeof bypassMainVue === 'undefined') {
  new Vue({
    el: 'body',
    components: vueComponents,
    data: vueData,
  });
}