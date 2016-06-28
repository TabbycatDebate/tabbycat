<script>
// Note that subscribing objects must provide a getEntity() that
// provides gender/region info
// Their classes should be bound to a diversityHighlights somewhere

export default {
  computed: {
    diversityHighlights: function () {
      var entity = this.getEntity()[0];
      var class_string = " diversity-highlightable"
      if (entity.gender === "M") {
        class_string += " male"
      } else if (entity.gender === "F") {
        class_string += " nm"
      } else if (entity.gender === "O") {
        class_string += " other "
      } else {
        class_string += " unknown "
      }
      if (entity.region !== "") {
        class_string += " region-"
        class_string += entity.region
      }
      if (entity.category !== "") {
        class_string += " category-"
        class_string += entity.category
      }
      return class_string;
    },
  }
}
</script>
