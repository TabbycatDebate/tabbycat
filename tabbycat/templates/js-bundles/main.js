// The base template with universal or near-universal functionality (imported on all pages)

//------------------------------------------------------------------------------
// jQuery, Lodash, and Boostrap
//------------------------------------------------------------------------------

var $ = require("jquery");
global.jQuery = $; // Set for bootstrap
window.$ = $; // Set for browser window

require("bootstrap"); // Need to call boostrap functions from within Vue etc

// Mount global jquery stuff here
$(document).ready(function(){
  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    'html': true
  });
  // Disable buttons post submission
  $('.submit-disable').on('click', function () {
    var $btn = $(this).button('loading');
  });
  // Make larger click targets for checkboxes in tables
  $('.checkbox-target').on('click', function (e) {
    if (e.target === this) { // Don't trigger when clicking the input itself
      var checkBox = $("input[type=checkbox]", this).first();
      checkBox.prop("checked", !checkBox.prop("checked"));
      checkBox.trigger("change");
    }
  });
});

// Add alerts programmatically
$.fn.extend({
  showAlert: function(alerttype, message, timeout) {
    $('#messages-container').append('<div id="alertdiv" class="alert alert-' + alerttype + ' fade in"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span>' + message + '</span></div>');
    if (timeout && timeout !== 0) {
      setTimeout(function() { // this will automatically close the alert and remove this if the users doesnt close it in 5 secs
        $("#alertdiv").alert('close');
      }, timeout);
    }
  }
});

//------------------------------------------------------------------------------
// Vue Structure Setup
//------------------------------------------------------------------------------

// Setup the main constructs used for custom components
var vueComponents = {}

// This is the main data package setout in the django template
var vueData = window.vueData // We need to mount props from the window itself

//------------------------------------------------------------------------------
// Vue Shared Components Setup
//------------------------------------------------------------------------------

// Table-based Views
import TablesContainer from '../js-vue/containers/TablesContainer.vue'
vueComponents['TablesContainer'] = TablesContainer

// Graph-based Views
import TextDisplay from '../js-vue/graphs/TextDisplay.vue'
vueComponents['TextDisplay'] = TextDisplay

import DonutChart from  '../js-vue/graphs/DonutChart.vue'
vueComponents['DonutChart'] = DonutChart

//------------------------------------------------------------------------------
// Expose data for admin/public.js to import
//------------------------------------------------------------------------------

// For admin modules
export default {
  baseComponents: vueComponents,
  baseData: vueData,
}
