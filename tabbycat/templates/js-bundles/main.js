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
import TablesContainer from '../js-vue/tables/TablesContainer.vue'

if (typeof tablesData !== 'undefined' && tablesData !== null) {
  // All vue data table views must provide this base tablesData in the template
  // If its setup we mount the main vue instance
  new Vue({
    el: 'body',
    components: {
      TablesContainer
    },
    data: {
      tablesData: tablesData // Import from global setting on base-vue-table
    }
  });
}
