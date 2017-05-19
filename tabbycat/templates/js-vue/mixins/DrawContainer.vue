<script>
export default {
  mixins: [
  ],
  props: {
    debates: Array,
    unallocatedItems: Array
  },
  computed: {
    positions: function() {
      return this.debates[0].positions // Shortcut function
    }
  },
  methods: {
  },
  events: {
  }
}
</script>
