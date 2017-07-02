// Vue and the main app
var Vue = require('vue');
import vueBases from './main.js';

// Setup error logging (should happen before other imports)
import Raven from 'raven-js';
import RavenVue from 'raven-js/plugins/vue';
if (window.buildData.sentry) {
  Raven.config('https://88a028d7eb504d93a1e4c92e077d6ce5@sentry.io/184984', {
    release: window.buildData.version
  }).addPlugin(RavenVue, Vue).install();
}

// Redefine variables from import so that they can be edited
var vueComponents = vueBases.baseComponents
var vueData = vueBases.baseData

// This is an coordinating instance used for inter-component pub/sub interfaces
var eventHub = new Vue()
Vue.prototype.$eventHub = eventHub

//------------------------------------------------------------------------------
// Tournament Homepage
//------------------------------------------------------------------------------

import TournamentOverviewContainer from  '../js-vue/containers/TournamentOverviewContainer.vue'
vueComponents['TournamentOverviewContainer'] = TournamentOverviewContainer

//------------------------------------------------------------------------------
// Printables
//------------------------------------------------------------------------------

import PrintableBallot from  '../../printing/templates/PrintableBallot.vue'
vueComponents['PrintableBallot'] = PrintableBallot

//------------------------------------------------------------------------------
// Draw Containers
//------------------------------------------------------------------------------

import AllocateDivisionsContainer from  '../../divisions/templates/AllocateDivisionsContainer.vue'
vueComponents['AllocateDivisionsContainer'] = AllocateDivisionsContainer

import EditMatchupsContainer from  '../js-vue/containers/EditMatchupsContainer.vue'
vueComponents['EditMatchupsContainer'] = EditMatchupsContainer

import EditVenuesContainer from  '../js-vue/containers/EditVenuesContainer.vue'
vueComponents['EditVenuesContainer'] = EditVenuesContainer

import EditAdjudicatorsContainer from  '../js-vue/containers/EditAdjudicatorsContainer.vue'
vueComponents['EditAdjudicatorsContainer'] = EditAdjudicatorsContainer

//------------------------------------------------------------------------------
// Main Vue Instance
//------------------------------------------------------------------------------

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
