$(document).ready( function() {

  $("#scroll_draw1").click(function(event){
    $('html, body').animate({
      scrollTop: $(document).height() - $(window).height()}, 40000, "linear");
    return false;
  });
  $("#scroll_draw2").click(function(event){
    $('html, body').animate({
      scrollTop: $(document).height() - $(window).height()}, 80000, "linear");
    return false;
  });
  $("#scroll_draw3").click(function(event){
    $('html, body').animate({
      scrollTop: $(document).height() - $(window).height()}, 120000, "linear");
    return false;
  });
  $("#scroll_draw4").click(function(event){
    $('html, body').animate({
      scrollTop: $(document).height() - $(window).height()}, 160000, "linear");
    return false;
  });
  $("#scroll_draw5").click(function(event){
    $('html, body').animate({
      scrollTop: $(document).height() - $(window).height()}, 200000, "linear");
    return false;
  });

  $("#tiny_text").click(function(event){
    $(this).siblings().removeClass("active");
    $(this).addClass("active");
    $("#draw").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h4" );
    $(".fixedHeader table").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h4" );
    return false;
  });
  $("#small_text").click(function(event){
    $(this).siblings().removeClass("active");
    $(this).addClass("active");
    $("#draw").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h3_minus" );
    $(".fixedHeader table").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h3_minus" );
    return false;
  });
  $("#medium_text").click(function(event){
    $(this).siblings().removeClass("active");
    $(this).addClass("active");
    $("#draw").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h3" );
    $(".fixedHeader table").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h3" );
    return false;
  });
  $("#large_text").click(function(event){
    $(this).siblings().removeClass("active");
    $(this).addClass("active");
    $("#draw").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h3_plus" );
    $(".fixedHeader table").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h3_plus" );
    return false;
  });
  $("#huge_text").click(function(event){
    $(this).siblings().removeClass("active");
    $(this).addClass("active");
    $("#draw").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h2" );
    $(".fixedHeader table").removeClass( "h1 h2 h3 h3_plus h4 h3_minus h5 h6" ).addClass( "h2" );
    return false;
  });
});

$(document).keydown(function(e) {
  e.stopPropagation();
  if (e.keyCode === 27 || e.keyCode === 38) {
    $('html, body').stop()
  }
});