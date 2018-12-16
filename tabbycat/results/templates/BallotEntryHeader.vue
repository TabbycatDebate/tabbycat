<template>
  <div class="card mt-3">
    <div class="list-group list-group-flush">

      <div class="list-group-item pt-4">
        <h4 class="card-title mt-0 mb-2 d-inline-block">
          Debate Information
        </h4>
      </div>
      <!-- TODO: Side choosing -->
      <!-- TODO: Motion choosing -->
      <!-- TODO: Veto choosing -->

      <div class="list-group-item pb-3 pt-3">
        <div class="form-group">
          <select class="required custom-select form-control" id="hasIron">
            <option value="0">
              There were no speakers who spoke multiple times (i.e. no 'Iron' person speeches)
            </option>
            <option value="1">
              There were speakers who spoke multiple times (i.e. one or more 'Iron' person speeches)
            </option>
          </select>
        </div>
      </div>

    </div>
  </div>
</template>

<script>

</script>
