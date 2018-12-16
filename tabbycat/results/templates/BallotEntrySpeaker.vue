<template>

  <div class="list-group-item">
    <div class="row">

      <div class="col-2 pt-2 p-lg-2 pr-0 p-1 speaker-position-label">
        PM
      </div>

      <div class="col mb-0 pr-md-2 pr-1 form-group">
        <div class="iron-person small pt-0 m-0 form-check form-check-inline" style="display: none;"
             data-toggle="tooltip" data-placement="bottom"
             title="Duplicate speeches are hidden from the speaker tab. If a speaker is 'iron-manning' you would typically mark only the lesser of their scores as a duplicate.">
          <span class="mt-2"></span>
        </div>
        <select name="og_speaker_s1" tabindex="1" class="form-control custom-select">
          <option value="" selected="">---------</option>
          <option value="">Ruby Took-Brandybuck</option>
          <option value="">Daría Briones</option>
        </select>
      </div>

      <div class="col-4 form-group pr-md-2 pr-1 score">
        <input type="number" class="form-control" min="50" max="99" step="1" tabindex="9">
      </div>

    </div>
  </div>

</template>

<script>

</script>
