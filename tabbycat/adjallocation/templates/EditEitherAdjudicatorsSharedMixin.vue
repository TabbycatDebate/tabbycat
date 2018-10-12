<script>
// Mixin for shared logic between editing debate adjudicators and editing panel adjudicators
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'
import DebateImportance from './DebateImportance.vue'

export default {
  mixins: [DragAndDropContainerMixin],
  components: { DebateImportance },
}
</script>
