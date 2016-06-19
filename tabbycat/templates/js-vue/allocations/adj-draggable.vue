<!-- Table Template -->
<script type="text/x-template" id="adj-draggable">

  <div>

  </div>

</script>

<!-- Team Draggable Component Behaviour -->
<script>

  // Define the component
  var adjDraggable = Vue.extend({
    template: '#adj-draggable',
    // mixins: [ajaxMixin],
    // props: {
    //    componentData: Object,
    // },
    // methods: {
    // }
  })

  pluginComponents.push({
    template: 'adj-draggable',
    reference: adjDraggable
  })

</script>
