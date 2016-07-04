<script>
// Note that subscribing objects must provide a entity property that
// provides gender/region info
// Their classes should be bound to a diversityHighlights somewhere

export default {
  computed: {
    diversityHighlights: function () {
      var class_string = " diversity-highlightable"
      var adjorteam = this.adjorteam;

      if (typeof adjorteam.gender !== 'undefined') {
        if (adjorteam.gender === "M") {
          class_string += " gender-male"
        } else if (adjorteam.gender === "F") {
          class_string += " gender-nm"
        } else if (adjorteam.gender === "O") {
          class_string += " gender-other"
        } else {
          class_string += " gender-unknown"
        }
      }

      if (adjorteam.gender_name && typeof adjorteam.gender_name !== 'undefined') {
        var speaker_genders = adjorteam.gender_name.toLowerCase().split(",")
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

      if (adjorteam.region && typeof adjorteam.region !== "undefined") {
        class_string += " region-" + adjorteam.region['seq']
      }

      if (adjorteam.categories && typeof adjorteam.categories !== "undefined") {
        // As above we need to normalise
        for (var i = 0; i < adjorteam.categories.length; ++i) {
          class_string += " category-" + adjorteam.categories[i].seq
        }
      }

      return class_string;
    },
  }
}
</script>
