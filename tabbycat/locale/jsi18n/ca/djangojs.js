

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
      "%(sel)s de %(cnt)s seleccionat",
      "%(sel)s of %(cnt)s seleccionats"
    ],
    "6 a.m.": "6 a.m.",
    "6 p.m.": "6 p.m.",
    "All": "Tot",
    "April": "Abril",
    "August": "Agost",
    "Available %s": "%s Disponibles",
    "Break": "Tall",
    "Cancel": "Cancel\u00b7lar",
    "Category": "Categoria",
    "Choose": "Escollir",
    "Choose a Date": "Escolliu una data",
    "Choose a Time": "Escolliu una hora",
    "Choose a time": "Escolliu una hora",
    "Choose all": "Escollir-los tots",
    "Chosen %s": "Escollit %s",
    "Click to choose all %s at once.": "Feu clic per escollir tots els %s d'un cop.",
    "Click to remove all chosen %s at once.": "Feu clic per eliminar tots els %s escollits d'un cop.",
    "Confirmed": "Confirmat",
    "December": "Desembre",
    "February": "Febrer",
    "Filter": "Filtre",
    "Find in Table": "Troba a la taula",
    "Hide": "Ocultar",
    "January": "Gener",
    "July": "Juliol",
    "June": "Juny",
    "Latest Actions": "\u00daltimes accions",
    "March": "Mar\u00e7",
    "May": "Maig",
    "Midnight": "Mitjanit",
    "Noon": "Migdia",
    "Note: You are %s hour ahead of server time.": [
      "Nota: Aneu %s hora avan\u00e7ats respecte la hora del servidor.",
      "Nota: Aneu %s hores avan\u00e7ats respecte la hora del servidor."
    ],
    "Note: You are %s hour behind server time.": [
      "Nota: Aneu %s hora endarrerits respecte la hora del servidor.",
      "Nota: Aneu %s hores endarrerits respecte la hora del servidor."
    ],
    "November": "Novembre",
    "Now": "Ara",
    "October": "Octubre",
    "Remove": "Eliminar",
    "Remove all": "Esborrar-los tots",
    "September": "Setembre",
    "Show": "Mostrar",
    "Team": "Equip",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Aquesta \u00e9s la llista de %s disponibles. En podeu escollir alguns seleccionant-los a la caixa de sota i fent clic a la fletxa \"Escollir\" entre les dues caixes.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Aquesta \u00e9s la llista de %s escollits. En podeu eliminar alguns seleccionant-los a la caixa de sota i fent clic a la fletxa \"Eliminar\" entre les dues caixes.",
    "Today": "Avui",
    "Tomorrow": "Dem\u00e0",
    "Type into this box to filter down the list of available %s.": "Escriviu en aquesta caixa per a filtrar la llista de %s disponibles.",
    "Unknown": "Desconegut",
    "Yesterday": "Ahir",
    "You have already submitted this form. Are you sure you want to submit it again?": "Ja ha enviat aquest formulari. Est\u00e0s segur que vols enviar-ho de nou?",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Has seleccionat una acci\u00f3 i no has fet cap canvi als camps individuals. Probablement est\u00e0s cercant el bot\u00f3 Anar enlloc del bot\u00f3 de Desar.",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Has seleccionat una acci\u00f3, per\u00f2 encara no l'has desat els canvis dels camps individuals. Si us plau clica OK per desar. Necessitar\u00e0s tornar a executar l'acci\u00f3.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Teniu canvis sense desar a camps editables individuals. Si executeu una acci\u00f3, es perdran aquests canvis no desats.",
    "abbrev. month April\u0004Apr": "Abr",
    "abbrev. month August\u0004Aug": "Ago",
    "abbrev. month December\u0004Dec": "Des",
    "abbrev. month February\u0004Feb": "Feb",
    "abbrev. month January\u0004Jan": "Gen",
    "abbrev. month July\u0004Jul": "Jul",
    "abbrev. month June\u0004Jun": "Jun",
    "abbrev. month March\u0004Mar": "Mar",
    "abbrev. month May\u0004May": "Mai",
    "abbrev. month November\u0004Nov": "Nov",
    "abbrev. month October\u0004Oct": "Oct",
    "abbrev. month September\u0004Sep": "Sep",
    "one letter Friday\u0004F": "V",
    "one letter Monday\u0004M": "L",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "J",
    "one letter Tuesday\u0004T": "M",
    "one letter Wednesday\u0004W": "X"
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
    "DATETIME_FORMAT": "j E \\d\\e Y \\a \\l\\e\\s G:i",
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
    "DATE_FORMAT": "j E \\d\\e Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j E",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d/m/Y G:i",
    "SHORT_DATE_FORMAT": "d/m/Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "G:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F \\d\\e\\l Y"
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

