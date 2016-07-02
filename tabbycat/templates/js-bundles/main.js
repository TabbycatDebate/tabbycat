// The base template with universal or near-universal functionality (imported on all pages)

//------------------------------------------------------------------------------
// jQuery and Boostrap
//------------------------------------------------------------------------------

var $ = require("jquery");
global.jQuery = $; // Set for bootstrap
window.$ = $; // Set for browser window
require("bootstrap");

// Mount global jquery stuff here
$(document).ready(function(){
  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    'html': true,
    'placement': 'top'
  });
  // Disable buttons post submission
  $('.submit-disable').on('click', function () {
    var $btn = $(this).button('loading');
  });
  // Make larger click targets for checkboxes in tables
  $('.checkbox-target').on('click', function (e) {
    if (e.target == this) { // Don't trigger when clicking the input itself
      var checkBox = $("input[type=checkbox]", this).first();
      checkBox.prop("checked", !checkBox.prop("checked"));
    }
  });
});

// Add alerts programmatically
$.fn.extend({
  showAlert: function(alerttype, message, timeout) {
    $('#messages-container').append('<div id="alertdiv" class="alert alert-' + alerttype + ' fade in"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span>' + message + '</span></div>');
    if (timeout || timeout === 0) {
      setTimeout(function() { // this will automatically close the alert and remove this if the users doesnt close it in 5 secs
        $("#alertdiv").alert('close');
      }, timeout);
    }
  }
});

//------------------------------------------------------------------------------
// Vues
//------------------------------------------------------------------------------

// Plugin mounting points for components/data
var baseComponents = {}
var baseData = {}

// Table-based Views
import TablesContainer from '../js-vue/tables/TablesContainer.vue'

if (typeof tablesData !== 'undefined' && tablesData !== null) {
  // All vue data table views must provide this base tablesData in the template
  baseComponents['TablesContainer'] = TablesContainer;
  baseData['tablesData'] = tablesData;
}

// Graph-based Views
import TextDisplay from '../js-vue/graphs/TextDisplay.vue'
import DonutChart from  '../js-vue/graphs/DonutChart.vue'

if (typeof graphsData !== 'undefined' && graphsData !== null) {
  baseComponents['TextDisplay'] = TextDisplay
  baseComponents['DonutChart'] = DonutChart
  baseData['graphsData'] = graphsData
}

// For admin modules
export default {
  baseComponents: baseComponents,
  baseData: baseData,
}