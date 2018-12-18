<template>

  <div class="card pr-0 mr-0 m-2">
    <div class="list-group list-group-flush">

      <div class="list-group-item pb-0">
        <div class="row">
          <!-- team-name class used by unknown sides switcher -->
          <div class="col mr-auto card-title pl-md-2 pl-1" v-html="team.name"></div>
          <div class="col-auto card-subtitle text-muted text-right pt-2 pr-md-2 pr-1">
            <h6>{{ team.position }}</h6>
          </div>
        </div>
      </div>

      <ballot-entry-speaker v-for="(speaker, index) in team.speakers"
                            :speaker="speaker" :key="index"></ballot-entry-speaker>

      <div class="list-group-item">
        <div class="row">

          <div class="col-6 mr-0 col-mr-auto pl-md-2 pl-1 btn-group">
            <button class="btn btn-outline-secondary btn-no-hover" readonly>Rank</button>
            <button class="btn btn-secondary border-right-0 btn-no-hover" readonly>?</button>
            <button class="btn btn-outline-secondary btn-no-hover" readonly>Margin</button>
            <button class="btn btn-secondary btn-no-hover" readonly>+0</button>
          </div>

          <div class="col"></div>

          <div class="col-4 btn-group pr-md-2 pr-1">
            <button class="btn btn-block btn-secondary btn-no-hover" readonly>00</button>
          </div>

        </div>
      </div>

    </div>
  </div>

</template>

<script>
import BallotEntrySpeaker from './BallotEntrySpeaker.vue'

export default {
  components: { BallotEntrySpeaker },
  props: { team: Object },
  data: function () {
    return {
    }
  },
}
</script>
