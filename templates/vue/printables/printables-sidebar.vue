<!-- Base Scoresheet Template -->
<script type="text/x-template" id="printables-sidebar">

  <aside role="complementary" class="dbui-sidebar db-hide db-flex-column">

    <div class="db-flex-static">
      <h4>Ballot Configuration</h4>

      <div class="form-block toggle-block db-flex-row">
        <button v-on:click="setFeedbackFalse" v-bind:class="{ 'active': !showFeedback }" class="toggle-btn left">Score Sheet</button>
        <button v-on:click="setFeedbackTrue" v-bind:class="{ 'active': showFeedback }" class="toggle-btn right">Feedback Sheet</button>
        <input class="hidden" type="checkbox" id="showFeedbackCheck" v-model="showFeedback">
      </div>

      <div class="form-block toggle-block db-flex-row">
        <button v-on:click="setBPFalse" v-bind:class="{ 'active': !isBP }" class="toggle-btn left">2 Teams</button>
        <button v-on:click="setBPTrue" v-bind:class="{ 'active': isBP }" class="toggle-btn right">4 Teams</button>
      </div>

      <div class="form-block toggle-block db-flex-row">
        <button v-on:click="setPortrait" v-bind:class="{ 'active': !pageIsLandscape }" class="toggle-btn left">A4 Portrait</button>
        <button v-on:click="setLandscape" v-bind:class="{ 'active': pageIsLandscape }" class="toggle-btn right">A4 Landscape</button>
      </div>

      <div class="form-block db-flex-row">
        <input type="text" class="side-by-side" id="tournamentNameText" v-bind:class="{ 'placeholder': tournamentName === 'Tournament Name' }" v-model="tournamentName">
        <div class="divider"></div>
        <input type="text" class="side-by-side" id="returnLocationText" v-bind:class="{ 'placeholder': returnLocation === 'Tab Room Location' }" v-model="returnLocation">
      </div>

      <div class="form-block db-flex-row">
        <div class="db-flex-item-1">
          <input type="checkbox" id="doubleUpCheck" v-model="doubleUp">
          <label for="doubleUpCheck">Two-Per-Page</label>
        </div>
        <div class="divider"></div>
        <div class="db-flex-item-1">
          <input type="checkbox" id="showTabRoomRowCheck" v-model="showTabRoomRow">
          <label for="showTabRoomRowCheck">Show Tab Room Info</label>
        </div>
      </div>

      <template v-if="showFeedback" transition="expand">

        <div class="form-block db-flex-row">
          <div class="db-flex-item-1">
            <input type="checkbox" id="showFeedbackKeyWordsText" v-model="showFeedbackKeyWords">
            <label for="showFeedbackKeyWordsText">Show Keywords (seperate with commas)</label>
          </div>
        </div>

        <div class="form-block db-flex-row" v-if="showFeedbackKeyWords">
            <textarea class="db-flex-item-1" v-model="feedbackKeywords">[[ feedbackKeywords ]]</textarea>
        </div>

      </template>

      <template v-if="!showFeedback" transition="expand">

        <div class="form-block db-flex-row">

          <div class="db-flex-item-1">
            <input type="checkbox" id="hasRepliesCheck" v-model="hasReplies">
            <label for="hasRepliesCheck">Reply Speeches</label>
          </div>
          <div class="divider"></div>
          <div class="db-flex-item-1">
            <input type="checkbox" id="hasMotionsCheck" v-model="hasMotionSelection">
            <label for="hasMotionsCheck">Motion Selection</label>
          </div>

        </div>

        <div class="form-block db-flex-row">

          <div class="db-flex-item-1">
            <input type="checkbox" id="showInfoCheck" v-model="showInfo">
            <label for="showInfoCheck">Show Rules Info</label>
          </div>
          <div class="divider"></div>
          <div class="db-flex-item-1">
            <input type="checkbox" id="showPronounsCheck" v-model="showPronouns">
            <label for="showPronounsCheck">Show Pronouns</label>
          </div>

        </div>

        <div class="form-block db-flex-row" v-if="showInfo">
          <textarea class="db-flex-item-1" v-model="infoText">[[ infoText ]]</textarea>
        </div>

      </template>

    </div>

    <div class="db-flex-static dbui-sidebar-section">
      <h4>How to Print</h4>
      <p class="db-notchrome-info">
        <strong>For best results print from <a href="https://www.google.com/chrome/" target="_blank">Chrome</a>.</strong> In other browsers margins and layouts may be off.</span>
      </p>
      <p>
        <span class="db-safari-info">
          Ensure "Print backgrounds" is <strong>on</strong> and "Print headers and footers" is <strong>off</strong>.</span>
        <span class="db-firefox-info">
          Use your browser's print function (File > Print) and set paper
          size/orientations as desired. In the "Show Details" section set "Pages" to be from <strong>1 to 1</strong> and set "Print Background Colors" <strong>on</strong>. If possible reduce the default "Margins".</span>
        <span class="db-chrome-info">
          Use your browser's print function (File > Print) and set paper
          size/orientations as desired. In the "More Settings" section ensure "Simplify Page" is <strong>off</strong> and "Background graphics" is <strong>on</strong>. You may also want to reduce the default "Margins".<span>
      </p>
    </div>


    <div class="db-flex-item db-align-vertical-center">
      <script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
      <!-- Sidebar Ad -->
      <ins class="adsbygoogle"
           style="display:inline-block;width:300px;height:250px"
           data-ad-client="ca-pub-4127280252237686"
           data-ad-slot="3424227058"></ins>
      <script>
      (adsbygoogle = window.adsbygoogle || []).push({});
      </script>
    </div>

    <div class="db-flex-static">

      <p class="small">Created by <a target="_blank" href="http://philipbelesky.com/">Philip</a>.
      Feedback <a target="_blank" href="http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=">
         welcome</a>.
      Based on <a target="_blank" href="https://github.com/czlee/tabbycat">Tabbycat's</a>
      pre-filled ballots feature.</p>

    </div>

  </aside>

</script>

<script>
  Vue.component('printables-sidebar', {
    template: '#printables-sidebar',
    props: ['data'],
  })
</script>
