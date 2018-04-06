<template>
  <div class="modal fade" id="autoAllocationIntroAlert" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered modal-sl">
      <div class="modal-content">
        <div class="modal-body">
          <div class="tab-content lead p-3" id="pills-tabContent">

            <div class="tab-pane fade show active" id="pills-intro" role="tabpanel">
              <h2>Welcome to the Edit Adjudicators interface</h2>
              <p class="mt-4">The allocation interface has a lot of features, so its worth providing a quick overview of how it works. This modal will only show once; but if you ever want to review it you can change the <em>show allocation introduction</em> under the <em>UI Options</em> section of this tournament's configuration.</p>
              <p>Use the buttons at the bottom left to view the different stages of the workflow.</p>
            </div>

            <div class="tab-pane fade" id="pills-priorities" role="tabpanel">
              <h2>Assigning Priorities</h2>
              <p>Debates with higher 'priority' values are given a higher-strength panels when adjudicators are automatically assigned (as described in the next step). You can use the <strong class="text-success">Auto-Prioritise</strong> button to have Tabbycat automatically assign relative importances (based on either a room's bracket or 'liveness'). With either option the highest priority value is not used so that it is available as an override.</p>
              <p>You can of course skip this step only only ever assign priorities manually, or use the automatic assignment just as a first pass. Note that priorities are relative; no absolute: if half the debates are set to "5" and the rest to "1" it would be the same as if they were set to "4" and "2" respectively.</p>
              <p>A debate's priority can be manually set using a slider. It looks like this:</p>
              <input max="2" min="-2" step="1" type="range" class="mb-4 mt-3 mx-5">
              <p>Even if using the auto-prioritise feature it is generally a good idea to check over each debate's priority and check for any edge cases that mean it should have a lower or higher value.
              </p>
            </div>

            <div class="tab-pane fade" id="pills-allocating" role="tabpanel">
              <h2>Allocating Adjudicators</h2>
              <p class="mt-4">You can use the <strong class="text-success">Auto-Allocate</strong> button to have Tabbycat automatically create panels for all debates.</p>
              <p>Whether you used auto-allocate or not, adjudicators can be dragged and dropped between debates to create or modify form panels. Whenever an adjudicator is added or removed from a panel the change will be saved automatically.</p>
              <p>Note that grey area at the bottom of the screen serves as an 'unused' area. Adjudicators in here will not show up in the resulting allocation; however it can also be handy to use as a staging area for adjudicators that you want to assign later on.</p>
            </div>

            <div class="tab-pane fade" id="pills-highlights" role="tabpanel">
              <h2>Highlights</h2>
              <p class="mt-4">As you hover over an adjudicator or team it will highlight other adjudicators or teams with solid blocks of color. This can be used to check where an adjudicator can be moved to safely.</p>
              <div class="mt-2 btn conflictable hover-histories-1-ago">
                Blue highlights show that the teams/adjudicators have been matched in earlier rounds.
              </div>
              <div class="mt-2 btn conflictable hover-histories-3-ago">
                Darker highlights mean this match happened more recently than lighter highlights
              </div>
              <div class="mt-2 btn conflictable hover-team">
                Red highlights indicates a personal conflict exists
              </div>
              <div class="mt-2 btn conflictable hover-institution">
                Orange highlights indicates a institutional conflict exists
              </div>
              <p class="mt-3">The same color scheme is used to convey information <em>within</em> a panel
              except it uses border colors rather than solid blocks</p>
              <div class="draw-team-cell mt-2 row px-3">
                <div class="col btn p-2 conflictable panel-histories-2-ago">
                  Adj/Team A has seen B before
                </div>
                <div class="col ml-2 btn p-2 conflictable panel-histories-2-ago">
                  Adj/Team B has seen A before
                </div>
              </div>
              <div class="draw-team-cell mt-2 row px-3">
                <div class="col btn p-2 conflictable panel-team">
                  Adj/Team A has a conflict with B
                </div>
                <div class="col ml-2 btn p-2 conflictable panel-team">
                  Adj/Team B has a conflict with A
                </div>
              </div>
              <div class="draw-team-cell mt-2 row px-3">
                <div class="col btn p-2 conflictable panel-institution">
                  Adj/Team A is from B's institution
                </div>
                <div class="col ml-2 btn p-2 conflictable panel-institution">
                  Adj/Team B is from A's institution
                </div>
              </div>
            </div>

            <div class="tab-pane fade" id="pills-slideovers" role="tabpanel">
              <h2>Slideovers</h2>
              <p class="mt-4">As you hover over an adjudicator or team a series of horizontal rows will appear at the top of the screen. For teams this shows:</p>
              <ul>
                <li>The team's speakers</li>
                <li>The break categories they are eligible</li>
                <li>Whether the team is still 'live' for that category</li>
                <li>How many points a team is on</li>
                <li>Whom they were judged by in prior rounds</li>
              </ul>
              <p>For adjudicators this shows:</p>
              <ul>
                <li>Their personal and institutional conflicts</li>
                <li>Whom they judged and judged with in prior rounds</li>
                <li>Their rankings in terms of their feedback ratings on a relative scale (A/B/C/etc corresponding with a percentile)</li>
              </ul>
            </div>

            <div class="tab-pane fade" id="pills-toggles" role="tabpanel">
              <h2>Toggles</h2>
              <p class="mt-4">There are a series of buttons in the top-right that can be used to turn on or off additional 'overlays' of information. They look like this:</p>
              <div class="btn-group mb-3">
                <button class="btn btn-outline-primary hoverable disabled">
                  <i data-feather="eye"></i> Break
                </button><button class="btn btn-outline-primary hoverable disabled">
                  <i data-feather="eye"></i> Region
                </button><button class="btn btn-outline-primary hoverable disabled">
                  <i data-feather="eye"></i> Gender
                </button><button class="btn btn-outline-primary hoverable disabled">
                  <i data-feather="eye"></i> Rank
                </button>
              </div>
              <p>When activiated they will color all teams/adjudicators according the specified category. The top-middle of a screen then displays a key for what the colors mean, such as this:</p>
              <div class="btn-group mb-3">
                <button class="visible-lg-block btn btn-outline-secondary disabled"><span class="d-xl-inline d-none">Gender</span> Key</button>
                <button class="btn gender-display gender-male">Male</button>
                <button class="btn gender-display gender-f">Female</button>
                <button class="btn gender-display gender-o">Other</button> <button class="btn gender-display gender-">Unknown</button>
              </div>
              <p>These toggles are typically use near the end of an allocation to check for obvious disparities in gender, regional, or judge ranking balance across debates. Because that they can obscure the colors used to identify conflicts, it's worth turning them off before doing a final check of the allocation.</p>
            </div>

            <div class="tab-pane fade" id="pills-liveness" role="tabpanel">
              <h2>Liveness</h2>
              <p class="mt-4">Teams in the draw shown with a ☆ are those that have been calculated
              as being 'live' for a category; i.e. that they can still break:</p>
              <div class="mb-4 mt-4">
                <div class="small btn btn-light mr-3">LIVE TEAM ☆</div>
                <div class="small btn btn-light mr-3">LIVE TEAM (IN TWO CATEGORIES) ☆☆</div>
                <div class="small btn btn-light mr-3">SAFE TEAM</div>
                <div class="small btn btn-light mr-3">DEAD TEAM</div>
              </div>
              <p>Teams without a star are either 'safe' (definitely breaking) or 'dead' (unable to break). If you hover over a team the top-right will clarify which is the case and for which category.</p>
              <p><strong class="text-danger">Important Note:</strong> liveness, as displayed here and calculated for auto-prioritisation, <em>does not take into account many edge cases</em> such as a team breaking into ESL but only participating in the general break, or special break rules such as 'caps'. Be cautious in trusting these figures, especially if you don't have a strictly mathematical break.</p>
            </div>

            <div class="tab-pane fade" id="pills-sharding" role="tabpanel">
              <h2>Sharding (beta)</h2>
              <p class="mt-4">'Sharding' allows you to split up the allocation interface into smaller sub-sections that only contain a portion of the entire draw. This can be used to essentially distribute the task of allocating adjudicators across multiple computers without worrying about each person overwriting the other's changes.</p>
              <p><strong class="text-danger">Important Note:</strong> this feature is in beta, and its use requires clear communication amongst those using it. You need everyone to be absolutely clear how the draw is being divided (i.e. <em>thirds</em> by <em>top-to-bottom</em>) and be sure that only one person is ever viewing each subset. If multiple people are viewing the same subset, or one person is still changing the entire draw you will end up overwriting each other's changes without realising it.</p>
              <p class="mt-4">When viewing a shard note the unallocated adjudicator panel will be hidden and the Auto-Prioritise and Auto-Allocate options will be disabled. You should ensure adjudicators have already been allocated, or remember to view the entire draw afterwards to allocate the remaining adjudicators. Once you have finishing allocating using shards be sure to check the main draw page and ensure that there have are no double-allocations, empty panels, unnoticed conflicts etc.</p>
            </div>

          </div>
        </div>
        <div class="modal-footer justify-content-between">

          <ul class="nav nav-pills" id="pills-tab" role="tablist">
            <li class="nav-item">
              <a class="nav-link btn active" id="pills-intro-tab" data-toggle="pill"
                 href="#pills-intro" role="tab" aria-controls="pills-intro" aria-selected="true">
                Intro
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-priorities-tab" data-toggle="pill"
                 href="#pills-priorities" role="tab" aria-controls="pills-priorities" aria-selected="false">
                Priorities
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-allocating-tab" data-toggle="pill"
                 href="#pills-allocating" role="tab" aria-controls="pills-allocating" aria-selected="false">
                Allocating
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-highlights-tab" data-toggle="pill"
                 href="#pills-highlights" role="tab" aria-controls="pills-highlights" aria-selected="false">
                Highlights
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-slideovers-tab" data-toggle="pill"
                 href="#pills-slideovers" role="tab" aria-controls="pills-slideovers" aria-selected="false">
                Slideovers
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-toggles-tab" data-toggle="pill"
                 href="#pills-toggles" role="tab" aria-controls="pills-toggles" aria-selected="false">
                Toggles
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-liveness-tab" data-toggle="pill"
                 href="#pills-liveness" role="tab" aria-controls="pills-liveness" aria-selected="false">
                Liveness
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link btn" id="pills-sharding-tab" data-toggle="pill"
                 href="#pills-sharding" role="tab" aria-controls="pills-sharding" aria-selected="false">
                Shards
              </a>
            </li>
          </ul>

          <button type="button" class="btn btn-secondary" data-dismiss="modal">
            Close
          </button>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: { roundInfo: Object, showIntroModal: Boolean },
  mounted: function () {
    if (this.showIntroModal) {
      $('#autoAllocationIntroAlert').modal()
    }
  },
}

</script>
