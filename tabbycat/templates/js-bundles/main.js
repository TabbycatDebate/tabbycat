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
var TablesContainer = require('../js-vue/tables/TablesContainer.vue')

if (typeof tablesData !== 'undefined') {
  var tables = tablesData;
} else {
  var tables = null;
}

// Mount the main vue instance
new Vue({
  el: 'body',
  components: {
    TablesContainer
  },
  data: {
    tablesData: tables // Import from global setting on base-vue-table
  }
});
