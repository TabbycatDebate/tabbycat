// When using anonymous speaker names prepopulate the form to save time
aff_speakers = $("#id_aff_speaker_s1 option").text();
neg_speakers = $("#id_neg_speaker_s1 option").text();
if (aff_speakers.indexOf("Speaker 1") != -1 && neg_speakers.indexOf("Speaker 1") != -1) {
  $("div.aff.s1").find("select :nth-child(2)").prop('selected', true);
  $("div.aff.s2").find("select :nth-child(3)").prop('selected', true);
  $("div.aff.s3").find("select :nth-child(4)").prop('selected', true);
  $("div.aff.s4").find("select :nth-child(5)").prop('selected', true);
  $("div.neg.s1").find("select :nth-child(2)").prop('selected', true);
  $("div.neg.s2").find("select :nth-child(3)").prop('selected', true);
  $("div.neg.s3").find("select :nth-child(4)").prop('selected', true);
  $("div.neg.s4").find("select :nth-child(5)").prop('selected', true);
}

function refresh_totals(scoresheet) {

  $scoresheet = $(scoresheet);

  // Fix the branching logic here into something cleaner
  var allClasses = 'btn-dark btn-secondary btn-success btn-primary btn-warning btn-danger btn-info';

  if ("{{ pref.teams_in_debate }}" == 2) {
    // 2-team
    $aff_total = $('.0_total', $scoresheet);
    $neg_total = $('.1_total', $scoresheet);
    $aff_rank = $('.0_rank', $scoresheet);
    $neg_rank = $('.1_rank', $scoresheet);
    $aff_margin = $('.0_margin', $scoresheet);
    $neg_margin = $('.1_margin', $scoresheet);
    if ($('.criterion', $scoresheet).length) {
      for (const side of [0, 1]) {
        for (const speaker of [...$(`.side-${side}.score`, $scoresheet)]) {
          const criteria = $('.criterion input', speaker);
          var weighted = 0;
          criteria.each((i, c) => {weighted += c.value * c.attributes.weight.value})
          speaker.querySelector('input.total').value = weighted;
        }
      }
    }
    var aff = sum($('.side-0.score input.total', $scoresheet));
    var neg = sum($('.side-1.score input.total', $scoresheet));
    $aff_total.text(aff);
    $neg_total.text(neg);

    $aff_rank.removeClass(allClasses);
    $neg_rank.removeClass(allClasses);
    if (aff > neg) {
      $aff_rank.addClass('btn-success');
      $neg_rank.addClass('btn-danger');
      $aff_rank.text('Won');
      $neg_rank.text('Lost');
      $aff_margin.text("+" + Number(aff - neg));
      $neg_margin.text(Number(neg - aff));
    } else if (neg > aff) {
      $aff_rank.addClass('btn-danger');
      $neg_rank.addClass('btn-success');
      $aff_rank.text('Lost');
      $neg_rank.text('Won');
      $aff_margin.text(Number(aff - neg));
      $neg_margin.text("+" + Number(neg - aff));
    } else {
      $aff_rank.addClass('btn-dark');
      $neg_rank.addClass('btn-dark');
      $aff_rank.text('Tie');
      $neg_rank.text('Tie');
      $aff_margin.text(Number(aff - neg));
      $neg_margin.text(Number(neg - aff));
    }
  } else {
    // BP
    var totals_elements = []
    var margins_elements = []
    var total_scores = []
    var rank_elements = []

    for (var i = 0; i < $('.scoresheet > div').length; i++) {
      totals_elements[i] = $('.' + i + '_total', $scoresheet);
      margins_elements[i] = $('.' + i + '_margin', $scoresheet);
      rank_elements[i] = $('.' + i + '_rank', $scoresheet);
      if ($('.criterion', $scoresheet).length) {
        for (const speaker of [...$(`.${i}.score`, $scoresheet)]) {
          const criteria = $('.criterion input', speaker);
          var weighted = 0;
          criteria.each((i, c) => {weighted += c.value * c.attributes.weight.value})
          speaker.querySelector('input.total').value = weighted;
        }
      }
      var team_total = sum($(`.side-${i}.score input.total`, $scoresheet));
      // Update totals scores only if both speaker scores have been entered
      if (team_total > 99) {
        total_scores[i] = team_total
        totals_elements[i].text(total_scores[i]);
      }
    }

    // Create new dict with total scores sorted high-low
    var sortedScores = total_scores.map(function(val, i) {
      return [i, val];
    });
    sortedScores.sort(function(first, second) {
      return second[1] - first[1];
    });

    // Use sorted dictionary to assign relative margins and win indicators
    for (var i = 0; i < sortedScores.length; i++) {

      var team = sortedScores[i][0];
      if (total_scores[team] === 0) { continue }

      // Add winning class indicators; but not if there was a tie
      var tie = false;
      for (var j = 0; j < sortedScores.length; j++) {
        if (j === i) { continue }
        tie ||= total_scores[team] === total_scores[sortedScores[j][0]];
      }

      rank_elements[team].removeClass(allClasses);
      rank_elements[team].text("?");
      if (!tie && sortedScores.length > 3) {
        const btn_classes = ['btn-success', 'btn-info', 'btn-warning', 'btn-danger'];
        const ordinals = ['1st', '2nd', '3rd', '4th'];
        rank_elements[team].addClass(btn_classes[i]);
        rank_elements[team].text(ordinals[i]);
      } else if (tie) {
        rank_elements[team].addClass('btn-dark');
        rank_elements[team].text("TIE");
      } else {
        rank_elements[team].addClass('btn-secondary');
      }

      // Display margin
      var top_score = total_scores[sortedScores[0][0]];
      var margin = String(top_score - total_scores[team]);
      if (margin !== "0") {
        margin = "-" + margin
      }
      margins_elements[team].text(margin);
    }
  }


}

