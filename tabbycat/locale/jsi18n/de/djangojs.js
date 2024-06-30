

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(count) { return (count == 1) ? 0 : 1; };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s von %(cnt)s ausgew\u00e4hlt",
      "%(sel)s von %(cnt)s ausgew\u00e4hlt"
    ],
    "%s selected option not visible": [
      "%s ausgew\u00e4hlte Option nicht sichtbar",
      "%s ausgew\u00e4hlte Optionen nicht sichtbar"
    ],
    "6 a.m.": "6 Uhr",
    "6 p.m.": "18 Uhr",
    "April": "April",
    "August": "August",
    "Available %s": "Verf\u00fcgbare %s",
    "Break": "Break",
    "Cancel": "Abbrechen",
    "Category": "Kategorie",
    "Choose": "Ausw\u00e4hlen",
    "Choose a Date": "Datum w\u00e4hlen",
    "Choose a Time": "Uhrzeit w\u00e4hlen",
    "Choose a time": "Uhrzeit",
    "Choose all": "Alle ausw\u00e4hlen",
    "Chosen %s": "Ausgew\u00e4hlte %s",
    "Click to choose all %s at once.": "Klicken, um alle %s auf einmal auszuw\u00e4hlen.",
    "Click to remove all chosen %s at once.": "Klicken, um alle ausgew\u00e4hlten %s auf einmal zu entfernen.",
    "Confirmed": "Best\u00e4tigt",
    "December": "Dezember",
    "February": "Februar",
    "Filter": "Filter",
    "Gender": "Geschlecht",
    "General": "Allgemein",
    "Hide": "Ausblenden",
    "January": "Januar",
    "July": "Juli",
    "June": "Juni",
    "March": "M\u00e4rz",
    "May": "Mai",
    "Midnight": "Mitternacht",
    "Noon": "Mittag",
    "Note: You are %s hour ahead of server time.": [
      "Achtung: Sie sind %s Stunde der Serverzeit vorraus.",
      "Achtung: Sie sind %s Stunden der Serverzeit vorraus."
    ],
    "Note: You are %s hour behind server time.": [
      "Achtung: Sie sind %s Stunde hinter der Serverzeit.",
      "Achtung: Sie sind %s Stunden hinter der Serverzeit."
    ],
    "November": "November",
    "Now": "Jetzt",
    "October": "Oktober",
    "Rank": "Rang",
    "Region": "Region",
    "Remove": "Entfernen",
    "Remove all": "Alle entfernen",
    "September": "September",
    "Show": "Einblenden",
    "Team": "Team",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Dies ist die Liste der verf\u00fcgbaren %s. Einfach im unten stehenden Feld markieren und mithilfe des \u201eAusw\u00e4hlen\u201c-Pfeils ausw\u00e4hlen.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Dies ist die Liste der ausgew\u00e4hlten %s. Einfach im unten stehenden Feld markieren und mithilfe des \u201eEntfernen\u201c-Pfeils wieder entfernen.",
    "Today": "Heute",
    "Tomorrow": "Morgen",
    "Total:": "Gesamt:",
    "Trainee": "Trainee",
    "Type into this box to filter down the list of available %s.": "Durch Eingabe in diesem Feld l\u00e4sst sich die Liste der verf\u00fcgbaren %s eingrenzen.",
    "Type into this box to filter down the list of selected %s.": "In diesem Feld tippen, um die Liste der ausgew\u00e4hlten %s einzuschr\u00e4nken.",
    "Warning: you have unsaved changes": "Warnung: es gibt ungesicherte \u00c4nderungen",
    "Yesterday": "Gestern",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Sie haben eine Aktion ausgew\u00e4hlt, aber keine \u00c4nderungen an bearbeitbaren Feldern vorgenommen. Sie wollten wahrscheinlich auf \u201eAusf\u00fchren\u201c und nicht auf \u201eSpeichern\u201c klicken.",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Sie haben eine Aktion ausgew\u00e4hlt, aber Ihre vorgenommenen \u00c4nderungen nicht gespeichert. Klicken Sie OK, um dennoch zu speichern. Danach m\u00fcssen Sie die Aktion erneut ausf\u00fchren.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Sie haben \u00c4nderungen an bearbeitbaren Feldern vorgenommen und nicht gespeichert. Wollen Sie die Aktion trotzdem ausf\u00fchren und Ihre \u00c4nderungen verwerfen?",
    "abbrev. month April\u0004Apr": "Apr",
    "abbrev. month August\u0004Aug": "Aug",
    "abbrev. month December\u0004Dec": "Dez",
    "abbrev. month February\u0004Feb": "Feb",
    "abbrev. month January\u0004Jan": "Jan",
    "abbrev. month July\u0004Jul": "Jul",
    "abbrev. month June\u0004Jun": "Jun",
    "abbrev. month March\u0004Mar": "Mrz",
    "abbrev. month May\u0004May": "Mai",
    "abbrev. month November\u0004Nov": "Nov",
    "abbrev. month October\u0004Oct": "Okt",
    "abbrev. month September\u0004Sep": "Sep",
    "deselect all": "Alle abw\u00e4hlen",
    "one letter Friday\u0004F": "Fr",
    "one letter Monday\u0004M": "Mo",
    "one letter Saturday\u0004S": "Sa",
    "one letter Sunday\u0004S": "So",
    "one letter Thursday\u0004T": "Do",
    "one letter Tuesday\u0004T": "Di",
    "one letter Wednesday\u0004W": "Mi",
    "select all": "Alle ausw\u00e4hlen"
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
    "DATETIME_FORMAT": "j. F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. F Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d.m.Y H:i",
    "SHORT_DATE_FORMAT": "d.m.Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
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

