<!-- Base Ballot Footer Template -->
<script type="text/x-template" id="base-ballot-footer">

  <section class="db-dont-fill-in db-margins-m db-bordered db-flex-row db-flex-item-1">

    <div class="db-padding-horizontal db-align-vertical-center db-flex-item-1 db-vertical-center-text">
      Return Ballots to [[ returnLocation ]].
    </div>

    <div class="db-item-gutter"></div>

    <div class="db-flex-item-1 db-flex-row">

        <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
          Data Entry:
        </div>
        <div class="db-flex-item db-fill-in ">
        </div>

        <div class="db-flex-item db-flex-static db-align-vertical-center db-right-text db-padding-horizontal">
          Data Check:
        </div>
        <div class="db-flex-item db-fill-in ">
        </div>

    </div>

  </section>

</script>

<!-- Division Droppable Component Behaviour -->
<script>
  Vue.component('base-ballot-footer', {
    template: '#base-ballot-footer',
    props: ['returnLocation']
  })
</script>
