
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
      "%(sel)s de %(cnt)s selecionado",
      "%(sel)s de %(cnt)s selecionados"
    ],
    "%s selected option not visible": [
      "%s op\u00e7\u00e3o selecionada n\u00e3o vis\u00edvel",
      "%s op\u00e7\u00f5es selecionadas n\u00e3o vis\u00edveis"
    ],
    "6 a.m.": "6 a.m.",
    "6 p.m.": "6 p.m.",
    "All": "Todos",
    "April": "Abril",
    "August": "Agosto",
    "Available %s": "Dispon\u00edvel %s",
    "Cancel": "Cancelar",
    "Choose a Date": "Escolha a Data",
    "Choose a Time": "Escolha a Hora",
    "Choose a time": "Escolha a hora",
    "Chosen %s": "Escolhido %s",
    "Confirmed": "Confirmado",
    "December": "Dezembro",
    "February": "Fevereiro",
    "Filter": "Filtrar",
    "Friday": "Sexta-feira",
    "January": "Janeiro",
    "July": "Julho",
    "June": "Junho",
    "March": "Mar\u00e7o",
    "May": "Maio",
    "Midnight": "Meia-noite",
    "Monday": "Segunda-feira",
    "No": "N\u00e3o",
    "Noon": "Meio-dia",
    "Note: You are %s hour ahead of server time.": [
      "Nota: O seu fuso hor\u00e1rio est\u00e1 %s hora adiantado em rela\u00e7\u00e3o ao servidor.",
      "Nota: O seu fuso hor\u00e1rio est\u00e1 %s horas adiantado em rela\u00e7\u00e3o ao servidor."
    ],
    "Note: You are %s hour behind server time.": [
      "Nota: O use fuso hor\u00e1rio est\u00e1 %s hora atrasado em rela\u00e7\u00e3o ao servidor.",
      "Nota: O use fuso hor\u00e1rio est\u00e1 %s horas atrasado em rela\u00e7\u00e3o ao servidor."
    ],
    "November": "Novembro",
    "Now": "Agora",
    "October": "Outubro",
    "Return to Draw": "Retornar \u00e0s Posi\u00e7\u00f5es",
    "Saturday": "S\u00e1bado",
    "September": "Setembro",
    "Sunday": "Domingo",
    "Team": "Dupla",
    "Thursday": "Quinta-feira",
    "Today": "Hoje",
    "Tomorrow": "Amanh\u00e3",
    "Tuesday": "Ter\u00e7a-feira",
    "Type into this box to filter down the list of available %s.": "Digite nesta caixa para filtrar a lista de %s dispon\u00edveis.",
    "Type into this box to filter down the list of selected %s.": "Digite nesta caixa para filtrar a lista de selecionados %s.",
    "Wednesday": "Quarta-feira",
    "Yes": "Sim",
    "Yesterday": "Ontem",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Tem mudan\u00e7as por guardar nos campos individuais. Se usar uma a\u00e7\u00e3o, as suas mudan\u00e7as por guardar ser\u00e3o perdidas.",
    "abbrev. day Friday\u0004Fri": "Sex",
    "abbrev. day Monday\u0004Mon": "Seg",
    "abbrev. day Saturday\u0004Sat": "S\u00e1b",
    "abbrev. day Sunday\u0004Sun": "Dom",
    "abbrev. day Thursday\u0004Thur": "Qui",
    "abbrev. day Tuesday\u0004Tue": "Ter",
    "abbrev. day Wednesday\u0004Wed": "Qua",
    "abbrev. month April\u0004Apr": "Abr",
    "abbrev. month August\u0004Aug": "Ago",
    "abbrev. month December\u0004Dec": "Dez",
    "abbrev. month February\u0004Feb": "Fev",
    "abbrev. month January\u0004Jan": "Jan",
    "abbrev. month July\u0004Jul": "Jul",
    "abbrev. month June\u0004Jun": "Jun",
    "abbrev. month March\u0004Mar": "Mar",
    "abbrev. month May\u0004May": "Mai",
    "abbrev. month November\u0004Nov": "Nov",
    "abbrev. month October\u0004Oct": "Out",
    "abbrev. month September\u0004Sep": "Set",
    "one letter Friday\u0004F": "S",
    "one letter Monday\u0004M": "S",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "Q",
    "one letter Tuesday\u0004T": "T",
    "one letter Wednesday\u0004W": "Q"
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
    "DATETIME_FORMAT": "j \\d\\e F \\d\\e Y \u00e0\\s H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M:%S",
      "%d/%m/%y %H:%M:%S.%f",
      "%d/%m/%y %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j \\d\\e F \\d\\e Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%d/%m/%Y",
      "%d/%m/%y"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "j \\d\\e F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d/m/Y H:i",
    "SHORT_DATE_FORMAT": "d/m/Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F \\d\\e Y"
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

