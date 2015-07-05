{% load debate_tags %}
{% load staticfiles %}

// UTILITY FUNCTIONS

function DOMIdtoInt(e) {
  return parseInt($(e).attr('id').split('_')[1]);
}

function formatScore(n) {
  return n.toPrecision(2);
}

function removeConflictClasses(el) {
  $(el).removeClass("personal-conflict institutional-conflict history-conflict adjudicator-conflict");
}

function removeUnusedRow(oldHolder) {
  var old_row = oldHolder.parent(); // Get the <tr>
  unusedAdjTable.row(old_row).remove().draw();
}

function rebindHoverEvents(el) {
  $(el).bind("mouseover", function(e) {
    display_conflicts(e.currentTarget);
  }).bind( "mouseout", function(e) {
    remove_conflicts(e.currentTarget);
  })
}

// Used by auto-allocation; removes all data before the auto sweep
function reset() {
  $('.adj').remove();
  unusedAdjTable.clear();
}

// DATA INITIALISATION FUNCTIONS

function load_adjudicator_scores(callback) {
  $.getJSON("{% tournament_url adj_scores %}", function(data) {
    all_adj_scores = data;
    if (callback) callback();
  });
}

function load_allocation_data(data) {
  $.each(data.debates, function(debate_id, adj_data) {
    if (adj_data.chair) {
      set_chair(debate_id, adj_data.chair);
      {% if duplicate_adjs %} // If duplicating adjs need to copy over those allocated
      moveToUnused(_make_adj(adj_data.chair));
      {% endif %}
    }
    clear_panel(debate_id);
    $.each(adj_data.panel, function(idx, adj) {
      add_panellist(debate_id, adj);
      {% if duplicate_adjs %} // If duplicating adjs need to copy over those allocated
      moveToUnused(_make_adj(adj));
      {% endif %}
    });
    clear_trainees(debate_id);
    $.each(adj_data.trainees, function(idx, adj) {
      add_trainee(debate_id, adj);
      {% if duplicate_adjs %} // If duplicating adjs need to copy over those allocated
      moveToUnused(_make_adj(adj));
      {% endif %}
    });

  });
  $.each(data.unused, function(idx, adj_data) {
    moveToUnused(_make_adj(adj_data));
  });
}

function load_allocation(callback) {
  $.getJSON("{% round_url draw_adjudicators_get %}", function(data){
    load_allocation_data(data);
    callback();
  });
}

function load_conflict_data() {
  $.getJSON("{% round_url adj_conflicts %}", function(data) {
    all_adj_conflicts = data;
    $(".adj").each( function() {
      // insert blank entries for adjs who aren't there (those without conflicts)
      var id = DOMIdtoInt(this);
      if (all_adj_conflicts['personal'][id] == undefined) { all_adj_conflicts['personal'][id] = []; }
      if (all_adj_conflicts['history'][id] == undefined) { all_adj_conflicts['history'][id] = []; }
      if (all_adj_conflicts['institutional'][id] == undefined) { all_adj_conflicts['institutional'][id] = []; }
      if (all_adj_conflicts['adjudicator'][id] == undefined) { all_adj_conflicts['adjudicator'][id] = []; }
    });
    update_all_conflicts();
  });
}

function append_adj_scores() {
  $(".adj").each(function() {
    $(this).prop('title', $(this).children("span").text());
    $(this).children("span").prepend('<a data-toggle="modal" data-target="#adj-feedback" title="Click to view feedback history" data-toggle="tooltip" class="info">' + formatScore(all_adj_scores[DOMIdtoInt(this)]) + '</a> ');
    $("a", this).click(function() {
      // Function to handle opening the modal window
      var adj_row = $(this).parent().parent(); // Going back up to the div with the id
      var adj_name = adj_row.attr('title');
      var adj_id = DOMIdtoInt(adj_row);
      $("#modal-adj-name").text(adj_name); // Updating header of the modal
      var adj_feedback_url = '{% tournament_url get_adj_feedback %}?id=' + adj_id;
      adjFeedbackModalTable.ajax.url(adj_feedback_url).load();
    }).tooltip();
  });
}
;

// CONFLICT BEHAVIOURS

