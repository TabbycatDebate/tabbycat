

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    var v=(n != 1);
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  var newcatalog = {
    "%1 %2 from %3": "crwdns34816:0%1crwdnd34816:0%2crwdnd34816:0%3crwdne34816:0",
    "%1 %2 from %3 %4": "crwdns34818:0%1crwdnd34818:0%2crwdnd34818:0%3crwdnd34818:0%4crwdne34818:0",
    "%1 %2 from %3 on %4 (Chair)": "crwdns34820:0%1crwdnd34820:0%2crwdnd34820:0%3crwdnd34820:0%4crwdne34820:0",
    "%1 %2 from %3 on %4 (Panellist)": "crwdns34822:0%1crwdnd34822:0%2crwdnd34822:0%3crwdnd34822:0%4crwdne34822:0",
    "%1 %2 from %3 on %4 (Trainee)": "crwdns34824:0%1crwdnd34824:0%2crwdnd34824:0%3crwdnd34824:0%4crwdne34824:0",
    "%1 (%2) with identifier of %3": "crwdns34804:0%1crwdnd34804:0%2crwdnd34804:0%3crwdne34804:0",
    "%1 (%2) with no assigned identifier": "crwdns34808:0%1crwdnd34808:0%2crwdne34808:0",
    "%1 (%2, %3)": "crwdns34886:0%1crwdnd34886:0%2crwdnd34886:0%3crwdne34886:0",
    "%1 (Absent; id=%2)": "crwdns34790:0%1crwdnd34790:0%2crwdne34790:0",
    "%1 (Present; id=%2)": "crwdns34788:0%1crwdnd34788:0%2crwdne34788:0",
    "%1 (no category) with identifier of %2": "crwdns34806:0%1crwdnd34806:0%2crwdne34806:0",
    "%1 (no category) with no assigned identifier": "crwdns34810:0%1crwdne34810:0",
    "%1 checked in %2: %3": "crwdns34752:0%1crwdnd34752:0%2crwdnd34752:0%3crwdne34752:0",
    "%1, %2": "crwdns34908:0%1crwdnd34908:0%2crwdne34908:0",
    "%1, a %2": "crwdns34794:0%1crwdnd34794:0%2crwdne34794:0",
    "%1, a %2 from %3 with identifier of %4": "crwdns34784:0%1crwdnd34784:0%2crwdnd34784:0%3crwdnd34784:0%4crwdne34784:0",
    "%1, a %2 from %3 with no assigned identifier": "crwdns34786:0%1crwdnd34786:0%2crwdnd34786:0%3crwdne34786:0",
    "%1, a %2 of no institutional affiliation with identifier of %3": "crwdns34780:0%1crwdnd34780:0%2crwdnd34780:0%3crwdne34780:0",
    "%1, a %2 of no institutional affiliation with no assigned identifier": "crwdns34782:0%1crwdnd34782:0%2crwdne34782:0",
    "%1, a team with speakers %2": "crwdns34792:0%1crwdnd34792:0%2crwdne34792:0",
    "%1:": "crwdns34864:0%1crwdne34864:0",
    "; ": "crwdns34890:0crwdne34890:0",
    "<strong>%1</strong>: %2": "crwdns34852:0%1crwdnd34852:0%2crwdne34852:0",
    "<strong>\u2613</strong> All": "crwdns34766:0crwdne34766:0",
    "<strong>\u2713</strong> All": "crwdns34764:0crwdne34764:0",
    "Add Ballot": "crwdns35022:0crwdne35022:0",
    "Adjudicating with %1.": "crwdns34888:0%1crwdne34888:0",
    "Adjudicator Demographics": "crwdns34992:0crwdne34992:0",
    "Adjudicator Results": "crwdns34996:0crwdne34996:0",
    "Aff Veto": "crwdns34854:0crwdne34854:0",
    "All": "crwdns34754:0crwdne34754:0",
    "Anon": "crwdns34798:0crwdne34798:0",
    "Anonymous (due to team codes)": "crwdns34796:0crwdne34796:0",
    "Auto-Allocate": "crwdns35034:0crwdne35034:0",
    "Auto-Prioritise": "crwdns35032:0crwdne35032:0",
    "Ballot Check-Ins": "crwdns35010:0crwdne35010:0",
    "Ballot Statuses": "crwdns35018:0crwdne35018:0",
    "Ballots Status": "crwdns34968:0crwdne34968:0",
    "Break": "crwdns35639:0crwdne35639:0",
    "By %1": "crwdns34756:0%1crwdne34756:0",
    "By how many points did they win:": "crwdns34906:0crwdne34906:0",
    "Category": "crwdns35647:0crwdne35647:0",
    "Chair for Panel of %1": "crwdns34830:0%1crwdne34830:0",
    "Checked-In": "crwdns35006:0crwdne35006:0",
    "Circle %1": "crwdns34850:0%1crwdne34850:0",
    "Circle Rank:": "crwdns34938:0crwdne34938:0",
    "Circle the last digit of the %1's score:": "crwdns34916:0%1crwdne34916:0",
    "Circle the last digit of the team's total:": "crwdns34950:0crwdne34950:0",
    "Click to check-in manually": "crwdns34768:0crwdne34768:0",
    "Click to undo a check-in": "crwdns34778:0crwdne34778:0",
    "Confirmed": "crwdns35016:0crwdne35016:0",
    "Copy From Check-Ins": "crwdns34966:0crwdne34966:0",
    "Debated": "crwdns34848:0crwdne34848:0",
    "Did %1 deliver the adjudication?": "crwdns34892:0%1crwdne34892:0",
    "Find in Table": "crwdns34952:0crwdne34952:0",
    "Gender": "crwdns35641:0crwdne35641:0",
    "ID %1,": "crwdns34826:0%1crwdne34826:0",
    "IMPORTANT: Check and explicitly note if a speaker gives multiple speeches": "crwdns34910:0crwdne34910:0",
    "If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can use the assistant version.": "crwdns34774:0crwdne34774:0",
    "Independent": "crwdns34800:0crwdne34800:0",
    "Latest Actions": "crwdns34970:0crwdne34970:0",
    "Latest Results": "crwdns34974:0crwdne34974:0",
    "Mark replies %1 to %2; <strong>%3</strong>.": "crwdns34842:0%1crwdnd34842:0%2crwdnd34842:0%3crwdne34842:0",
    "Mark speeches %1 to %2; <strong>%3</strong>.": "crwdns34840:0%1crwdnd34840:0%2crwdnd34840:0%3crwdne34840:0",
    "Match": "crwdns34958:0crwdne34958:0",
    "Match Check-Ins": "crwdns34962:0crwdne34962:0",
    "Neg Veto": "crwdns34856:0crwdne34856:0",
    "No": "crwdns34902:0crwdne34902:0",
    "No Actions Yet": "crwdns34972:0crwdne34972:0",
    "No Adjudicator Ratings Information": "crwdns35002:0crwdne35002:0",
    "No Adjudicator-Adjudicator Feedback Information": "crwdns35004:0crwdne35004:0",
    "No Category": "crwdns35637:0crwdne35637:0",
    "No Confirmed Results Yet": "crwdns34976:0crwdne34976:0",
    "No Gender Information": "crwdns34980:0crwdne34980:0",
    "No Position Information": "crwdns34994:0crwdne34994:0",
    "No Region Information": "crwdns34990:0crwdne34990:0",
    "No Speaker Categories Information": "crwdns34982:0crwdne34982:0",
    "No changes": "crwdns35028:0crwdne35028:0",
    "No code name set": "crwdns35064:0crwdne35064:0",
    "No matching people found.": "crwdns34760:0crwdne34760:0",
    "No matching rooms found.": "crwdns51658:0crwdne51658:0",
    "No, I am submitting feedback on:": "crwdns34896:0crwdne34896:0",
    "Not Checked-In": "crwdns35008:0crwdne35008:0",
    "Open the assistant version.": "crwdns34776:0crwdne34776:0",
    "Panellist": "crwdns34834:0crwdne34834:0",
    "Priority %1": "crwdns34814:0%1crwdne34814:0",
    "Rank": "crwdns35643:0crwdne35643:0",
    "Re-Edit": "crwdns35024:0crwdne35024:0",
    "Region": "crwdns35645:0crwdne35645:0",
    "Return ballots to %1.": "crwdns34844:0%1crwdne34844:0",
    "Return to Draw": "crwdns35030:0crwdne35030:0",
    "Review": "crwdns35026:0crwdne35026:0",
    "Room:": "crwdns51660:0crwdne51660:0",
    "Scan Using Camera": "crwdns34746:0crwdne34746:0",
    "Score:": "crwdns34914:0crwdne34914:0",
    "Set All Breaking as Available": "crwdns34954:0crwdne34954:0",
    "Set all availabilities to exactly match check-ins.": "crwdns34960:0crwdne34960:0",
    "Set all the availabilities to exactly match what they were in the previous round.": "crwdns34956:0crwdne34956:0",
    "Set people as available only if they have a check-in and are currently unavailable \u2014 i.e. it will not overwrite any existing availabilities.": "crwdns34964:0crwdne34964:0",
    "Solo Chair": "crwdns34832:0crwdne34832:0",
    "Speaker Demographics": "crwdns34978:0crwdne34978:0",
    "Speaker Results": "crwdns34984:0crwdne34984:0",
    "Stop Camera Scan": "crwdns34748:0crwdne34748:0",
    "Team": "crwdns34838:0crwdne34838:0",
    "The bracket range of the hypothetical debate": "crwdns35056:0crwdne35056:0",
    "The debate's bracket": "crwdns35054:0crwdne35054:0",
    "The estimated total number of live break categories across all teams of the hypothetical debate": "crwdns35060:0crwdne35060:0",
    "The motion is <em>%1</em>": "crwdns34846:0%1crwdne34846:0",
    "The total number of live break categories across all teams": "crwdns35058:0crwdne35058:0",
    "This debate's priority": "crwdns35062:0crwdne35062:0",
    "This page will live-update with new check-ins as they occur although the initial list may be up to a minute old.": "crwdns34762:0crwdne34762:0",
    "This person does not have a check-in identifier so they can't be checked in": "crwdns34772:0crwdne34772:0",
    "Total:": "crwdns34948:0crwdne34948:0",
    "Trainee": "crwdns34836:0crwdne34836:0",
    "Turn On Sounds": "crwdns34750:0crwdne34750:0",
    "Unaffiliated": "crwdns34802:0crwdne34802:0",
    "Uncategorised": "crwdns34812:0crwdne34812:0",
    "Unconfirmed": "crwdns35014:0crwdne35014:0",
    "Unknown": "crwdns35012:0crwdne35012:0",
    "Unsure": "crwdns34900:0crwdne34900:0",
    "Which team won the debate:": "crwdns34904:0crwdne34904:0",
    "Yes": "crwdns34894:0crwdne34894:0",
    "You cannot confirm this ballot because you entered it": "crwdns35020:0crwdne35020:0",
    "adjudicators with gender data": "crwdns34998:0crwdne34998:0",
    "decimal marks are allowed": "crwdns34876:0crwdne34876:0",
    "feedback scores total": "crwdns35000:0crwdne35000:0",
    "no \u00bd marks": "crwdns34872:0crwdne34872:0",
    "saving...": "crwdns34770:0crwdne34770:0",
    "speaker scores total": "crwdns34988:0crwdne34988:0",
    "speakers with gender data": "crwdns34986:0crwdne34986:0",
    "tab check": "crwdns34868:0crwdne34868:0",
    "tab entry": "crwdns34866:0crwdne34866:0",
    "\u00bd marks are allowed": "crwdns34874:0crwdne34874:0"
  };
  for (var key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      var value = django.catalog[msgid];
      if (typeof(value) == 'undefined') {
        return msgid;
      } else {
        return (typeof(value) == 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      var value = django.catalog[singular];
      if (typeof(value) == 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      var value = django.gettext(context + '\x04' + msgid);
      if (value.indexOf('\x04') != -1) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      var value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.indexOf('\x04') != -1) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "N j, Y, P",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M"
    ],
    "DATE_FORMAT": "N j, Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%b %d %Y",
      "%b %d, %Y",
      "%d %b %Y",
      "%d %b, %Y",
      "%B %d %Y",
      "%B %d, %Y",
      "%d %B %Y",
      "%d %B, %Y"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "F j",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "m/d/Y P",
    "SHORT_DATE_FORMAT": "m/d/Y",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "P",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      var value = django.formats[format_type];
      if (typeof(value) == 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }

}(this));

