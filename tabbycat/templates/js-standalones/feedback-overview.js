
// Actions for the table elements
$(document).ready(function(){

  $(".edit-test-score a").each( function() {
    $(this).click( function() {
      var adj_id = parseInt($(this).attr("data-target"));
      var adj_score = $(this, "span").text();
      $("#id_adj_id").val(adj_id); // Updating form ID reference
      $("#id_test_score").prop('placeholder', adj_score); // updating the form's table
      $('#edit-test-score').modal();
    });
  });

  $(".edit-note a").each( function() {
    $(this).click( function() {
      var adj_id = parseInt($(this).attr("data-target").split("===")[0]);
      var adj_note = $(this).attr("data-target").split("===")[1];
      $("#id_note").val(adj_note);
      $("#id_adj_id_note").val(adj_id);
      $('#edit-note').modal();
    });
  });

  $(".toggle_breaking_status input").each(function() {
    $(this).change( function() {
      var adj_id = parseInt($(this).attr("adj_id"));
      var breaking_status = null;
      if (this.checked) {
        breaking_status = true;
        $("#breaking_count").html(parseInt($('#breaking_count').html(), 10)+1);
      } else {
        breaking_status = false;
        $("#breaking_count").html(parseInt($('#breaking_count').html(), 10)-1);
      }
      $.ajax({
        type: "POST",
        url: setBreakingURL,
        data: {adj_id: adj_id, adj_breaking_status: breaking_status},
        error: function(xhr, error, ex) {
          alert("error setting adj status");
        }
      });
      return false;
    });
  });

});
