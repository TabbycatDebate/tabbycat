

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    var v=0;
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  var newcatalog = {
    "%(sel)s of %(cnt)s selected": [
      "%(cnt)s\u500b\u4e2d%(sel)s\u500b\u9078\u629e"
    ],
    "6 a.m.": "\u5348\u524d 6 \u6642",
    "6 p.m.": "\u5348\u5f8c 6 \u6642",
    "All": "\u3059\u3079\u3066",
    "April": "4\u6708",
    "August": "8\u6708",
    "Available %s": "\u5229\u7528\u53ef\u80fd %s",
    "Break": "\u30d6\u30ec\u30a4\u30af",
    "Cancel": "\u30ad\u30e3\u30f3\u30bb\u30eb",
    "Choose": "\u9078\u629e",
    "Choose a Date": "\u65e5\u4ed8\u3092\u9078\u629e",
    "Choose a Time": "\u6642\u9593\u3092\u9078\u629e",
    "Choose a time": "\u6642\u9593\u3092\u9078\u629e",
    "Choose all": "\u5168\u3066\u9078\u629e",
    "Chosen %s": "\u9078\u629e\u3055\u308c\u305f %s",
    "Click to choose all %s at once.": "\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068\u3059\u3079\u3066\u306e %s \u3092\u9078\u629e\u3057\u307e\u3059\u3002",
    "Click to remove all chosen %s at once.": "\u30af\u30ea\u30c3\u30af\u3059\u308b\u3068\u3059\u3079\u3066\u306e %s \u3092\u9078\u629e\u304b\u3089\u524a\u9664\u3057\u307e\u3059\u3002",
    "Copy From Check-Ins": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u304b\u3089\u30b3\u30d4\u30fc\u3059\u308b",
    "December": "12\u6708",
    "February": "2\u6708",
    "Filter": "\u30d5\u30a3\u30eb\u30bf\u30fc",
    "Hide": "\u975e\u8868\u793a",
    "January": "1\u6708",
    "July": "7\u6708",
    "June": "6\u6708",
    "March": "3\u6708",
    "May": "5\u6708",
    "Midnight": "0\u6642",
    "No": "\u3044\u3044\u3048",
    "No Gender Information": "\u30b8\u30a7\u30f3\u30c0\u30fc\u306b\u95a2\u3059\u308b\u60c5\u5831\u306a\u3057",
    "No Region Information": "\u5730\u57df\u60c5\u5831\u306a\u3057",
    "Noon": "12\u6642",
    "Note: You are %s hour ahead of server time.": [
      "\u30ce\u30fc\u30c8: \u3042\u306a\u305f\u306e\u74b0\u5883\u306f\u30b5\u30fc\u30d0\u30fc\u6642\u9593\u3088\u308a\u3001%s\u6642\u9593\u9032\u3093\u3067\u3044\u307e\u3059\u3002"
    ],
    "Note: You are %s hour behind server time.": [
      "\u30ce\u30fc\u30c8: \u3042\u306a\u305f\u306e\u74b0\u5883\u306f\u30b5\u30fc\u30d0\u30fc\u6642\u9593\u3088\u308a\u3001%s\u6642\u9593\u9045\u308c\u3066\u3044\u307e\u3059\u3002"
    ],
    "November": "11\u6708",
    "Now": "\u73fe\u5728",
    "October": "10\u6708",
    "Remove": "\u524a\u9664",
    "Remove all": "\u3059\u3079\u3066\u524a\u9664",
    "September": "9\u6708",
    "Show": "\u8868\u793a",
    "Team": "\u30c1\u30fc\u30e0",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "\u3053\u308c\u304c\u4f7f\u7528\u53ef\u80fd\u306a %s \u306e\u30ea\u30b9\u30c8\u3067\u3059\u3002\u4e0b\u306e\u30dc\u30c3\u30af\u30b9\u3067\u9805\u76ee\u3092\u9078\u629e\u3057\u30012\u3064\u306e\u30dc\u30c3\u30af\u30b9\u9593\u306e \"\u9078\u629e\"\u306e\u77e2\u5370\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u3001\u3044\u304f\u3064\u304b\u3092\u9078\u629e\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "\u3053\u308c\u304c\u9078\u629e\u3055\u308c\u305f %s \u306e\u30ea\u30b9\u30c8\u3067\u3059\u3002\u4e0b\u306e\u30dc\u30c3\u30af\u30b9\u3067\u9078\u629e\u3057\u30012\u3064\u306e\u30dc\u30c3\u30af\u30b9\u9593\u306e \"\u524a\u9664\"\u77e2\u5370\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u4e00\u90e8\u3092\u524a\u9664\u3059\u308b\u3053\u3068\u304c\u3067\u304d\u307e\u3059\u3002",
    "Today": "\u4eca\u65e5",
    "Tomorrow": "\u660e\u65e5",
    "Type into this box to filter down the list of available %s.": "\u4f7f\u7528\u53ef\u80fd\u306a %s \u306e\u30ea\u30b9\u30c8\u3092\u7d5e\u308a\u8fbc\u3080\u306b\u306f\u3001\u3053\u306e\u30dc\u30c3\u30af\u30b9\u306b\u5165\u529b\u3057\u307e\u3059\u3002",
    "Yes": "\u306f\u3044",
    "Yesterday": "\u6628\u65e5",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "\u64cd\u4f5c\u3092\u9078\u629e\u3057\u307e\u3057\u305f\u304c\u3001\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u5909\u66f4\u306f\u3042\u308a\u307e\u305b\u3093\u3067\u3057\u305f\u3002\u3082\u3057\u304b\u3057\u3066\u4fdd\u5b58\u30dc\u30bf\u30f3\u3067\u306f\u306a\u304f\u3066\u5b9f\u884c\u30dc\u30bf\u30f3\u3092\u304a\u63a2\u3057\u3067\u3059\u304b\u3002",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "\u64cd\u4f5c\u3092\u9078\u629e\u3057\u307e\u3057\u305f\u304c\u3001\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\u3002OK\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u4fdd\u5b58\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u305d\u306e\u5f8c\u3001\u64cd\u4f5c\u3092\u518d\u5ea6\u5b9f\u884c\u3059\u308b\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\u3002",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\u3002\u64cd\u4f5c\u3092\u5b9f\u884c\u3059\u308b\u3068\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u306f\u5931\u308f\u308c\u307e\u3059\u3002",
    "one letter Friday\u0004F": "\u91d1",
    "one letter Monday\u0004M": "\u6708",
    "one letter Saturday\u0004S": "\u571f",
    "one letter Sunday\u0004S": "\u65e5",
    "one letter Thursday\u0004T": "\u6728",
    "one letter Tuesday\u0004T": "\u706b",
    "one letter Wednesday\u0004W": "\u6c34"
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
    "DATETIME_FORMAT": "Y\u5e74n\u6708j\u65e5G:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%Y",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M",
      "%m/%d/%y"
    ],
    "DATE_FORMAT": "Y\u5e74n\u6708j\u65e5",
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
    "MONTH_DAY_FORMAT": "n\u6708j\u65e5",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "Y/m/d G:i",
    "SHORT_DATE_FORMAT": "Y/m/d",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "G:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "Y\u5e74n\u6708"
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

