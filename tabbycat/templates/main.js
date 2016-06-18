var Vue = require('vue')
var App = require('./vue/App.vue')

Vue.config.debug = true;
Vue.config.devtools = true;

// Used by table but Vue isn't defined there
Vue.filter('caseInsensitiveOrderBy', function (arr, sortIndex, reverse) {
  // This is basically a copy of Vue's native orderBy except we are overriding
  // the last part to see if the cell has custom sort attributes
  var order = (reverse && reverse < 0) ? -1 : 1;
  // sort on a copy to avoid mutating original array
  return arr.slice().sort(function (a, b) {
    // Check if cell has custom sorting
    if (a[sortIndex] && b[sortIndex] && typeof(a[sortIndex].sort) !== 'undefined') {
      a = a[sortIndex].sort;
      b = b[sortIndex].sort;
    } else if (a[sortIndex] && b[sortIndex] && typeof(a[sortIndex].text) !== 'undefined') {
      a = a[sortIndex].text;
      b = b[sortIndex].text;
    } else {
      console.log('Error sorting; sort key probably doesnt exist');
    }
    return a === b ? 0 : a > b ? order : -order;
  });
});

// Create the base vue instance
/* eslint-disable no-new */

if (typeof tablesData !== 'undefined') {
  var tables = tablesData;
} else {
  var tables = null;
}

// Mount the main vue instance
new Vue({
  el: 'body',
  components: { App },
  data: {
    tablesData: tables // Import from global setting on base-vue-table
  }
});

// Mount global jquery stuff
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