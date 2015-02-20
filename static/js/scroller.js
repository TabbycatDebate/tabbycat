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
});
$(document).keydown(function(e) {
    e.stopPropagation();
    if (e.keyCode === 27 || e.keyCode === 38) {
        $('html, body').stop()
    }
});