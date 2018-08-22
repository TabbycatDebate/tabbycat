// The base template with universal or near-universal functionality (imported on all pages)
import Vue from 'vue'
import VueTouch from 'vue-touch'
import Raven from 'raven-js'
import RavenVue from 'raven-js/plugins/vue'
import Popper from 'popper.js'
import feather from 'feather-icons'
import 'bootstrap' // Import bootstrap javascript plugins

import AllocateDivisionsContainer from '../../divisions/templates/AllocateDivisionsContainer.vue'
import CheckInStatusContainer from '../../checkins/templates/CheckInStatusContainer.vue'
import CheckboxTablesContainer from '../tables/CheckboxTablesContainer.vue'
import DiversityContainer from '../../participants/templates/DiversityContainer.vue'
import EditAdjudicatorsContainer from '../../adjallocation/templates/EditAdjudicatorsContainer.vue'
import EditVenuesContainer from '../../venues/templates/EditVenuesContainer.vue'
import EditMatchupsContainer from '../../draw/templates/EditMatchupsContainer.vue'
import PrintableBallot from '../../printing/templates/PrintableBallot.vue'
import TablesContainer from '../tables/TablesContainer.vue'
import TournamentOverviewContainer from '../../tournaments/templates/TournamentOverviewContainer.vue'

// Setup the main constructs used for custom components
var vueComponents = {}

// Setup jquery access
var $ = require('jquery')

// Setup error logging (should happen before other imports)
if (window.buildData.sentry === true) {
  Raven.config('https://88a028d7eb504d93a1e4c92e077d6ce5@sentry.io/185378', {
    release: window.buildData.version,
  }).addPlugin(RavenVue, Vue).install()
}

//------------------------------------------------------------------------------
// TCI: jQuery, Lodash, and Boostrap
//------------------------------------------------------------------------------

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

  // IE 11 has no endsWith(); do a quick polyfill if that is the case
  // https://developer.mozilla.org/en/docs/Web/JavaScript/Reference/Global_Objects/String/endsWith
  if (!String.prototype.endsWith) {
    // eslint-disable-next-line no-extend-native
    String.prototype.endsWith = function (search, thisLength) {
      if (thisLength === undefined || thisLength > this.length) {
        // eslint-disable-next-line no-param-reassign
        thisLength = this.length;
      }
      return this.substring(thisLength - search.length, thisLength) === search;
    };
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
// Vue General Components Setup
//------------------------------------------------------------------------------

// Table-based Views
vueComponents.TablesContainer = TablesContainer
vueComponents.CheckboxTablesContainer = CheckboxTablesContainer
// Checkin Statuses
vueComponents.CheckInStatusContainer = CheckInStatusContainer
// Divisions Containers
vueComponents.AllocateDivisionsContainer = AllocateDivisionsContainer
vueComponents.DiversityContainer = DiversityContainer
vueComponents.TournamentOverviewContainer = TournamentOverviewContainer
// Printables
vueComponents.PrintableBallot = PrintableBallot
// Allocations
vueComponents.EditAdjudicatorsContainer = EditAdjudicatorsContainer
vueComponents.EditMatchupsContainer = EditMatchupsContainer
vueComponents.EditVenuesContainer = EditVenuesContainer

//------------------------------------------------------------------------------
// Asynchronously Loaded Components Setup (defer loading to reduce bundle)
//------------------------------------------------------------------------------

// Note the 3d graphs are async loaded inline as part of components: {}
// Check-Ins (thus delays loading quagga)
vueComponents.CheckInScanContainer = () => import('../../checkins/templates/CheckInScanContainer.vue')

//------------------------------------------------------------------------------
// Main Vue Instance
//------------------------------------------------------------------------------

// This is the main data package setout in the django template
const vueData = window.vueData // We need to mount props from the window itself

// Vue Transations Setup
// Mixin that maps methods in Vue to what django's equivalents; passing args
const vueTranslationMixin = {
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

// This is an coordinating instance used for inter-component pub/sub interfaces
const eventHub = new Vue()
Vue.prototype.$eventHub = eventHub

// Make a global mixin to provide translation functions
Vue.mixin(vueTranslationMixin)
// Provide support for tab events
Vue.use(VueTouch, { name: 'v-touch' })

// Only instantiate Vue if there is set vueData; otherwise the mount is missing
if (typeof vueData !== 'undefined') {
  // Many templates share the vueTable base but don't provide data
  if ('tablesData' in vueData && vueData.tablesData === null) {
    // Is an empty table; do not mount
  } else {
    new Vue({
      el: '#vueMount',
      components: vueComponents,
      data: vueData,
    });
  }
}
