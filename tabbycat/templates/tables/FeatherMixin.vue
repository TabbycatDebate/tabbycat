<script>
import feather from 'feather-icons';
import _ from 'lodash'

// Provides the rendered version of an icon; for when it needs to update
// on DOM changes
// Inheriting classes must provide an icon computed property or data property

export default {
  computed: {
    getFeatherIcon: function() {
      // Need to dynamically update icons once table order changes
      // as they are otherwise tied to the DOM
      if (this.icon) {
        return feather.toSvg(this.icon);
      }
    }
  },
}
</script>