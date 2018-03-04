<template>

  <div class="list-group mt-3">

    <div class="list-group-item">
      <input v-model="message" autofocus placeholder="identifier" type="number"
             step="1" class="form-control">
    </div>
    <!-- extra items for error messages -->

  </div>

</template>

<script>
import AjaxMixin from '../../templates/ajax/AjaxMixin.vue'

import _ from 'lodash'

export default {
  mixins: [AjaxMixin],
  components: { },
  props: { },
  computed: { },
  methods: { }
}
</script>
