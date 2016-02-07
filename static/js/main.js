
jQuery.extend( true, $.fn.dataTable.defaults, {
  // Default Data Table options
  "sDom":
    "<'row'<'table-container'lr"+ // f = the filter
    "t"+
    "f<p>",
  "bPaginate": false,
  "oLanguage": {
    "sSearch": "Search: "
  }
});

$(document).ready(function(){

  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    'html': true,
    'placement': 'bottom'
  });
  // Disable buttons post submission
  $('.submit-disable').on('click', function () {
    var $btn = $(this).button('loading');
  });
  // Enable AJAX-based hover tooltips to lookup speaker names
  // $('.team-speakers-hover').tooltip({
  //   title: getTeamSpeakers,
  //   'html': true,
  //   'placement': 'bottom'
  // });
  // Dynamic lookup speakers on hover
  var cachedData = Array();
  function getTeamSpeakers(){
      var element = $(this);
      var id = element.attr('id').replace("team_speakers_", "");
      if(id in cachedData){
          return cachedData[id];
      }
      var localData = "error";
      $.ajax('{{ tournament.get_public_url  }}participants/team_list/' + id + '/', {
          async: false,
          success: function(data){
              localData = data[0] + ", " + data[1] + ", " + data[2];
          }
      });
      cachedData[id] = localData;
      return localData;
  }
});
