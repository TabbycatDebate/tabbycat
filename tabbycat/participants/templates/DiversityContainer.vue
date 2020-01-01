<template>
  <div class="card-deck">

    <div class="card mt-3">
      <div class="card-body text-center px-0">
        <h5 class="card-title mb-4" v-text="gettext('Speaker Demographics')"></h5>
        <donut-chart v-for="set in graphsData.speakers_gender"
                     :graph-data="set.data" :title="set.title"
                     :key="'gender-' + set.title"></donut-chart>
        <p v-if="graphsData.speakers_gender.length === 0" class="text-muted"
           v-text="gettext('No Gender Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.speakers_categories"
                     :graph-data="set.data" :title="set.title"
                     :key="'categories-' + set.title"></donut-chart>
        <p v-if="graphsData.speakers_categories.length === 0" class="text-muted"
           v-text="gettext('No Speaker Categories Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.speakers_region"
                     :graph-data="set.data" :title="set.title"
                     :regions="graphsData.regions"
                     :key="'region-' + set.title"></donut-chart>
        <p v-if="graphsData.speakers_region.length === 0" class="text-muted"
           v-text="gettext('No Region Information')">
        </p>
        <hr>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center">
        <h5 class="card-title mb-4" v-text="gettext('Speaker Results')"></h5>
        <h6 class="text-muted">
          {{ graphsData.gendered_speakers }}
          <span v-text="gettext('speakers with gender data')"></span><br>
          {{ graphsData.speaks_count }}
          <span v-text="gettext('speaker scores analysed')"></span>
        </h6>
        <hr>
        <text-display v-for="set in graphsData.speakers_results"
                      :set="set" :key="'speakers-' + set.title"></text-display>
        <p v-if="graphsData.speakers_results.length === 0" class="text-muted"
           v-text="gettext('No Gender Information')">
        </p>
        <text-display v-for="set in graphsData.detailed_speakers_results"
                      :set="set" :key="'dspeakers-' + set.title"></text-display>
        <p v-if="graphsData.detailed_speakers_results.length === 0" class="text-muted"
           v-text="gettext('No Region Information')">
        </p>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center px-0">
        <h5 class="card-title mb-4" v-text="gettext('Adjudicator Demographics')"></h5>
        <donut-chart v-for="set in graphsData.adjudicators_gender"
                     :graph-data="set.data" :title="set.title"
                     :key="'demo-' + set.title"></donut-chart>
        <p v-if="graphsData.adjudicators_gender.length === 0" class="text-muted"
           v-text="gettext('No Gender Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.adjudicators_position"
                     :graph-data="set.data" :title="set.title"
                     :key="'position-' + set.title"></donut-chart>
        <p v-if="graphsData.adjudicators_position.length === 0" class="text-muted"
           v-text="gettext('No Position Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.adjudicators_region"
                     :graph-data="set.data" :title="set.title"
                     :regions="graphsData.regions"
                     :key="'region-' + set.title"></donut-chart>
        <p v-if="graphsData.adjudicators_region.length === 0" class="text-muted"
           v-text="gettext('No Region Information')">
        </p>
        <hr>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center">
        <h5 class="card-title mb-4" v-text="gettext('Adjudicator Results')"></h5>
        <h6 class="text-muted">
          {{ graphsData.gendered_adjudicators }}
          <span v-text="gettext('adjudicators with gender data')"></span><br>
          {{ graphsData.feedbacks_count }}
          <span v-text="gettext('feedback scores analysed')"></span>
        </h6>
        <hr>
        <text-display v-for="set in graphsData.adjudicators_results"
                      :set="set" :key="'adjs-' + set.title"></text-display>
        <p v-if="graphsData.adjudicators_results.length === 0" class="text-muted"
           v-text="gettext('No Adjudicator Ratings Information')">
        </p>
        <hr>
        <text-display v-for="set in graphsData.detailed_adjudicators_results"
                      :set="set" :key="'dadjs-' + set.title"></text-display>
        <p v-if="graphsData.detailed_adjudicators_results.length === 0" class="text-muted"
           v-text="gettext('No Adjudicator-Adjudicator Feedback Information')">
        </p>
        <hr>
      </div>
    </div>

  </div>
</template>

<script>
import TextDisplay from '../../templates/graphs/TextDisplay.vue'

export default {
  components: {
    DonutChart: () => import('../../templates/graphs/DonutChart.vue'),
    TextDisplay,
  },
  props: ['graphsData'],
}
</script>
