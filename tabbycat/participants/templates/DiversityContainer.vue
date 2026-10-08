<script setup>
import { defineAsyncComponent, toRefs } from 'vue'
import { useDjangoI18n } from '../../templates/composables/useDjangoI18n.js'
import TextDisplay from '../../templates/graphs/TextDisplay.vue'

const DonutChart = defineAsyncComponent(() => import('../../templates/graphs/DonutChart.vue'))


const props = defineProps({
  graphsData: Object,
})

const { graphsData } = toRefs(props)

const { gettext } = useDjangoI18n()
</script>

<template>
  <div class="card-deck">
    <div class="card mt-3">
      <div class="card-body text-center px-0">
        <h5 class="card-title mb-4">
          {{ gettext('Speaker Demographics') }}
        </h5>
        <donut-chart
          v-for="set in graphsData.speakers_gender"
          :key="'gender-' + set.title"
          :graph-data="set.data"
          :title="set.title"
        />
        <p
          v-if="graphsData.speakers_gender.length === 0"
          class="text-muted"
        >
          {{ gettext('No Gender Information') }}
        </p>
        <hr>
        <donut-chart
          v-for="set in graphsData.speakers_categories"
          :key="'categories-' + set.title"
          :graph-data="set.data"
          :title="set.title"
        />
        <p
          v-if="graphsData.speakers_categories.length === 0"
          class="text-muted"
        >
          {{ gettext('No Speaker Categories Information') }}
        </p>
        <hr>
        <donut-chart
          v-for="set in graphsData.speakers_region"
          :key="'region-' + set.title"
          :graph-data="set.data"
          :title="set.title"
          :regions="graphsData.regions"
        />
        <p
          v-if="graphsData.speakers_region.length === 0"
          class="text-muted"
        >
          {{ gettext('No Region Information') }}
        </p>
        <hr>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center">
        <h5 class="card-title mb-4">
          {{ gettext('Speaker Results') }}
        </h5>
        <h6 class="text-muted">
          {{ graphsData.gendered_speakers }}
          <span>{{ gettext('speakers with gender data') }}</span><br>
          {{ graphsData.speaks_count }}
          <span>{{ gettext('speaker scores analysed') }}</span>
        </h6>
        <hr>
        <text-display
          v-for="set in graphsData.speakers_results"
          :key="'speakers-' + set.title"
          :set="set"
        />
        <p
          v-if="graphsData.speakers_results.length === 0"
          class="text-muted"
        >
          {{ gettext('No Gender Information') }}
        </p>
        <text-display
          v-for="set in graphsData.detailed_speakers_results"
          :key="'dspeakers-' + set.title"
          :set="set"
        />
        <p
          v-if="graphsData.detailed_speakers_results.length === 0"
          class="text-muted"
        >
          {{ gettext('No Region Information') }}
        </p>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center px-0">
        <h5 class="card-title mb-4">
          {{ gettext('Adjudicator Demographics') }}
        </h5>
        <donut-chart
          v-for="set in graphsData.adjudicators_gender"
          :key="'demo-' + set.title"
          :graph-data="set.data"
          :title="set.title"
        />
        <p
          v-if="graphsData.adjudicators_gender.length === 0"
          class="text-muted"
        >
          {{ gettext('No Gender Information') }}
        </p>
        <hr>
        <donut-chart
          v-for="set in graphsData.adjudicators_position"
          :key="'position-' + set.title"
          :graph-data="set.data"
          :title="set.title"
        />
        <p
          v-if="graphsData.adjudicators_position.length === 0"
          class="text-muted"
        >
          {{ gettext('No Position Information') }}
        </p>
        <hr>
        <donut-chart
          v-for="set in graphsData.adjudicators_region"
          :key="'region-' + set.title"
          :graph-data="set.data"
          :title="set.title"
          :regions="graphsData.regions"
        />
        <p
          v-if="graphsData.adjudicators_region.length === 0"
          class="text-muted"
        >
          {{ gettext('No Region Information') }}
        </p>
        <hr>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body text-center">
        <h5 class="card-title mb-4">
          {{ gettext('Adjudicator Results') }}
        </h5>
        <h6 class="text-muted">
          {{ graphsData.gendered_adjudicators }}
          <span>{{ gettext('adjudicators with gender data') }}</span><br>
          {{ graphsData.feedbacks_count }}
          <span>{{ gettext('feedback scores analysed') }}</span>
        </h6>
        <hr>
        <text-display
          v-for="set in graphsData.adjudicators_results"
          :key="'adjs-' + set.title"
          :set="set"
        />
        <p
          v-if="graphsData.adjudicators_results.length === 0"
          class="text-muted"
        >
          {{ gettext('No Adjudicator Ratings Information') }}
        </p>
        <hr>
        <text-display
          v-for="set in graphsData.detailed_adjudicators_results"
          :key="'dadjs-' + set.title"
          :set="set"
        />
        <p
          v-if="graphsData.detailed_adjudicators_results.length === 0"
          class="text-muted"
        >
          {{ gettext('No Adjudicator-Adjudicator Feedback Information') }}
        </p>
        <hr>
      </div>
    </div>
  </div>
</template>
