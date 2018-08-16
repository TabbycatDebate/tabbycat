import Vue from 'vue'
import Raven from 'raven-js'
import RavenVue from 'raven-js/plugins/vue'
import vueBases from './main'

import EditAdjudicatorsContainer from '../../adjallocation/templates/EditAdjudicatorsContainer.vue'
import TournamentOverviewContainer from '../../tournaments/templates/TournamentOverviewContainer.vue'
import PrintableBallot from '../../printing/templates/PrintableBallot.vue'
import CheckboxTablesContainer from '../tables/CheckboxTablesContainer.vue'
import AllocateDivisionsContainer from '../../divisions/templates/AllocateDivisionsContainer.vue'
import EditMatchupsContainer from '../../draw/templates/EditMatchupsContainer.vue'
import EditVenuesContainer from '../../venues/templates/EditVenuesContainer.vue'
import CheckInScanContainer from '../../checkins/templates/CheckInScanContainer.vue'


// Vue and the main app
var VueTouch = require('vue-touch')

// Redefine variables from import so that they can be edited
var vueComponents = vueBases.baseComponents
var vueData = vueBases.baseData

// This is an coordinating instance used for inter-component pub/sub interfaces
var eventHub = new Vue()
Vue.prototype.$eventHub = eventHub

// Setup error logging (should happen before other imports)
if (window.buildData.sentry === true) {
  Raven.config('https://88a028d7eb504d93a1e4c92e077d6ce5@sentry.io/185378', {
    release: window.buildData.version,
  }).addPlugin(RavenVue, Vue).install()
}

// Make a global mixin to provide translation functions
Vue.mixin(vueBases.vueTranslationMixin)
// Provide support for tab events
Vue.use(VueTouch, { name: 'v-touch' })

//------------------------------------------------------------------------------
// Tournament Homepage
//------------------------------------------------------------------------------

vueComponents.TournamentOverviewContainer = TournamentOverviewContainer

//------------------------------------------------------------------------------
// Printables
//------------------------------------------------------------------------------

vueComponents.PrintableBallot = PrintableBallot

//------------------------------------------------------------------------------
// Other
//------------------------------------------------------------------------------

vueComponents.CheckboxTablesContainer = CheckboxTablesContainer

//------------------------------------------------------------------------------
// Check-Ins
//------------------------------------------------------------------------------

vueComponents.CheckInScanContainer = CheckInScanContainer

//------------------------------------------------------------------------------
// Draw Containers
//------------------------------------------------------------------------------

vueComponents.AllocateDivisionsContainer = AllocateDivisionsContainer
vueComponents.EditMatchupsContainer = EditMatchupsContainer
vueComponents.EditVenuesContainer = EditVenuesContainer
vueComponents.EditAdjudicatorsContainer = EditAdjudicatorsContainer

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
