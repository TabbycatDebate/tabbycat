$(document).ready( function() {
    $("#scroll_draw1").click(function(event){
        $('html, body').animate({
            scrollTop: $(document).height() - $(window).height()}, 20000, "linear");
        return false;
    });
    $("#scroll_draw2").click(function(event){
        $('html, body').animate({
            scrollTop: $(document).height() - $(window).height()}, 40000, "linear");
        return false;
    });
    $("#scroll_draw3").click(function(event){
        $('html, body').animate({
            scrollTop: $(document).height() - $(window).height()}, 60000, "linear");
        return false;
    });
});