// Read the dicitionary and check if the adj has any conflicts
function eachConflictingTeam(adj_id, fn) {
  $.each(all_adj_conflicts['personal'][adj_id], function (i, n) {
    $("#team_" + n).each( function() { fn('personal', this); });
  });
  $.each(all_adj_conflicts['history'][adj_id], function (i, n) {
    $("#team_" + n).each( function() { fn('history', this); });
  });
  $.each(all_adj_conflicts['institutional'][adj_id], function (i, n) {
    $("#team_" + n).each( function() { fn('institutional', this); });
  });
  $.each(all_adj_conflicts['adjudicator'][adj_id], function (i, n) {
    $("#adj_" + n).each( function() { fn('adjudicator', this); });
  });
}

function display_conflicts(target) {
  if (draggingCurrently === false) {
    eachConflictingTeam(DOMIdtoInt(target),
      function (type, elem) {
        $(elem).addClass(conflictTypeClass[type]);
      }
    );
  }
}

function remove_conflicts(target) {
  if (draggingCurrently === false) {
    eachConflictingTeam(DOMIdtoInt(target),
      function (type, elem) {
        $(elem).removeClass(conflictTypeClass[type]);
      }
    );
    removeConflictClasses(target);
    update_all_conflicts(); // Need to check we haven't removed in-situ conflicts
  }
}

// Checks/highlights any existing conflicts on in-place data
function update_all_conflicts() {
  // Remove all current conflicts
  removeConflictClasses($(".teaminfo"));
  removeConflictClasses($(".adj"));
  // Recalculate in-situ conflicts
  $("#allocationsTable tbody tr").each( function() {
    updateConflicts(this);
  });
}

// Checks an individual debate for circumstances of conflict on each row
function updateConflicts(debate_tr) {
  $(".adj", debate_tr).each( function() {
    var adj = this;
    var adj_id = DOMIdtoInt(this);

    // Check each team within each debate
    $("td.teaminfo", debate_tr).each( function() {
      if ($.inArray(DOMIdtoInt(this),all_adj_conflicts['personal'][adj_id]) != -1) {
        $(this).addClass("personal-conflict");
        $(adj).addClass("personal-conflict");
      } else if ($.inArray(DOMIdtoInt(this),all_adj_conflicts['institutional'][adj_id]) != -1) {
        $(this).addClass("institutional-conflict");
        $(adj).addClass("institutional-conflict");
      } else if ($.inArray(DOMIdtoInt(this), all_adj_conflicts['history'][adj_id]) != -1) {
        $(this).addClass("history-conflict");
        $(adj).addClass("history-conflict");
      }
    });

    // Check each panelist within each debate
    $(".adj", debate_tr).each( function() {
      //console.log(this);
      var adj_adj_conflict_ids = all_adj_conflicts['adjudicator'][adj_id];
      if ($.inArray(DOMIdtoInt(this), adj_adj_conflict_ids) != -1) {
        if (DOMIdtoInt(this) != adj_id) { // Can't conflict self
          // Check if any of the panelists are conflicted with each other
          $(this).addClass("adjudicator-conflict");
          $(adj).addClass("adjudicator-conflict");
        }
      }
    });
  });

  // Check for incomplete panels
  if ($(".panel-holder .adj", debate_tr).length % 2 != 0) {
    console.log('incomplete');
    $(".panel-holder", debate_tr).addClass("panel-incomplete");
  } else {
    $(".panel-holder", debate_tr).removeClass("panel-incomplete");
  }

  // Check for missing chairs
  if ($(".chair-holder .adj", debate_tr).length != 1) {
    console.log('no chair');
    $(".chair-holder", debate_tr).addClass("chair-incomplete");
  } else {
    $(".chair-holder", debate_tr).removeClass("chair-incomplete");
  }

}

// TABLE BEHAVIOURS

$('#allocationsTable .importance select').on('change', function() {
  console.log("change");
  var importance = $("option:selected", this).val(); // or $(this).val()
  var cell = $(this).parent()
  var row = $(this).parent().parent();
  var debate_id = DOMIdtoInt(row);
  $.ajax({
    type: "POST",
    url: "{% round_url update_debate_importance %}",
    data: { debate_id: debate_id, value: importance },
  });
  var adjacent = allocationsTable.cell(cell.siblings(".importance-recording"));
  // adjacent.data(importance).draw(); // Buggy - breaks the change event
})

