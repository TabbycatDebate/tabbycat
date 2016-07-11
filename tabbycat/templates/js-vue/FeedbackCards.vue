<!-- Feedback Cards -->
<template>

  <div class="modal fade" id="modalFeedbacks" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content">
        <div class="modal-header h4 text-center">Feedback</div>
        <div class="modal-body">
          <ul class="list-group" v-for="feedback in feedbacks">
            <li class="list-group-item list-group-item-success">
              <span class="badge">5.0</span>
              <span class="h5">Eunice Mcbride(Toronto, chair)</span>
            </li>
            <li class="list-group-item">
              <span class="glyphicon glyphicon-remove text-danger"></span>
              <small><strong title="" data-toggle="tooltip" data-original-title="Did this judge's decision concur with yours?">concur</strong></small>
            </li>
            <li class="list-group-item panel-footer">
              <em><small>submitted by Billy Griffin (Princeton, panellist), 2&nbsp;hours ago</small></em>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
export default {
  props: {
    feedbacks: Array,
  },
}
</script>
