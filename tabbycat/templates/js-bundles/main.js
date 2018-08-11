// The base template with universal or near-universal functionality (imported on all pages)

//------------------------------------------------------------------------------
// TCI: jQuery, Lodash, and Boostrap
//------------------------------------------------------------------------------

var $ = require('jquery')
global.jQuery = $ // Set for bootstrap
window.$ = $ // Set for browser window

// Hover over options Needs to come before bootstrap
import Popper from 'popper.js'
window.Popper = Popper

// Import bootstrap javascript plugins
require('bootstrap')

// Icons
import feather from 'feather-icons'

// Add alerts programmatically
$.fn.extend({
  showAlert: function (alerttype, message, timeout) {
    $('#messages-container').prepend('<div id="alertdiv" class="alert alert-' + alerttype + ' fade show"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span>' + message + '</div>');
    if (timeout && timeout !== 0) {
      setTimeout(function () { // this will automatically close the alert and remove this if the users doesnt close it in 5 secs
        $('#alertdiv').alert('close')
      }, timeout);
    }
  },
  loadButton: function (button, triggeredForm) {
    // Can't use disable attr as some submission button need to pass their value
    $('button').prop('disabled', true);
  },
  resetButton: function (button) {
    $('button').prop('disabled', false);
  },
});

//------------------------------------------------------------------------------
// TCI: Mount global jquery stuff here
//------------------------------------------------------------------------------

$(document).ready(function (){

  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    'html': true
  });

  // Feather shim for icons
  feather.replace();

  // Remove the pre-expanded sidebar states for mobile (they overlap)
  if ($(window).width() < 768) {
    $("#sidebar .collapse").removeClass("show");
  }

  // Auto disable submit buttons for forms upon submission (prevent double-sub)
  $('form').submit(function(event) {
    var triggeredForm = this;
    var triggeredButton = $("[type=submit]:focus")[0]; // CLicked button

    if ($(triggeredButton).prop('disabled') === undefined ||
        $(triggeredButton).prop('disabled') === false) {
      //event.preventDefault(); // Prevent form submission until new field added
      var submitValue = $(triggeredButton).attr('value');
      var submitName = $(triggeredButton).attr('name');
      // Add new dummy field with the button's values
      // (so they pass through despite disabled state)
      if (submitValue !== undefined || submitName !== undefined) {
        $('<input />')
          .attr('type', 'hidden')
          .attr('name', submitName)
          .attr('value', submitValue)
          .appendTo(triggeredForm);
      }
      $.fn.loadButton(triggeredButton, triggeredForm);
    }
  });

  // Auto disable submit buttons for buttons that POST
  $('.submit-disable').click(function(event){
    $.fn.loadButton(event.target);
  });

  // Focus '/' on table search
  if ($("#table-search").length) {
    $(document).keypress(function (e) {
      if ((e.which == 47 || e.key == "/") && !$("#table-search").is(":focus")) {
        $("#table-search").focus()
        e.preventDefault() // Stop the keystroke
      }
    })
  }

  // IE 11 has no endsWith(); do a quick polyfill if that is the case
  // https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/String/endsWith
  if (!String.prototype.endsWith) {
    String.prototype.endsWith = function(search, this_len) {
      if (this_len === undefined || this_len > this.length) {
        this_len = this.length;
      }
      return this.substring(this_len - search.length, this_len) === search;
    };
  }

  // Set Highlights on Navigation Elements
  var currentUrl = window.location.href;
  if ($('.admin-sidebar').length) {
    // For admin area
    $('.admin-sidebar a.list-group-item').filter(function (index, elem) {
      return currentUrl.endsWith($(elem).attr('href'))
    }).addClass('active')
    // Expand sidebar if an item within a section is active (if not on mobile)
    let isMobile = window.matchMedia("only screen and (max-width: 576px)");
    if (!isMobile.matches) {
      const menuSectionClass = '.list-group-item.d-inline-block:not(.main-menu-item)';
      const listGroups = $(menuSectionClass).filter(function(index, elem) {
        return $(elem).find('a.list-group-item.active').length
      })
      listGroups.children('a').attr('aria-expanded', 'true')
      listGroups.children('div').addClass('show')
    }
  } else {
    // For assistant and public navs
    $('#collapsed-main-nav a').filter(function (index, elem) {
      if (currentUrl.endsWith($(elem).attr('href'))) {
        $(this).addClass('active')
        const parentMenuItem = $(this).parent().parent()
        if (parentMenuItem.hasClass('dropdown')) {
          $(parentMenuItem, '> .nav-link').addClass('active')
        }
      }
    })
  }

});

//------------------------------------------------------------------------------
// TCI: Vue Structure Setup
//------------------------------------------------------------------------------

// Setup the main constructs used for custom components
var vueComponents = {}

// This is the main data package setout in the django template
var vueData = window.vueData // We need to mount props from the window itself

// Vue Shared Components Setup

// Table-based Views
import TablesContainer from '../tables/TablesContainer.vue'
vueComponents['TablesContainer'] = TablesContainer

// Diversity Standings
import DiversityContainer from  '../../participants/templates/DiversityContainer.vue'
vueComponents['DiversityContainer'] = DiversityContainer

// Checkin Statuses
import CheckInStatusContainer from '../../checkins/templates/CheckInStatusContainer.vue'
vueComponents['CheckInStatusContainer'] = CheckInStatusContainer

// Vue Transations Setup

// Mixin that maps methods in Vue to what django's equivalents; passing args
var vueTranslationMixin = {
  methods: {
    gettext: function() {
      return window.gettext.apply(this, arguments)
    },
    ngettext: function() {
      return window.ngettext.apply(this, arguments)
    },
    interpolate: function() {
      return window.interpolate.apply(this, arguments)
    },
    get_format: function() {
      return window.get_format.apply(this, arguments)
    },
    gettext_noop: function() {
      return window.gettext_noop.apply(this, arguments)
    },
    pgettext: function() {
      return window.pgettext.apply(this, arguments)
    },
    npgettext: function() {
      return window.npgettext.apply(this, arguments)
    },
    pluralidx: function() {
      return window.pluralidx.apply(this, arguments)
    }
  }
}

// Expose data for admin/public.js to import
// For admin modules
export default {
  baseComponents: vueComponents,
  baseData: vueData,
  vueTranslationMixin: vueTranslationMixin
}
