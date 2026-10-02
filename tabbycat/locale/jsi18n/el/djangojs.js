
'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});


  django.pluralidx = function(n) {
    const v = (n != 1);
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };


  /* gettext library */

  django.catalog = django.catalog || {};

  const newcatalog = {
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s \u03b1\u03c0\u03cc %(cnt)s \u03b5\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03b1",
      "%(sel)s \u03b1\u03c0\u03cc %(cnt)s \u03b5\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03b1"
    ],
    "6 a.m.": "6 \u03c0.\u03bc.",
    "6 p.m.": "6 \u03bc.\u03bc.",
    "April": "\u0391\u03c0\u03c1\u03af\u03bb\u03b9\u03bf\u03c2",
    "August": "\u0391\u03cd\u03b3\u03bf\u03c5\u03c3\u03c4\u03bf\u03c2",
    "Available %s": "\u0394\u03b9\u03b1\u03b8\u03ad\u03c3\u03b9\u03bc\u03bf %s",
    "Cancel": "\u0391\u03ba\u03cd\u03c1\u03c9\u03c3\u03b7",
    "Choose": "\u0395\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae",
    "Choose a Date": "\u0395\u03c0\u03b9\u03bb\u03ad\u03be\u03c4\u03b5 \u03bc\u03b9\u03b1 \u0397\u03bc\u03b5\u03c1\u03bf\u03bc\u03b7\u03bd\u03af\u03b1",
    "Choose a Time": "\u0395\u03c0\u03b9\u03bb\u03ad\u03be\u03c4\u03b5 \u03a7\u03c1\u03cc\u03bd\u03bf",
    "Choose a time": "\u0395\u03c0\u03b9\u03bb\u03ad\u03be\u03c4\u03b5 \u03c7\u03c1\u03cc\u03bd\u03bf",
    "Choose all": "\u0395\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae \u03cc\u03bb\u03c9\u03bd",
    "Chosen %s": "\u0395\u03c0\u03b9\u03bb\u03ad\u03c7\u03b8\u03b7\u03ba\u03b5 %s",
    "Click to choose all %s at once.": "\u03a0\u03b1\u03c4\u03ae\u03c3\u03c4\u03b5 \u03b3\u03b9\u03b1 \u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae \u03cc\u03bb\u03c9\u03bd \u03c4\u03c9\u03bd %s \u03bc\u03b5 \u03c4\u03b7 \u03bc\u03af\u03b1.",
    "Click to remove all chosen %s at once.": "\u039a\u03bb\u03af\u03ba \u03b3\u03b9\u03b1 \u03bd\u03b1 \u03b1\u03c6\u03b1\u03b9\u03c1\u03b5\u03b8\u03bf\u03cd\u03bd \u03cc\u03bb\u03b1 \u03c4\u03b1 \u03b5\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03b1 %s \u03bc\u03b5 \u03c4\u03b7 \u03bc\u03af\u03b1.",
    "December": "\u0394\u03b5\u03ba\u03ad\u03bc\u03b2\u03c1\u03b9\u03bf\u03c2",
    "February": "\u03a6\u03b5\u03b2\u03c1\u03bf\u03c5\u03ac\u03c1\u03b9\u03bf\u03c2",
    "Filter": "\u03a6\u03af\u03bb\u03c4\u03c1\u03bf",
    "Hide": "\u0391\u03c0\u03cc\u03ba\u03c1\u03c5\u03c8\u03b7",
    "January": "\u0399\u03b1\u03bd\u03bf\u03c5\u03ac\u03c1\u03b9\u03bf\u03c2",
    "July": "\u0399\u03bf\u03cd\u03bb\u03b9\u03bf\u03c2",
    "June": "\u0399\u03bf\u03cd\u03bd\u03b9\u03bf\u03c2",
    "March": "\u039c\u03ac\u03c1\u03c4\u03b9\u03bf\u03c2",
    "May": "\u039c\u03ac\u03b9\u03bf\u03c2",
    "Midnight": "\u039c\u03b5\u03c3\u03ac\u03bd\u03c5\u03c7\u03c4\u03b1",
    "Noon": "\u039c\u03b5\u03c3\u03b7\u03bc\u03ad\u03c1\u03b9",
    "Note: You are %s hour ahead of server time.": [
      "\u03a3\u03b7\u03bc\u03b5\u03af\u03c9\u03c3\u03b7: \u0395\u03af\u03c3\u03c4\u03b5 %s \u03ce\u03c1\u03b1 \u03bc\u03c0\u03c1\u03bf\u03c3\u03c4\u03ac \u03b1\u03c0\u03cc \u03c4\u03b7\u03bd \u03ce\u03c1\u03b1 \u03c4\u03bf\u03c5 \u03b5\u03be\u03c5\u03c0\u03b7\u03c1\u03b5\u03c4\u03b7\u03c4\u03ae.",
      "\u03a3\u03b7\u03bc\u03b5\u03af\u03c9\u03c3\u03b7: \u0395\u03af\u03c3\u03c4\u03b5 %s \u03ce\u03c1\u03b5\u03c2 \u03bc\u03c0\u03c1\u03bf\u03c3\u03c4\u03ac \u03b1\u03c0\u03cc \u03c4\u03b7\u03bd \u03ce\u03c1\u03b1 \u03c4\u03bf\u03c5 \u03b5\u03be\u03c5\u03c0\u03b7\u03c1\u03b5\u03c4\u03b7\u03c4\u03ae."
    ],
    "Note: You are %s hour behind server time.": [
      "\u03a3\u03b7\u03bc\u03b5\u03af\u03c9\u03c3\u03b7: \u0395\u03af\u03c3\u03c4\u03b5 %s \u03ce\u03c1\u03b1 \u03c0\u03af\u03c3\u03c9 \u03b1\u03c0\u03cc \u03c4\u03b7\u03bd \u03ce\u03c1\u03b1 \u03c4\u03bf\u03c5 \u03b5\u03be\u03c5\u03c0\u03b7\u03c1\u03b5\u03c4\u03b7\u03c4\u03ae",
      "\u03a3\u03b7\u03bc\u03b5\u03af\u03c9\u03c3\u03b7: \u0395\u03af\u03c3\u03c4\u03b5 %s \u03ce\u03c1\u03b5\u03c2 \u03c0\u03af\u03c3\u03c9 \u03b1\u03c0\u03cc \u03c4\u03b7\u03bd \u03ce\u03c1\u03b1 \u03c4\u03bf\u03c5 \u03b5\u03be\u03c5\u03c0\u03b7\u03c1\u03b5\u03c4\u03b7\u03c4\u03ae."
    ],
    "November": "\u039d\u03bf\u03ad\u03bc\u03b2\u03c1\u03b9\u03bf\u03c2",
    "Now": "\u03a4\u03ce\u03c1\u03b1",
    "October": "\u039f\u03ba\u03c4\u03ce\u03b2\u03c1\u03b9\u03bf\u03c2",
    "Remove": "\u0391\u03c6\u03b1\u03af\u03c1\u03b5\u03c3\u03b7",
    "Remove all": "\u0391\u03c6\u03b1\u03af\u03c1\u03b5\u03c3\u03b7 \u03cc\u03bb\u03c9\u03bd",
    "September": "\u03a3\u03b5\u03c0\u03c4\u03ad\u03bc\u03b2\u03c1\u03b9\u03bf\u03c2",
    "Show": "\u03a0\u03c1\u03bf\u03b2\u03bf\u03bb\u03ae",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "\u0391\u03c5\u03c4\u03ae \u03b5\u03af\u03bd\u03b1\u03b9 \u03b7 \u03bb\u03af\u03c3\u03c4\u03b1 \u03c4\u03c9\u03bd \u03b4\u03b9\u03b1\u03b8\u03ad\u03c3\u03b9\u03bc\u03c9\u03bd %s. \u039c\u03c0\u03bf\u03c1\u03b5\u03af\u03c4\u03b5 \u03bd\u03b1 \u03b5\u03c0\u03b9\u03bb\u03ad\u03be\u03b5\u03c4\u03b5 \u03ba\u03ac\u03c0\u03bf\u03b9\u03b1, \u03b1\u03c0\u03cc \u03c4\u03bf \u03c0\u03b1\u03c1\u03b1\u03ba\u03ac\u03c4\u03c9 \u03c0\u03b5\u03b4\u03af\u03bf \u03ba\u03b1\u03b9 \u03c0\u03b1\u03c4\u03ce\u03bd\u03c4\u03b1\u03c2 \u03c4\u03bf \u03b2\u03ad\u03bb\u03bf\u03c2 \"\u0395\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae\" \u03bc\u03b5\u03c4\u03b1\u03be\u03cd \u03c4\u03c9\u03bd \u03b4\u03cd\u03bf \u03c0\u03b5\u03b4\u03af\u03c9\u03bd.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "\u0391\u03c5\u03c4\u03ae \u03b5\u03af\u03bd\u03b1\u03b9 \u03b7 \u03bb\u03af\u03c3\u03c4\u03b1 \u03c4\u03c9\u03bd \u03b5\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03c9\u03bd %s. \u039c\u03c0\u03bf\u03c1\u03b5\u03af\u03c4\u03b5 \u03bd\u03b1 \u03b1\u03c6\u03b1\u03b9\u03c1\u03ad\u03c3\u03b5\u03c4\u03b5 \u03bc\u03b5\u03c1\u03b9\u03ba\u03ac \u03b5\u03c0\u03b9\u03bb\u03ad\u03b3\u03bf\u03bd\u03c4\u03b1\u03c2 \u03c4\u03b1 \u03b1\u03c0\u03bf \u03c4\u03bf \u03ba\u03bf\u03c5\u03c4\u03af \u03c0\u03b1\u03c1\u03b1\u03ba\u03ac\u03c4\u03c9 \u03ba\u03b1\u03b9 \u03bc\u03b5\u03c4\u03ac \u03ba\u03ac\u03bd\u03bf\u03bd\u03c4\u03b1\u03c2 \u03ba\u03bb\u03af\u03ba \u03c3\u03c4\u03bf \u03b2\u03b5\u03bb\u03ac\u03ba\u03b9 \"\u0391\u03c6\u03b1\u03af\u03c1\u03b5\u03c3\u03b7\" \u03b1\u03bd\u03ac\u03bc\u03b5\u03c3\u03b1 \u03c3\u03c4\u03b1 \u03b4\u03cd\u03bf \u03ba\u03bf\u03c5\u03c4\u03b9\u03ac.",
    "Today": "\u03a3\u03ae\u03bc\u03b5\u03c1\u03b1",
    "Tomorrow": "\u0391\u03cd\u03c1\u03b9\u03bf",
    "Type into this box to filter down the list of available %s.": "\u03a0\u03bb\u03b7\u03ba\u03c4\u03c1\u03bf\u03bb\u03bf\u03b3\u03ae\u03c3\u03c4\u03b5 \u03c3\u03b5 \u03b1\u03c5\u03c4\u03cc \u03c4\u03bf \u03c0\u03b5\u03b4\u03af\u03bf \u03b3\u03b9\u03b1 \u03bd\u03b1 \u03c6\u03b9\u03bb\u03c4\u03c1\u03ac\u03c1\u03b5\u03c4\u03b5 \u03c4\u03b7 \u03bb\u03af\u03c3\u03c4\u03b1 \u03c4\u03c9\u03bd \u03b4\u03b9\u03b1\u03b8\u03ad\u03c3\u03b9\u03bc\u03c9\u03bd %s.",
    "Yesterday": "\u03a7\u03b8\u03ad\u03c2",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "\u0388\u03c7\u03b5\u03c4\u03b5 \u03b5\u03c0\u03b9\u03bb\u03ad\u03be\u03b5\u03b9 \u03bc\u03b9\u03b1 \u03b5\u03bd\u03ad\u03c1\u03b3\u03b5\u03b9\u03b1, \u03ba\u03b1\u03b9 \u03b4\u03b5\u03bd \u03ad\u03c7\u03b5\u03c4\u03b5 \u03ba\u03ac\u03bd\u03b5\u03b9 \u03ba\u03b1\u03bc\u03af\u03b1 \u03b1\u03bb\u03bb\u03b1\u03b3\u03ae \u03c3\u03c4\u03b1 \u03b5\u03ba\u03ac\u03c3\u03c4\u03bf\u03c4\u03b5 \u03c0\u03b5\u03b4\u03af\u03b1. \u03a0\u03b9\u03b8\u03b1\u03bd\u03ce\u03bd \u03b8\u03ad\u03bb\u03b5\u03c4\u03b5 \u03c4\u03bf \u03ba\u03bf\u03c5\u03bc\u03c0\u03af Go \u03b1\u03bd\u03c4\u03af \u03c4\u03bf\u03c5 \u03ba\u03bf\u03c5\u03bc\u03c0\u03b9\u03bf\u03cd \u0391\u03c0\u03bf\u03b8\u03ae\u03ba\u03b5\u03c5\u03c3\u03b7\u03c2.",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "\u0388\u03c7\u03b5\u03c4\u03b5 \u03b5\u03c0\u03b9\u03bb\u03ad\u03be\u03b5\u03b9 \u03bc\u03b9\u03b1 \u03b5\u03bd\u03ad\u03c1\u03b3\u03b5\u03b9\u03b1, \u03b1\u03bb\u03bb\u03ac \u03b4\u03b5\u03bd \u03ad\u03c7\u03b5\u03c4\u03b5 \u03b1\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03cd\u03c3\u03b5\u03b9 \u03c4\u03b9\u03c2 \u03b1\u03bb\u03bb\u03b1\u03b3\u03ad\u03c2 \u03c3\u03c4\u03b1 \u03b5\u03ba\u03ac\u03c3\u03c4\u03c9\u03c4\u03b5 \u03c0\u03b5\u03b4\u03af\u03b1 \u03b1\u03ba\u03cc\u03bc\u03b1. \u03a0\u03b1\u03c1\u03b1\u03ba\u03b1\u03bb\u03ce \u03c0\u03b1\u03c4\u03ae\u03c3\u03c4\u03b5 \u039f\u039a \u03b3\u03b9\u03b1 \u03bd\u03b1 \u03c4\u03b9\u03c2 \u03b1\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03cd\u03c3\u03b5\u03c4\u03b5. \u0398\u03b1 \u03c7\u03c1\u03b5\u03b9\u03b1\u03c3\u03c4\u03b5\u03af \u03bd\u03b1 \u03b5\u03ba\u03c4\u03b5\u03bb\u03ad\u03c3\u03b5\u03c4\u03b5 \u03be\u03b1\u03bd\u03ac \u03c4\u03b7\u03bd \u03b5\u03bd\u03ad\u03c1\u03b3\u03b5\u03b9\u03b1.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "\u0388\u03c7\u03b5\u03c4\u03b5 \u03bc\u03b7 \u03b1\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03c5\u03bc\u03ad\u03bd\u03b5\u03c2 \u03b1\u03bb\u03bb\u03b1\u03b3\u03ad\u03c2 \u03c3\u03b5 \u03bc\u03b5\u03bc\u03bf\u03bd\u03c9\u03bc\u03ad\u03bd\u03b1 \u03b5\u03c0\u03b5\u03be\u03b5\u03c1\u03b3\u03ac\u03c3\u03b9\u03bc\u03b1 \u03c0\u03b5\u03b4\u03af\u03b1. \u0386\u03bd \u03b5\u03ba\u03c4\u03b5\u03bb\u03ad\u03c3\u03b5\u03c4\u03b5 \u03bc\u03b9\u03b1 \u03b5\u03bd\u03ad\u03c1\u03b3\u03b5\u03b9\u03b1, \u03bf\u03b9 \u03bc\u03b7 \u03b1\u03c0\u03bf\u03b8\u03b7\u03ba\u03b5\u03c5\u03bc\u03ad\u03bd\u03b5\u03c2 \u03b1\u03bb\u03bb\u03ac\u03b3\u03b5\u03c2 \u03b8\u03b1 \u03c7\u03b1\u03b8\u03bf\u03cd\u03bd",
    "abbrev. month April\u0004Apr": "\u0391\u03c0\u03c1",
    "abbrev. month August\u0004Aug": "\u0391\u03cd\u03b3",
    "abbrev. month December\u0004Dec": "\u0394\u03b5\u03ba",
    "abbrev. month February\u0004Feb": "\u03a6\u03b5\u03b2",
    "abbrev. month January\u0004Jan": "\u0399\u03b1\u03bd",
    "abbrev. month July\u0004Jul": "\u0399\u03bf\u03cd\u03bb",
    "abbrev. month June\u0004Jun": "\u0399\u03bf\u03cd\u03bd",
    "abbrev. month March\u0004Mar": "\u039c\u03ac\u03c1",
    "abbrev. month May\u0004May": "\u039c\u03ac\u03b9",
    "abbrev. month November\u0004Nov": "\u039d\u03bf\u03ad",
    "abbrev. month October\u0004Oct": "\u039f\u03ba\u03c4",
    "abbrev. month September\u0004Sep": "\u03a3\u03b5\u03c0",
    "one letter Friday\u0004F": "\u03a0",
    "one letter Monday\u0004M": "\u0394",
    "one letter Saturday\u0004S": "\u03a3",
    "one letter Sunday\u0004S": "\u039a",
    "one letter Thursday\u0004T": "\u03a0",
    "one letter Tuesday\u0004T": "\u03a4",
    "one letter Wednesday\u0004W": "\u03a4"
  };
  for (const key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }


  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      const value = django.catalog[msgid];
      if (typeof value === 'undefined') {
        return msgid;
      } else {
        return (typeof value === 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      const value = django.catalog[singular];
      if (typeof value === 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      let value = django.gettext(context + '\x04' + msgid);
      if (value.includes('\x04')) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      let value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.includes('\x04')) {
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
    "DATETIME_FORMAT": "d/m/Y P",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M:%S",
      "%d/%m/%y %H:%M:%S.%f",
      "%d/%m/%y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "d/m/Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d/m/Y P",
    "SHORT_DATE_FORMAT": "d/m/Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "P",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      const value = django.formats[format_type];
      if (typeof value === 'undefined') {
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
};

