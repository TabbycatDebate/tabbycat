

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(count) { return (count == 1) ? 0 : 1; };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  var newcatalog = {
    "%(sel)s of %(cnt)s selected": [
      "\u0412\u044b\u0431\u0440\u0430\u043d %(sel)s \u0438\u0437 %(cnt)s",
      "\u0412\u044b\u0431\u0440\u0430\u043d\u043e %(sel)s \u0438\u0437 %(cnt)s"
    ],
    "6 a.m.": "6 \u0443\u0442\u0440\u0430",
    "6 p.m.": "6 \u0432\u0435\u0447\u0435\u0440\u0430",
    "Add": "\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c",
    "April": "\u0410\u043f\u0440\u0435\u043b\u044c",
    "August": "\u0410\u0432\u0433\u0443\u0441\u0442",
    "Available %s": "\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0435 %s",
    "Cancel": "\u041e\u0442\u043c\u0435\u043d\u0430",
    "Choose": "\u0412\u044b\u0431\u0440\u0430\u0442\u044c",
    "Choose a Date": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0430\u0442\u0443",
    "Choose a Time": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0432\u0440\u0435\u043c\u044f",
    "Choose a time": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0432\u0440\u0435\u043c\u044f",
    "Choose all": "\u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435",
    "Chosen %s": "\u0412\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0435 %s",
    "Click to choose all %s at once.": "\u041d\u0430\u0436\u043c\u0438\u0442\u0435, \u0447\u0442\u043e\u0431\u044b \u0432\u044b\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435 %s \u0441\u0440\u0430\u0437\u0443.",
    "Click to remove all chosen %s at once.": "\u041d\u0430\u0436\u043c\u0438\u0442\u0435 \u0447\u0442\u043e\u0431\u044b \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u0441\u0435 %s \u0441\u0440\u0430\u0437\u0443.",
    "December": "\u0414\u0435\u043a\u0430\u0431\u0440\u044c",
    "Delete": "\u0423\u0434\u0430\u043b\u0438\u0442\u044c",
    "February": "\u0424\u0435\u0432\u0440\u0430\u043b\u044c",
    "Filter": "\u0424\u0438\u043b\u044c\u0442\u0440",
    "General": "\u041e\u0431\u0449\u0435\u0435",
    "Hide": "\u0421\u043a\u0440\u044b\u0442\u044c",
    "January": "\u042f\u043d\u0432\u0430\u0440\u044c",
    "July": "\u0418\u044e\u043b\u044c",
    "June": "\u0418\u044e\u043d\u044c",
    "March": "\u041c\u0430\u0440\u0442",
    "May": "\u041c\u0430\u0439",
    "Midnight": "\u041f\u043e\u043b\u043d\u043e\u0447\u044c",
    "Noon": "\u041f\u043e\u043b\u0434\u0435\u043d\u044c",
    "Note: You are %s hour ahead of server time.": [
      "\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435: \u0412\u0430\u0448\u0435 \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u043e\u043f\u0435\u0440\u0435\u0436\u0430\u0435\u0442 \u0432\u0440\u0435\u043c\u044f \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u043d\u0430 %s \u0447\u0430\u0441.",
      "\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435: \u0412\u0430\u0448\u0435 \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u043e\u043f\u0435\u0440\u0435\u0436\u0430\u0435\u0442 \u0432\u0440\u0435\u043c\u044f \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u043d\u0430 %s \u0447\u0430\u0441\u0430."
    ],
    "Note: You are %s hour behind server time.": [
      "\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435: \u0412\u0430\u0448\u0435 \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u043e\u0442\u0441\u0442\u0430\u0451\u0442 \u043e\u0442 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u043d\u0430 %s \u0447\u0430\u0441.",
      "\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435: \u0412\u0430\u0448\u0435 \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e\u0435 \u0432\u0440\u0435\u043c\u044f \u043e\u0442\u0441\u0442\u0430\u0451\u0442 \u043e\u0442 \u0432\u0440\u0435\u043c\u0435\u043d\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u0430 \u043d\u0430 %s \u0447\u0430\u0441\u0430."
    ],
    "November": "\u041d\u043e\u044f\u0431\u0440\u044c",
    "Now": "\u0421\u0435\u0439\u0447\u0430\u0441",
    "October": "\u041e\u043a\u0442\u044f\u0431\u0440\u044c",
    "Remove": "\u0423\u0434\u0430\u043b\u0438\u0442\u044c",
    "Remove all": "\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0432\u0441\u0435",
    "September": "\u0421\u0435\u043d\u0442\u044f\u0431\u0440\u044c",
    "Show": "\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "\u042d\u0442\u043e \u0441\u043f\u0438\u0441\u043e\u043a \u0432\u0441\u0435\u0445 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0445 %s. \u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0432\u044b\u0431\u0440\u0430\u0442\u044c \u043d\u0435\u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0438\u0437 \u043d\u0438\u0445, \u0432\u044b\u0434\u0435\u043b\u0438\u0432 \u0438\u0445 \u0432 \u043f\u043e\u043b\u0435 \u043d\u0438\u0436\u0435 \u0438 \u043a\u043b\u0438\u043a\u043d\u0443\u0432 \"\u0412\u044b\u0431\u0440\u0430\u0442\u044c\", \u043b\u0438\u0431\u043e \u0434\u0432\u043e\u0439\u043d\u044b\u043c \u0449\u0435\u043b\u0447\u043a\u043e\u043c.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "\u042d\u0442\u043e \u0441\u043f\u0438\u0441\u043e\u043a \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0445 %s. \u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0443\u0434\u0430\u043b\u0438\u0442\u044c \u043d\u0435\u043a\u043e\u0442\u043e\u0440\u044b\u0435 \u0438\u0437 \u043d\u0438\u0445, \u0432\u044b\u0434\u0435\u043b\u0438\u0432 \u0438\u0445 \u0432 \u043f\u043e\u043b\u0435 \u043d\u0438\u0436\u0435 \u0438 \u043a\u043b\u0438\u043a\u043d\u0443\u0432 \"\u0423\u0434\u0430\u043b\u0438\u0442\u044c\", \u043b\u0438\u0431\u043e \u0434\u0432\u043e\u0439\u043d\u044b\u043c \u0449\u0435\u043b\u0447\u043a\u043e\u043c.",
    "Today": "\u0421\u0435\u0433\u043e\u0434\u043d\u044f",
    "Tomorrow": "\u0417\u0430\u0432\u0442\u0440\u0430",
    "Type into this box to filter down the list of available %s.": "\u041d\u0430\u0447\u043d\u0438\u0442\u0435 \u0432\u0432\u043e\u0434\u0438\u0442\u044c \u0442\u0435\u043a\u0441\u0442 \u0432 \u044d\u0442\u043e\u043c \u043f\u043e\u043b\u0435, \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u0444\u0438\u0442\u0440\u043e\u0432\u0430\u0442\u044c \u0441\u043f\u0438\u0441\u043e\u043a \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0445 %s.",
    "Warning: you have unsaved changes": "\u0412\u043d\u0438\u043c\u0430\u043d\u0438\u0435: \u0443 \u0432\u0430\u0441 \u0435\u0441\u0442\u044c \u043d\u0435\u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f",
    "Yesterday": "\u0412\u0447\u0435\u0440\u0430",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "\u0412\u044b \u0432\u044b\u0431\u0440\u0430\u043b\u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u0438 \u043d\u0435 \u0432\u043d\u0435\u0441\u043b\u0438 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u0439 \u0432 \u0434\u0430\u043d\u043d\u044b\u0435. \u0412\u043e\u0437\u043c\u043e\u0436\u043d\u043e, \u0432\u044b \u0445\u043e\u0442\u0435\u043b\u0438 \u0432\u043e\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f \u043a\u043d\u043e\u043f\u043a\u043e\u0439 \"\u0412\u044b\u043f\u043e\u043b\u043d\u0438\u0442\u044c\", \u0430 \u043d\u0435 \u043a\u043d\u043e\u043f\u043a\u043e\u0439 \"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c\". \u0415\u0441\u043b\u0438 \u044d\u0442\u043e \u0442\u0430\u043a, \u0442\u043e \u043d\u0430\u0436\u043c\u0438\u0442\u0435 \"\u041e\u0442\u043c\u0435\u043d\u0430\", \u0447\u0442\u043e\u0431\u044b \u0432\u0435\u0440\u043d\u0443\u0442\u044c\u0441\u044f \u0432 \u0438\u043d\u0442\u0435\u0440\u0444\u0435\u0439\u0441 \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f. ",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "\u0412\u044b \u0432\u044b\u0431\u0440\u0430\u043b\u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435, \u043d\u043e \u0435\u0449\u0435 \u043d\u0435 \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u043b\u0438 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f, \u0432\u043d\u0435\u0441\u0435\u043d\u043d\u044b\u0435 \u0432 \u043d\u0435\u043a\u043e\u0442\u043e\u0440\u044b\u0445 \u043f\u043e\u043b\u044f\u0445 \u0434\u043b\u044f \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f. \u041d\u0430\u0436\u043c\u0438\u0442\u0435 OK, \u0447\u0442\u043e\u0431\u044b \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f. \u041f\u043e\u0441\u043b\u0435 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f \u0432\u0430\u043c \u043f\u0440\u0438\u0434\u0435\u0442\u0441\u044f \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u0435\u0449\u0435 \u0440\u0430\u0437.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "\u0418\u043c\u0435\u044e\u0442\u0441\u044f \u043d\u0435\u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0432 \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u044b\u0445 \u043f\u043e\u043b\u044f\u0445 \u0434\u043b\u044f \u0440\u0435\u0434\u0430\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f. \u0415\u0441\u043b\u0438 \u0432\u044b \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u0435 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435, \u043d\u0435\u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u043d\u044b\u0435 \u0438\u0437\u043c\u0435\u043d\u0435\u043d\u0438\u044f \u0431\u0443\u0434\u0443\u0442 \u043f\u043e\u0442\u0435\u0440\u044f\u043d\u044b.",
    "deselect all": "\u0443\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435",
    "one letter Friday\u0004F": "\u041f",
    "one letter Monday\u0004M": "\u041f",
    "one letter Saturday\u0004S": "\u0421",
    "one letter Sunday\u0004S": "\u0412",
    "one letter Thursday\u0004T": "\u0427",
    "one letter Tuesday\u0004T": "\u0412",
    "one letter Wednesday\u0004W": "\u0421",
    "select all": "\u0432\u044b\u0431\u0440\u0430\u0442\u044c \u0432\u0441\u0435"
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
    "DATETIME_FORMAT": "j E Y \u0433. G:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%d.%m.%Y",
      "%d.%m.%y %H:%M:%S",
      "%d.%m.%y %H:%M:%S.%f",
      "%d.%m.%y %H:%M",
      "%d.%m.%y",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j E Y \u0433.",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y H:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": "\u00a0",
    "TIME_FORMAT": "G:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y \u0433."
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

