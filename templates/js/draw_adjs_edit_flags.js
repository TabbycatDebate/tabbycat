{% load debate_tags %}
{% load staticfiles %}

// UI BEHAVIOURS

// Toggling the unused column from horizontal to vertical arrangements
$('#toggle_unused_layout').click(function() {
  if ($('#scratch').hasClass("fixed-right")) {
    $('#scratch').removeClass("fixed-right").addClass("fixed-bottom");
    $('#main').removeClass("col-xs-10").addClass("col-xs-2");
  } else {
    $('#scratch').removeClass("fixed-bottom").addClass("fixed-right");
    $('#main').addClass("col-xs-10").removeClass("col-xs-2");
  }
  return false
});

$('#toggle_gender').click(function() {
  var columnA = allocationsTable.column(5);
  columnA.visible( ! columnA.visible() );
  var columnB = allocationsTable.column(8);
  columnB.visible( ! columnB.visible() );
  $(".adj").toggleClass("gender-display");
  $(".gender-highlight").toggleClass("gender-display");
  $("span", this).toggleClass("glyphicon-eye-open").toggleClass("glyphicon-eye-close");

  $("#conflict_key").toggle();
  $("#gender_key").toggle();
  return false
});

$('#toggle_region').click(function() {
  $("span", this).toggleClass("glyphicon-eye-open").toggleClass("glyphicon-eye-close");

  $(".teaminfo").toggleClass("region-display");
  $(".adj").toggleClass("region-display");
  $("#conflict_key").toggle();
  $("#region_key").toggle();
  return false
});

$('#toggle_breakcategory').click(function() {
  $("span", this).toggleClass("glyphicon-eye-open").toggleClass("glyphicon-eye-close");

  $(".teaminfo").toggleClass("breakcategory-display");
  $("#conflict_key").toggle();
  $("#breakcategory_key").toggle();
  return false
});

$('#toggle_venues').click(function() {
  var venuesColumn = allocationsTable.column(3);
  venuesColumn.visible( ! venuesColumn.visible() );
  $("span", this).toggleClass("glyphicon-eye-open").toggleClass("glyphicon-eye-close");
  return false
});

$('#toggle_wins').click(function() {
  var affWinsColumn = allocationsTable.column(4);
  affWinsColumn.visible( ! affWinsColumn.visible() );
  var negWinsColumn = allocationsTable.column(7);
  negWinsColumn.visible( ! negWinsColumn.visible() );
  $("span", this).toggleClass("glyphicon-eye-open").toggleClass("glyphicon-eye-close");
  return false
})

