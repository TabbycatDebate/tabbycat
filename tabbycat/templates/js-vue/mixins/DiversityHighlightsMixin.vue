<script>
// Note that subscribing objects must provide a entity property that
// provides gender/region info
// Their classes should be bound to a diversityHighlights somewhere

export default {
  computed: {
    diversityState: function () {
      var adjorteam = this.adjorteam;
      var class_string = ""
      if (adjorteam.region_show === true) {
        class_string += " region-display";
      }
      if (adjorteam.gender_show === true) {
        class_string += " gender-display";
      }
      if (adjorteam.category_show === true) {
        class_string += " category-display";
      }
      return class_string
    },
    diversityHighlights: function () {
      var adjorteam = this.adjorteam;

      var class_string = ""
      if (typeof adjorteam.gender !== 'undefined') {
        if (adjorteam.gender === "M") {
          class_string += " has-gender gender-male"
        } else if (adjorteam.gender === "F") {
          class_string += " has-gender gender-nm"
        } else if (adjorteam.gender === "O") {
          class_string += " has-gender gender-other"
        } else {
          class_string += " gender-unknown"
        }
      }

      if (adjorteam.speakers && typeof adjorteam.speakers !== 'undefined') {
        var men_count = 0, notmen_count = 0;
        for (var i = 0; i < adjorteam.speakers.length; ++i) {
          if (adjorteam.speakers[i].gender === "M") {
            men_count += 1
          }
          if (adjorteam.speakers[i].gender === "F" || adjorteam.speakers[i].gender === "O" ) {
            notmen_count += 1
          }
        }
        if (notmen_count > 0 || men_count > 0) {
          class_string += ' has-gender '
        }
        class_string += ' gender-men-' + men_count
        class_string += ' gender-notmen-' + notmen_count
      }

      if (adjorteam.region && typeof adjorteam.region !== "undefined") {
        class_string += " has-region region-" + adjorteam.region['seq']
      }

      if (adjorteam.categories && typeof adjorteam.categories !== "undefined") {
        // As above we need to normalise
        for (var i = 0; i < adjorteam.categories.length; ++i) {
          class_string += " has-category category-" + adjorteam.categories[i].seq
        }
      }

      return class_string;
    },
  }
}
</script>
