<template>
  <div class="card-deck">

    <div class="card mt-3">
      <div class="card-body text-center px-0">
        <h5 class="card-title mb-4" v-text="gettext('Speaker Demographics')"></h5>
        <donut-chart v-for="set in graphsData.speakers_gender"
                     :graph-data="set.data" :title="set.title"
                     :key="set.title"></donut-chart>
        <p v-if="graphsData.speakers_gender.length === 0"
           v-text="gettext('No Gender Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.speakers_categories"
                     :graph-data="set.data" :title="set.title"
                     :key="set.title"></donut-chart>
        <p v-if="graphsData.speakers_categories.length === 0"
           v-text="gettext('No Speaker Categories Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.speakers_region"
                     :graph-data="set.data" :title="set.title"
                     :regions="graphsData.regions"
                     :key="set.title"></donut-chart>
        <p v-if="graphsData.speakers_region.length === 0"
           v-text="gettext('No Regions Information')">
        </p>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center">
        <h5 class="card-title mb-4" v-text="gettext('Speaker Results')"></h5>
        <h6 class="text-muted">
          {{ graphsData.gendered_speakers }}
          <span v-text="gettext('speakers with gender data')"></span><br>
          {{ graphsData.speaks_count }}
          <span v-text="gettext('speaker scores total')"></span>
        </h6>
        <hr>
        <text-display v-for="set in graphsData.speakers_results"
                      :set="set" :key="set.title"></text-display>
        <p v-if="graphsData.speakers_results.length === 0"
           v-text="gettext('No Gender Information')">
        </p>
        <text-display v-for="set in graphsData.detailed_speakers_results"
                      :set="set" :key="set.title"></text-display>
        <p v-if="graphsData.detailed_speakers_results.length === 0"
           v-text="gettext('No Region Information')">
        </p>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center px-0">
        <h5 class="card-title mb-4" v-text="gettext('Adjudicator Demographics')"></h5>
        <donut-chart v-for="set in graphsData.adjudicators_gender"
                     :graph-data="set.data" :title="set.title"
                     :key="set.title"></donut-chart>
        <p v-if="graphsData.adjudicators_gender.length === 0"
           v-text="gettext('No Gender Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.adjudicators_position"
                     :graph-data="set.data" :title="set.title"
                     :key="set.title"></donut-chart>
        <p v-if="graphsData.adjudicators_position.length === 0"
           v-text="gettext('No Position Information')">
        </p>
        <hr>
        <donut-chart v-for="set in graphsData.adjudicators_region"
                     :graph-data="set.data" :title="set.title"
                     :regions="graphsData.regions"
                     :key="set.title"></donut-chart>
        <p v-if="graphsData.adjudicators_region.length === 0"
           v-text="gettext('No Region Information')">
        </p>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center">
        <h5 class="card-title mb-4" v-text="gettext('Adjudicator Results')"></h5>
        <h6 class="text-muted">
          {{ graphsData.gendered_adjudicators }}
          <span v-text="gettext('adjudicators with gender data')"></span><br>
          {{ graphsData.feedbacks_count }}
          <span v-text="gettext('feedback scores total')"></span>
        </h6>
        <hr>
        <text-display v-for="set in graphsData.adjudicators_results"
                      :set="set" :key="set.title"></text-display>
        <p v-if="graphsData.adjudicators_results.length === 0"
           v-text="gettext('No Adjudicator Ratings Information')">
        </p>
        <text-display v-for="set in graphsData.detailed_adjudicators_results"
                      :set="set" :key="set.title"></text-display>
        <p v-if="graphsData.detailed_adjudicators_results.length === 0"
           v-text="gettext('No Adjudicator-Adjudicator Feedback Information')">
        </p>
      </div>
    </div>

  </div>
</template>

<script>
import DonutChart from  '../../templates/graphs/DonutChart.vue'
import TextDisplay from '../../templates/graphs/TextDisplay.vue'

export default {
  components: { DonutChart, TextDisplay },
  props: [ 'graphsData' ],

}
</script>