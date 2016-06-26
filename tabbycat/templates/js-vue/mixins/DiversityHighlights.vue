<script>
export default {
  computed: {
    diversityHighlights: function () {
      if (typeof this.adj !== 'undefined') {
        var entity = this.adj;
      } else if (typeof this.team !== 'undefined') {
        var entity = this.team;
      }
      console.log(entity);
      var class_string = "diversity-highlightable "
      if (entity.gender === "M") {
        class_string += "male "
      } else if (entity.gender === "F") {
        class_string += "nm "
      } else if (entity.gender === "O") {
        class_string += "other "
      } else {
        class_string += "unknown "
      }
      if (entity.region !== "") {
        class_string += "region-"
        class_string += entity.region
      }
      return class_string;
    },
  }
}
</script>
