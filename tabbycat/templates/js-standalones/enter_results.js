
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
  $("select.required.error").removeClass("error");
}

function refresh_totals(scoresheet) {
  $scoresheet = $(scoresheet);
  $aff_total = $('.aff_total', $scoresheet);
  $neg_total = $('.neg_total', $scoresheet);
  $aff_margin = $('.aff_margin', $scoresheet);
  $neg_margin = $('.neg_margin', $scoresheet);

  var aff = sum($('.aff.score input', $scoresheet));
  var neg = sum($('.neg.score input', $scoresheet));
  $aff_total.text(aff);
  $neg_total.text(neg);

  if (aff > neg) {
    $aff_total.addClass('btn-success').removeClass('btn-danger');
    $neg_total.addClass('btn-danger').removeClass('btn-success');
    $aff_margin.text("+" + Number(aff - neg));
    $neg_margin.text(Number(neg - aff));
  } else if (neg > aff) {
    $aff_total.addClass('btn-danger').removeClass('btn-success');
    $neg_total.addClass('btn-success').removeClass('btn-danger');
    $aff_margin.text(Number(aff - neg));
    $neg_margin.text("+" + Number(neg - aff));
  } else {
    $aff_total.addClass('btn-danger').removeClass('btn-success');
    $neg_total.addClass('btn-danger').removeClass('btn-success');
    $aff_margin.text(Number(aff - neg));
    $neg_margin.text(Number(neg - aff));
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
  if (posno != {{ form.REPLY_POSITION }})
    for (var i = 1; i <= {{ form.LAST_SUBSTANTIVE_POSITION }}; i++)
      if (i != posno) others.push(i);
  if (posno == {{ form.LAST_SUBSTANTIVE_POSITION }})
    others.push({{ form.REPLY_POSITION }});
  if (posno == {{ form.REPLY_POSITION }})
    others.push({{ form.LAST_SUBSTANTIVE_POSITION }});
  {% else %}
  for (var i = 1; i <= {{ form.LAST_SUBSTANTIVE_POSITION }}; i++)
    if (i != posno) others.push(i);
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
    $('.submit-disable').button('reset');
  }
});

$('.scoresheet').each(function() {
    refresh_totals($(this));
});
$('.score input').change(function() {
    refresh_totals($(this).parents('.scoresheet'));
});

$('.js-team-speakers select').change(update_speakers).each(update_speaker);

// Fill in the reply speaker if there is only one option
{% if form.using_replies and form.LAST_SUBSTANTIVE_POSITION == 2 %}

  $('#id_aff_speaker_s1').change(function() {
    $('#id_aff_speaker_s{{ form.REPLY_POSITION }}').val($(this).val());
    update_speakers();
  });
  $('#id_neg_speaker_s1').change(function() {
    $('#id_neg_speaker_s{{ form.REPLY_POSITION }}').val($(this).val());
    update_speakers();
  });

{% endif %}

{% if pref.enable_forfeits %}

  function disable_required() {
    $("#ballot_set").find(".form-control").removeClass("required").removeClass("error");
    $("#ballot_set").find(".form-control-parent .number").removeClass("required").removeClass("error");
    $("#ballot_set").find(".form-control").removeClass("required").removeClass("error");
    $("#ballot_set").find(".scoresheet select").attr("disabled", true);
    $("#ballot_set").find(".scoresheet input").attr("disabled", true);
  }

  $("#id_forfeits_0").click(function() {
    disable_required();
  });
  $("#id_forfeits_1").click(function() {
    disable_required();
  });

  if ($("#id_forfeits_0").is(':checked') || $("#id_forfeits_1").is(':checked')) {
    // For when reloading initial form data
    disable_required();
  }

{% endif %}

{% if side_allocations_unknown %}

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
      $(".aff-speaker").each(function(index) {
        current_speakers["aff" + index] = $(this).val();
      })
      $(".neg-speaker").each(function(index) {
        current_speakers["neg" + index] = $(this).val();
      })

      // Copy speaker positions dropdowns
      $(".aff-speaker option").remove();
      $(".aff-speaker").each(function(index) {
        $("#id_team_" + aff_team_id + " option").clone().appendTo(this);
        // HACK TODO check for values before assigning
        $(this).val(current_speakers["aff" + index]);
        if (!$(this).val())
          $(this).val(current_speakers["neg" + index]);
      })
      $(".neg-speaker option").remove();
      $(".neg-speaker").each(function(index) {
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
    $(".adj-ballot .text-warning").hide();
    var selected_option = $("#id_choose_sides").val()
    swap_sides(selected_option)
  }

  // On Change
  $('#id_choose_sides').change(function() {
    var selected_option = $("#id_choose_sides").val()
    if (selected_option != "") {
      $(".scoresheet").show();
      $(".adj-ballot .text-warning").hide();
      swap_sides(selected_option)
    } else {
      $(".scoresheet").hide();
      $(".adj-ballot .text-warning").show();
    }
    update_speakers();
  });

{% endif %}

{% if ballotsub.submitter_type == ballotsub.SUBMITTER_PUBLIC %}
  function preSubmit() {
      $('#ballot_set input').removeAttr('readonly');
      $('#ballot_set select').removeAttr('disabled');
  }
  // $('#ballot_set input[type="number"]').attr('readonly', 'true');
  // $('#ballot_set select').attr('disabled', 'true');
  $('#submit').click(function() {
      preSubmit();
  });
{% endif %}
