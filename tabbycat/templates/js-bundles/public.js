// Vue and the main app
var Vue = require('vue');
import vueBases from './main.js';

// Redefine so they can be edited
var vueComponents = vueBases.baseComponents;
var vueData = vueBases.baseData;

//------------------------------------------------------------------------------
// Main Vue Instance
//------------------------------------------------------------------------------

if (typeof bypassMainVue === 'undefined') {
  new Vue({
    el: 'body',
    components: vueComponents,
    data: vueData
  });
}