function sum(elems) {
  var r = 0;
  elems.each(function(){
    var p = parseFloat($(this).val());
    if (p > 0) r += p;
  });
  return r;
}

function update_speakers() {
  $('.js-speaker').each(update_speaker);
}

function update_speaker() {
  // e.g. id_aff_speaker_s1
  var parts = $(this).attr('id').split('_');
  var side = parts[1]; // e.g. 'aff'
  var pos = parts[3];  // e.g. 's1'
  var speaker = $(':selected', this).text();

  // Update speaker names for all judges other than the first
  // e.g. '.aff.s1 .speaker-name'
  $('.' + side + '.' + pos + ' .speaker-name').html(speaker);

  var others = [];
  var posno = parseInt(pos.charAt(1));

  {% if form.using_replies %}
    if (posno != {{ form.reply_position }})
      for (var i = 1; i <= {{ form.last_substantive_position }}; i++)
        if (i != posno) others.push(i);
    if (posno == {{ form.last_substantive_position }})
      others.push({{ form.reply_position }});
    if (posno == {{ form.reply_position }})
      others.push({{ form.last_substantive_position }});
  {% elif form.last_substantive_position %}
    for (var i = 1; i <= {{ form.last_substantive_position }}; i++)
      if (i != posno) others.push(i);
  {% else %}
    // If there's no form (ie adj has no debate for this round) do nothing
  {% endif %}

  // Detect duplicates
  var dupe = false;
  $.each(others, function(idx, val) {
    $sel = $('#id_'+side+'_speaker_s'+val);
    if ($(':selected', $sel).text() == speaker) {
      dupe = true;
    };
  });
  if (dupe || speaker === '---------') {
    $(this).addClass('error');
  } else {
    $(this).removeClass('error');
  }

}

$("#resultsForm").validate({
  invalidHandler: function(event, validator) {
    $.fn.resetButton($("#submit", event.target))
  }
});

