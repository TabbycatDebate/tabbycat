$(document).ready( function() {
        var emoji_arr = [];
        $.getJSON('/emoji/all.json', function(data) {
        for (var i in data) {
            //console.log(data[i]);
            emoji_arr.push(data[i]);
        }
        $(".team-emoji").each(function(index) {
            var emojiID = $(this).attr("class").replace('team-emoji team-', '');
            $(this).append('<img src="' + emoji_arr[parseInt(emojiID)] + '" />');
        });
    });
});