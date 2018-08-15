// The base template with universal or near-universal functionality (imported on all pages)

import Popper from 'popper.js'
import feather from 'feather-icons'
import 'bootstrap' // Import bootstrap javascript plugins

import TablesContainer from '../tables/TablesContainer.vue'
import DiversityContainer from '../../participants/templates/DiversityContainer.vue'
import CheckInStatusContainer from '../../checkins/templates/CheckInStatusContainer.vue'

//------------------------------------------------------------------------------
// TCI: Vue Structure Setup
//------------------------------------------------------------------------------

// Setup the main constructs used for custom components
var vueComponents = {}

// This is the main data package setout in the django template
var vueData = window.vueData // We need to mount props from the window itself

// Vue Transations Setup

// Mixin that maps methods in Vue to what django's equivalents; passing args
var vueTranslationMixin = {
  methods: {
    gettext: function () {
      return window.gettext.apply(this, arguments)
    },
    ngettext: function () {
      return window.ngettext.apply(this, arguments)
    },
    interpolate: function () {
      return window.interpolate.apply(this, arguments)
    },
    get_format: function () {
      return window.get_format.apply(this, arguments)
    },
    gettext_noop: function () {
      return window.gettext_noop.apply(this, arguments)
    },
    pgettext: function () {
      return window.pgettext.apply(this, arguments)
    },
    npgettext: function () {
      return window.npgettext.apply(this, arguments)
    },
    pluralidx: function () {
      return window.pluralidx.apply(this, arguments)
    },
  },
}

//------------------------------------------------------------------------------
// TCI: jQuery, Lodash, and Boostrap
//------------------------------------------------------------------------------

var $ = require('jquery')

global.jQuery = $ // Set for bootstrap
window.$ = $ // Set for browser window

// Hover over options Needs to come before bootstrap
window.Popper = Popper

// Add alerts programmatically
$.fn.extend({
  showAlert: function (alerttype, message, timeout) {
    $('#messages-container').prepend(`
      <div id='alertdiv' class='alert alert-${alerttype} fade show'>
        <button type='button' class='close' data-dismiss='alert' aria-label='Close'>
        <span aria-hidden='true'>&times;</span></button>${message}
      </div>`);
    if (timeout && timeout !== 0) {
      // this will automatically close the alert and remove this if the users don't within in 5s
      setTimeout(() => {
        $('#alertdiv').alert('close')
      }, timeout);
    }
  },
  loadButton: function () {
    // Can't use disable attr as some submission button need to pass their value
    $('button').prop('disabled', true);
  },
  resetButton: function () {
    $('button').prop('disabled', false);
  },
});

//------------------------------------------------------------------------------
// TCI: Mount global jquery stuff here
//------------------------------------------------------------------------------

function disabledTriggeredForm(triggeredForm) {
  var triggeredButton = $('[type=submit]:focus')[0]; // CLicked button
  var submitValue = $(triggeredButton).attr('value');
  var submitName = $(triggeredButton).attr('name');

  if ($(triggeredButton).prop('disabled') === undefined ||
      $(triggeredButton).prop('disabled') === false) {
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
}

$(document).ready(() => {
  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    html: true,
  });

  // Feather shim for icons
  feather.replace();

  // Remove the pre-expanded sidebar states for mobile (they overlap)
  if ($(window).width() < 768) {
    $('#sidebar .collapse').removeClass('show');
  }

  // Auto disable submit buttons for forms upon submission (prevent double-sub)
  $('form').submit(function () {
    disabledTriggeredForm(this)
  });

  // Auto disable submit buttons for buttons that POST
  $('.submit-disable').click((event) => {
    $.fn.loadButton(event.target);
  });

  // Focus '/' on table search
  if ($('#table-search').length) {
    $(document).keypress((e) => {
      if ((e.which === 47 || e.key === '/') && !$('#table-search').is(':focus')) {
        $('#table-search').focus()
        e.preventDefault() // Stop the keystroke
      }
    })
  }

  // Set Highlights on Navigation Elements
  const currentUrl = window.location.href;
  if ($('.admin-sidebar').length) {
    // For admin area
    $('.admin-sidebar a.list-group-item').filter((index, elem) =>
      currentUrl.endsWith($(elem).attr('href'))).addClass('active')
    // Expand sidebar if an item within a section is active (if not on mobile)
    const isMobile = window.matchMedia('only screen and (max-width: 576px)');
    if (!isMobile.matches) {
      const menuSectionClass = '.list-group-item.d-inline-block:not(.main-menu-item)';
      const listGroups = $(menuSectionClass).filter((index, elem) =>
        $(elem).find('a.list-group-item.active').length > 0)
      listGroups.children('a').attr('aria-expanded', 'true')
      listGroups.children('div').addClass('show')
    }
  } else {
    // For assistant and public navs
    $('#collapsed-main-nav a').each(function (index, elem) {
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
// Vue Shared Components Setup
//------------------------------------------------------------------------------

// Table-based Views
vueComponents.TablesContainer = TablesContainer
// Diversity Standings
vueComponents.DiversityContainer = DiversityContainer
// Checkin Statuses
vueComponents.CheckInStatusContainer = CheckInStatusContainer

// Expose data for admin/public.js to import
// For admin modules
export default {
  baseComponents: vueComponents,
  baseData: vueData,
  vueTranslationMixin: vueTranslationMixin,
}
