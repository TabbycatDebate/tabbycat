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


    $("#tiny_text").click(function(event){
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        $( "#draw" ).removeClass( "h1 h2 h3 h4_plus h4 h4_minus h5 h6" ).addClass( "h5" );
        return false;
    });
    $("#small_text").click(function(event){
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        $( "#draw" ).removeClass( "h1 h2 h3 h4_plus h4 h4_minus h5 h6" ).addClass( "h4_minus" );
        return false;
    });
    $("#medium_text").click(function(event){
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        $( "#draw" ).removeClass( "h1 h2 h3 h4_plus h4 h4_minus h5 h6" ).addClass( "h4" );
        return false;
    });
    $("#large_text").click(function(event){
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        $( "#draw" ).removeClass( "h1 h2 h3 h4_plus h4 h4_minus h5 h6" ).addClass( "h4_plus" );
        return false;
    });
    $("#huge_text").click(function(event){
        $(this).siblings().removeClass("active");
        $(this).addClass("active");
        $( "#draw" ).removeClass( "h1 h2 h3 h4_plus h4 h4_minus h5 h6" ).addClass( "h3" );
        return false;
    });
});
$(document).keydown(function(e) {
    e.stopPropagation();
    if (e.keyCode === 27 || e.keyCode === 38) {
        $('html, body').stop()
    }
});