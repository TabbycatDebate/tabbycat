<script>
// Note that subscribing objects must provide a getEntity() that
// provides gender/region info
// Their classes should be bound to a diversityHighlights somewhere

export default {
  computed: {
    diversityHighlights: function () {
      var entity = this.getEntity()[0];
      var class_string = " diversity-highlightable"

      if (typeof entity.gender !== 'undefined') {
        if (entity.gender === "M") {
          class_string += " gender-male"
        } else if (entity.gender === "F") {
          class_string += " gender-nm"
        } else if (entity.gender === "O") {
          class_string += " gender-other"
        } else {
          class_string += " gender-unknown"
        }
      }

      if (typeof entity.gender_name !== 'undefined') {
        var speaker_genders = entity.gender_name.toLowerCase().split(",")
        var men_count = 0, notmen_count = 0;
        for (var i = 0; i < speaker_genders.length; ++i) {
          if (speaker_genders[i].trim() === "male") {
            men_count += 1
          }
          if (speaker_genders[i].trim() === "female") {
            notmen_count += 1
          }
        }
        class_string += ' gender-men-' + men_count
        class_string += ' gender-notmen-' + notmen_count
      }


      if (entity.region && typeof entity.region !== "undefined") {
        class_string += " region-" + entity.region['seq']
      }

      if (entity.categories && typeof entity.categories !== "undefined") {
        // As above we need to normalise
        for (var i = 0; i < entity.categories.length; ++i) {
          class_string += " category-" + entity.categories[i].seq
        }
      }

      return class_string;
    },
  }
}
</script>
