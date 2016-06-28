<script>
// Inheriting componets should provide a getPopOverTitle() method
// Along with providing an element with the "popover-raw" class as a direct
// descendent of the component's root template
// They can then trigger showPopover; ie "v-on:mouseover="showPopover""
// Note that once triggered, it will handle its own show/hide events

export default {
  methods: {
    setupPopover: function(event) {
      var content = this.$el.getElementsByClassName('popover-raw')[0].innerHTML;

      if (typeof this.popContainer === 'undefined') {
        // Hide all other popover elements (seems to fix issues with them lingering)
        $(".popover").hide();

        // Construct new popover
        $(event.target).popover({
          animation:false,
          trigger: 'manual',
          container: 'body',
          placement: 'top',
          html: true,
          title: this.getPopOverTitle(),
          content: function() {
            return content;
          }
        })

        // Show it
        $(event.target).popover('show')
        .on("mouseenter", function () {
          var _this = this;
          $(this).popover("show");
          $(".popover").on("mouseleave", function () {
            console.log('left child');
            $(_this).popover('hide');
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
              console.log('left parent');
              $(_this).popover("hide");
            }
          }, 300);
        });
      }
    },
  }
}
</script>
