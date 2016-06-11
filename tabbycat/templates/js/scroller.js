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
    $(this).addClass("active").siblings().removeClass("active");;
    $(".table").removeClass( "draw-xs draw-s draw-m draw-l draw-xl" ).addClass( "draw-xs" );
    return false;
  });
  $("#small_text").click(function(event){
    $(this).addClass("active").siblings().removeClass("active");;
    $(".table").removeClass( "draw-xs draw-s draw-m draw-l draw-xl" ).addClass( "draw-s" );
    return false;
  });
  $("#medium_text").click(function(event){
    $(this).addClass("active").siblings().removeClass("active");;
    $(".table").removeClass( "draw-xs draw-s draw-m draw-l draw-xl" ).addClass( "draw-m" );
    return false;
  });
  $("#large_text").click(function(event){
    $(this).addClass("active").siblings().removeClass("active");;
    $(".table").removeClass( "draw-xs draw-s draw-m draw-l draw-xl" ).addClass( "draw-l" );
    return false;
  });
  $("#huge_text").click(function(event){
    $(this).addClass("active").siblings().removeClass("active");;
    $(".table").removeClass( "draw-xs draw-s draw-m draw-l draw-xl" ).addClass( "draw-xl" );
    return false;
  });

});

$(document).keydown(function(e) {
  e.stopPropagation();
  if (e.keyCode === 27 || e.keyCode === 38) {
    $('html, body').stop()
  }
});
