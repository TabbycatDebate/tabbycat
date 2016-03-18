<script type="text/x-template" id="feedback-question">

[[ question ]]
[[ question.text ]]
[[ question.seq ]]
[[ question.type ]]
[[ question.required ]]
[[ question.chair_on_panellist ]]
[[ question.panellist_on_chair ]]
[[ question.panellist_on_panellist ]]
[[ question.team_on_orallist ]]
<hr>

</script>

<!-- Register Component Behaviour -->
<script>
  Vue.component('feedback-question', {
    template: '#feedback-question',
    props: ['question'],
  })
</script>
