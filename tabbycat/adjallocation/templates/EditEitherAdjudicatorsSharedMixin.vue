<script>
// Mixin for shared logic between editing debate adjudicators and editing panel adjudicators
import DragAndDropContainerMixin from '../../utils/templates/DragAndDropContainerMixin.vue'
import DebateImportance from './DebateImportance.vue'
import ModalForSharding from '../../utils/templates/modals/ModalForSharding.vue'
import ModalForPrioritising from '../../utils/templates/modals/ModalForPrioritising.vue'
import ModalForAllocating from '../../utils/templates/modals/ModalForAllocating.vue'

export default {
  mixins: [DragAndDropContainerMixin],
  components: { DebateImportance, ModalForSharding, ModalForPrioritising, ModalForAllocating },
}
</script>
