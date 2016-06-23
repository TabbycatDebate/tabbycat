<template>

  <section class="db-margins-m db-bordered db-flex-row db-flex-item-1">

    <div class="db-padding-horizontal db-align-vertical-center db-flex-item-1 db-vertical-center-text">
      <em><span v-if="returnLocation !== ''">Return Ballots to [[ returnLocation ]]</span></em>
    </div>

    <div class="db-item-gutter"></div>

    <div class="db-flex-item-1 db-flex-row">
      <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
        <em>Data Entry:</em>
      </div>
      <div class="db-flex-item db-fill-in ">
      </div>
      <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
        <em>Data Check:</em>
      </div>
      <div class="db-flex-item db-fill-in ">
      </div>
    </div>

  </section>

</template>

<script>
export default {
  props: ['returnLocation']
}
</script>