$('#auto_allocate').click(function() {
  var btn = $(this)
  btn.button('loading')

  $.ajax({
    type: "POST",
    url: "{% round_url create_adj_allocation %}",
    success: function(data, status) {
      reset();
      load_allocation_data($.parseJSON(data));
      update_all_conflicts();
      append_adj_scores();
      $('#loading').hide();
      btn.button('reset')
    },
    error: function(xhr, error, ex) {
      $("#alerts-holder").html('<div class="alert alert-danger alert-dismissable" id=""><button type="button" class="close" data-dismiss="alert">&times;</button>Auto-allocation failed! '
        + xhr.responseText + ' (' + xhr.status + ')</div>');
      $(this).button('reset');
      btn.button('reset')
    }
  });
});

$('#save').click( function() {
  var btn = $(this)
  btn.button('loading')
  var data = {};

  $("#allocationsTable tbody tr").each( function() {
    var debateId = DOMIdtoInt(this); // Purpose of the value is to ID this debate as being saved, so if following values are blank it is still processed
    data['debate_' + debateId] = true;
    $(".chair-holder .adj", this).each( function() {
      data['chair_' + debateId] = DOMIdtoInt(this);
    });
    data['panel_' + debateId]  = [];
    $(".panel-holder .adj", this).each( function() {
      data['panel_' + debateId].push(DOMIdtoInt(this));
    });
    data['trainees_' + debateId]  = [];
    $(".trainee-holder .adj", this).each( function() {
      data['trainees_' + debateId].push(DOMIdtoInt(this));
    });
  });

  $.ajax( {
    type: "POST",
    url: "{% round_url save_adjudicators %}",
    data: data,
    success: function(data, status) {
      btn.button('reset')
      $("#alerts-holder").html('<div class="alert alert-success alert-dismissable" id=""><button type="button" class="close" data-dismiss="alert">&times;</button>Saved successfully!</div>');
    },
    error: function(xhr, error, ex) {
      btn.button('reset')
      $("#alerts-holder").html('<div class="alert alert-danger alert-dismissable" id=""><button type="button" class="close" data-dismiss="alert">&times;</button>Saved failed!</div>');
    }
  });

  return false;
});


// UI INITIALISATION FUNCTIONS

function init_adj(el) {

  el.mouseover( function(e) {
    display_conflicts(e.currentTarget);
  });

  el.mouseout( function(e) {
    remove_conflicts(e.currentTarget);
  });

  el.draggable({
    containment: "body", // bounds that limit dragging area
    revert: 'invalid',
    appendTo: "#helper_holder", // append helper to element with highest z-index
    helper: function() {
      this.oldHolder = $(this).parent("td");
      var adj = $(this).clone();
      return adj;
    },
    start: function(event, ui) {
      // We want to keep showing conflicts during drag, so we unbind the event
      display_conflicts(event.currentTarget);
      $(event.currentTarget).unbind('mouseover mouseout');
      draggingCurrently = true;
    },
    stop: function(event, ui) {
      target_id = $("#" + ui.helper.attr("id"));
      $(ui.helper).remove();
      draggingCurrently = false;
      update_all_conflicts(); // Update to account for new/resolved conflicts
    }
  });
}

$("#scratch").droppable( {
  accept: '.adj',
  hoverClass: 'bg-success',
  drop: function(event, ui) {
    var adj = ui.draggable;
    moveToUnused(adj);
    remove_conflicts(adj);
  }
});

$("#allocationsTable .adj-holder").droppable( {
  hoverClass: 'bg-info',
  drop: function(event, ui) {
    var adj = ui.draggable; // The adj being dragged
    var oldHolder = adj[0].oldHolder; // Where the element came from
    var destinationAdjs = $(".adj", this); // Any adjs present in the drop destination

    if ($(this).hasClass("chair-holder")) {
      // Swap the two around if dropping into a single position
      oldHolder.append(destinationAdjs);
    }
    if (!oldHolder.hasClass("adj-holder")) {
      // If placing from the unused column
      removeUnusedRow(oldHolder);
    }

    $(this).append(adj);
    rebindHoverEvents($(adj));
  }
});


// ALLOCATION MANIPULATION FUNCTIONS

function _make_adj(data) {
  var gender_class = ""
  if (data["gender"] == "M") {
    gender_class = "male";
  } else if (data["gender"] == "F") {
    gender_class = "female";
  }
  var adj = $('<div></div>')
    .addClass('adj btn btn-block')
    .addClass(gender_class)
    .addClass(data["region"])
    .attr('id', 'adj_' + data.id)
    .append($('<span></span> ').html(data.name));
  init_adj(adj);
  return adj;
}

