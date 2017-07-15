<script>
// Inheriting componets should provide a getPopOverTitle() method
// Along with providing an element with the "popover-raw" class as a direct
// descendent of the component's root template
// They can then trigger showPopover; ie "@mouseover="showPopover""
// Note that once triggered, it will handle its own show/hide events

export default {
  methods: {
    setupPopover: function(event, content) {

      // Hide all other popover elements (seems to fix issues with them lingering)
      $(".popover").hide();

      // Destroy previous popovers attached to this element; so they don't stick
      // around when a table is filtered or searched
      $(event.target).popover('destroy')

      var self = this
      // Construct new popover
      $(event.target).popover({
        animation: false,
        trigger: 'manual',
        container: 'body',
        placement: 'top',
        html: true,
        title: self.getPopOverTitle(),
        content: function() { return content }
      })

      // Show it
      $(event.target).popover('show')
        .on("mouseenter", function () {
          $(this).popover("show");
          $(".popover").on("mouseleave", function () {
            $(self).popover('hide');
          });
        })
        .on("mouseleave", function () {
          // We want to allow links inside to be clicked
          // So here (and above) we set up additional listener events so that
          // leaving the initial cell (but hovering in the bubble) doesn't
          // automatically hide the element hide
          var _this = this;
          setTimeout(function () {
            if (!$(".popover:hover").length) {
              $(_this).popover("hide");
            }
          }, 300)
        })
    },
  }
}
</script>