$('.scoresheet').each(function() {
  refresh_totals($(this));
});
$('.score input').change(function() {
  refresh_totals($(this).parents('.scoresheet'));
});

function checkForfeit() {
  const anyChecked = document.querySelectorAll('input.forfeit-check:checked').length;
  if (anyChecked) {
    [...document.querySelectorAll('.js-speaker,.total')].forEach(el => { el.disabled = true; });
  } else {
    [...document.querySelectorAll('.js-speaker,.total')].forEach(el => { el.disabled = false; });
  }
}

checkForfeit();
[...document.querySelectorAll('input.forfeit-check')].forEach((checkbox) => {
  checkbox.addEventListener('change', checkForfeit);
});

$('.js-team-speakers select').change(update_speakers).each(update_speaker);

// Show/hide on initial input
$( ".iron-person input" ).each(function(index) {
  if ($(this).prop('checked') === true) {
    $("#hasIron").val('1');
    $(".iron-person").show()
  }
});

// Show/hide on toggle
$("#hasIron").change(function() {
  var enabled = $("#hasIron option:selected").val()
  if (enabled === "1") {
    $(".iron-person").show()
  } else if (enabled === "0") {
    $(".iron-person input").prop('checked', false);
    $(".iron-person").hide()
  }
});

{% if form.using_replies and form.last_substantive_position == 2 %}
// Fill in the reply speaker if there is only one option

  $('#id_aff_speaker_s1').change(function() {
    $('#id_aff_speaker_s{{ form.reply_position }}').val($(this).val());
    update_speakers();
  });
  $('#id_neg_speaker_s1').change(function() {
    $('#id_neg_speaker_s{{ form.reply_position }}').val($(this).val());
    update_speakers();
  });

{% endif %}

{% if form.choosing_sides %}

  var team_names = {};
  {% for team in form.debate.teams %}team_names['{{team.id}}'] = '{{team.short_name}}';
  {% endfor %}

  function swap_sides(selected_option) {

      team_ids = selected_option.split(',');
      aff_team_id = team_ids[0];
      neg_team_id = team_ids[1];

      // Copy team names
      $(".aff-team-name").text(team_names[aff_team_id]);
      $(".neg-team-name").text(team_names[neg_team_id]);

      // Take note of speaker positions
      current_speakers = {};
      $(".aff .js-speaker").each(function(index) {
        current_speakers["aff" + index] = $(this).val();
      })
      $(".neg .js-speaker").each(function(index) {
        current_speakers["neg" + index] = $(this).val();
      })

      // Copy speaker positions dropdowns
      $(".aff .js-speaker option").remove();
      $(".aff .js-speaker").each(function(index) {
        $("#id_team_" + aff_team_id + " option").clone().appendTo(this);
        // HACK TODO check for values before assigning
        $(this).val(current_speakers["aff" + index]);
        if (!$(this).val())
          $(this).val(current_speakers["neg" + index]);
      })
      $(".neg .js-speaker option").remove();
      $(".neg .js-speaker").each(function(index) {
        $("#id_team_" + neg_team_id + " option").clone().appendTo(this);
        // HACK TODO check for values before assigning
        $(this).val(current_speakers["neg" + index]);
        if (!$(this).val())
          $(this).val(current_speakers["aff" + index]);
      })

  }

  // On Load
  if ($("#id_choose_sides").val() == "") {
    $(".scoresheet").hide();
  } else {
    $(".sides-before-scores-warning").hide();
    var selected_option = $("#id_choose_sides").val()
    swap_sides(selected_option)
  }

  // On Change
  $('#id_choose_sides').change(function() {
    var selected_option = $("#id_choose_sides").val()
    if (selected_option != "") {
      $(".scoresheet").show();
      $(".sides-before-scores-warning").hide();
      swap_sides(selected_option)
    } else {
      $(".scoresheet").hide();
      $(".sides-before-scores-warning").show();
    }
    update_speakers();
  });

{% endif %}