function set_chair(debate_id, data) {
  var td = $('#chair_'+debate_id);
  removeUnusedRow(td)
  $('div.adj', td).remove();
  _make_adj(data).appendTo(td);
}

function clear_panel(debate_id) {
  $('#panel_'+debate_id).find('div.adj').remove();
}

function clear_trainees(debate_id) {
  $('#trainees_'+debate_id).find('div.adj').remove();
}

function add_panellist(debate_id, data) {
  var td = $('#panel_'+debate_id);
  removeUnusedRow(td)
  _make_adj(data).appendTo(td);
}

function add_trainee(debate_id, data) {
  var td = $('#trainees_'+debate_id);
  removeUnusedRow(td)
  _make_adj(data).appendTo(td);
}

function moveToUnused(adj) {
  // Build a list of all adjs already on the table
  var unusedIDs = [];
  $("#unusedAdjTable .adj").each(function(){
    unusedIDs.push(DOMIdtoInt(this));
  });
  var moving_adj_id = DOMIdtoInt(adj);

  if (unusedIDs.indexOf(moving_adj_id) == -1) {
    // If the adj isn't already in the table
    var new_row = unusedAdjTable.row.add( ["",formatScore(all_adj_scores[moving_adj_id])] ).draw(); // Adds a new row
    var first_cell = $("td:first", new_row.node()).append(adj); // Append the adj element
  } else {
    // Adj is already in the table (probably just be dragging back)
  }

}

// INITIALISATION VARIABLES

// Dictionary matching scores to adj_id, ie 279:5
var all_adj_scores;

// A list of bjects for each conflict type. Each has a list of Adj IDs with an array of conflict IDs
var all_adj_conflicts;

var conflictTypeClass = {
  'personal': 'personal-conflict',
  'institutional': 'institutional-conflict',
  'history': 'history-conflict',
  'adjudicator': 'adjudicator-conflict',
}

// Global dragging variable; to stop highlights on other teams being shown while dragging
var draggingCurrently = false;

// DATATABLE INITIALISATION

var allocationsTable = $("#allocationsTable").DataTable( {
  "bAutoWidth": false,
  "aoColumns": [
    { "sWidth": "3%" },
    { "sWidth": "0%" },
    { "sWidth": "3%" },
    { "sWidth": "3%" },
    { "sWidth": "3%" },
    { "sWidth": "3%" },
    { "sWidth": "17%" },
    { "sWidth": "3%" },
    { "sWidth": "3%" },
    { "sWidth": "17%" },
    { "sWidth": "18%" },
    { "sWidth": "18%" },
    { "sWidth": "18%" }
  ],
  "aaSorting": [[1, 'desc']],
  "aoColumnDefs": [
    { "bVisible": false, "aTargets": [3,4,5,7,8] }, //set column visibility
    {"iDataSort": 1, "aTargets": [2] },
    { "bVisible": false, "aTargets": [1] },
  ]
});

var unusedAdjTable = $("#unusedAdjTable").DataTable({
  aoColumns: [
    { "sWdith": "90%", "sType": "string" },
    { "sWidth": "10%", "sType": "string" }
  ],
  "aaSorting": [[1, 'desc'], [0, 'desc']],
  "aoColumnDefs": [
    // Sort based on feedback despite it being a hidden column
    {"iDataSort": 1, "aTargets": [0] },
    { "bVisible": false, "aTargets": [1] },
  ],
  "autoWidth": false,
  bFilter: false,
})

// Setup feedback popover
var adjFeedbackModalTable = $("#modal-adj-table").DataTable({
  {% if adj0.id %}
  'ajax': '{% tournament_url get_adj_feedback %}?id={{ adj0.id }}',
  {% endif %}
  'bPaginate': false,
  'bFilter': false
});
$('#table-search').keyup(function(){
  adjFeedbackModalTable.search($(this).val()).draw();
})

// ALLOCATION INITIALISATION

load_adjudicator_scores(function() {
  // The below function is the callback to be executed after load_adjudicator_scores()
  load_allocation(function() {
    append_adj_scores();
    load_conflict_data();
  });
});
