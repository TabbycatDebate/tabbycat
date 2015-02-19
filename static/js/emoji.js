$(document).ready( function() {
        var emoji_arr = [];
        $.getJSON('/static/js/emoji_list.json', function(data) {
        for (var i in data) {
            //console.log(data[i]);
            emoji_arr.push(data[i]);
        }
        var team_ids = [];
        $(".team-emoji").each(function(index) {
            var emojiID = $(this).attr("class").replace('team-emoji team-', '');
            var ID = parseInt(emojiID);
            team_ids.push(ID); // building an array of team IDS
        });
        team_ids.sort(function(a,b){return a - b})
        console.log(team_ids.length + ' to make emoji');
        console.log(team_ids);
        for (var i = 0; i < team_ids.length; i++) {
            var base_id = team_ids[i] - team_ids[0] // Starting from Emoji[0]
            $(".team-" + team_ids[i]).html('<img src="' + emoji_arr[base_id] + '" />');
        }
    });
});