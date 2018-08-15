import Vue from 'vue'
import vueBases from './main'


// Vue and the main app
var VueTouch = require('vue-touch')

// Redefine variables from import so that they can be edited
var vueComponents = vueBases.baseComponents
var vueData = vueBases.baseData

// This is an coordinating instance used for inter-component pub/sub interfaces
var eventHub = new Vue()
Vue.prototype.$eventHub = eventHub

// Make a global mixin to provide translation functions
Vue.mixin(vueBases.vueTranslationMixin)
// Provide support for tab events
Vue.use(VueTouch, { name: 'v-touch' })

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
