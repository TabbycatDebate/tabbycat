<template>
  <div class="row">

    <div class="col-md-3">
      <div class="panel panel-default">
        <div class="panel-heading text-center">
          <h4 class="panel-title">Speaker Demographics</h4>
        </div>
        <div class="panel-body text-center no-side-padding">
          <donut-chart v-for="set in graphsData.speakers_gender"
                       :graph-data="set.data" :title="set.title"
                       :key="set.title"></donut-chart>
          <p v-if="graphsData.speakers_gender.length === 0">
            No Gender Information
          </p>
          <hr>
          <donut-chart v-for="set in graphsData.speakers_categories"
                       :graph-data="set.data" :title="set.title"
                       :key="set.title"></donut-chart>
          <p v-if="graphsData.speakers_categories.length === 0">
            No Speaker Categories Information
          </p>
          <hr>
          <donut-chart v-for="set in graphsData.speakers_region"
                       :graph-data="set.data" :title="set.title"
                       :regions="graphsData.regions"
                       :key="set.title"></donut-chart>
          <p v-if="graphsData.speakers_region.length === 0">
            No Regions Information
          </p>
        </div>
      </div>
    </div>

    <div class="col-md-3">
      <div class="panel panel-default">
        <div class="panel-heading text-center">
          <h4 class="panel-title">Adjudicator Demographics</h4>
        </div>
        <div class="panel-body text-center no-side-padding">
          <donut-chart v-for="set in graphsData.adjudicators_gender"
                       :graph-data="set.data" :title="set.title"
                       :key="set.title"></donut-chart>
          <p v-if="graphsData.adjudicators_gender.length === 0">
            No Gender Information
          </p>
          <hr>
          <donut-chart v-for="set in graphsData.adjudicators_region"
                       :graph-data="set.data" :title="set.title"
                       :regions="graphsData.regions"
                       :key="set.title"></donut-chart>
          <p v-if="graphsData.adjudicators_region.length === 0">
            No Region Information
          </p>
        </div>
      </div>
    </div>

    <div class="col-md-3">
      <div class="panel panel-default">
        <div class="panel-heading text-center">
          <h4 class="panel-title">Speaker Results</h4>
        </div>
        <div class="panel-body text-center">
          <text-display v-for="set in graphsData.speakers_results"
                        :set="set" :key="set.title"></text-display>
          <p v-if="graphsData.speakers_results.length === 0">
            No Gender Information
          </p>
          <hr>
          <text-display v-for="set in graphsData.detailed_speakers_results"
                        :set="set" :key="set.title"></text-display>
          <p v-if="graphsData.detailed_speakers_results.length === 0">
            No Region Information
          </p>
        </div>
      </div>
    </div>

    <div class="col-md-3">
      <div class="panel panel-default">
        <div class="panel-heading text-center">
          <h4 class="panel-title">Adjudicator Results</h4>
        </div>
        <div class="panel-body text-center">
          <text-display v-for="set in graphsData.adjudicators_results"
                        :set="set" :key="set.title"></text-display>
          <p v-if="graphsData.adjudicators_results.length === 0">
            No Adjudicator Ratings Yet
          </p>
          <hr>
          <text-display v-for="set in graphsData.detailed_adjudicators_results"
                        :set="set" :key="set.title"></text-display>
          <p v-if="graphsData.detailed_adjudicators_results.length === 0">
            No Adjudicator-Adjudicator Feedback
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import DonutChart from  '../../graphs/DonutChart.vue'
import TextDisplay from '../../graphs/TextDisplay.vue'

export default {
  components: { DonutChart, TextDisplay },
  props: [ 'graphsData' ],

}
</script>