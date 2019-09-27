

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    var v=(n > 1);
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
      "%(sel)s sur %(cnt)s s\u00e9lectionn\u00e9",
      "%(sel)s sur %(cnt)s s\u00e9lectionn\u00e9s"
    ],
    "6 a.m.": "6:00",
    "6 p.m.": "18:00",
    "Add": "Ajouter",
    "Add Ballot": "Ajouter feuille",
    "Adjudicator Demographics": "D\u00e9mographiques des juges",
    "Adjudicator Results": "R\u00e9sultats de juge",
    "April": "Avril",
    "August": "Ao\u00fbt",
    "Auto-Allocate": "Allouer automatiquement",
    "Auto-Prioritise": "Prioriser automatiquement",
    "Available %s": "%s disponible(s)",
    "Ballot Check-Ins": "Enregistrements de feuilles",
    "Ballot Statuses": "Statuts de feuilles",
    "Cancel": "Annuler",
    "Checked-In": "Enregistr\u00e9",
    "Choose": "Choisir",
    "Choose a Date": "Choisir une date",
    "Choose a Time": "Choisir une heure",
    "Choose a time": "Choisir une heure",
    "Choose all": "Tout choisir",
    "Chosen %s": "Choix des \u00ab\u00a0%s \u00bb",
    "Click to choose all %s at once.": "Cliquez pour choisir tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Click to remove all chosen %s at once.": "Cliquez pour enlever tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Confirmed": "Confirm\u00e9",
    "Copy From Check-Ins": "Copier \u00e0 partir des enregistrements",
    "December": "D\u00e9cembre",
    "Delete": "\u00c9ffacer",
    "February": "F\u00e9vrier",
    "Filter": "Filtrer",
    "Find in Table": "Trouver dans la table",
    "General": "G\u00e9n\u00e9ral",
    "Hide": "Masquer",
    "January": "Janvier",
    "July": "Juillet",
    "June": "Juin",
    "March": "Mars",
    "Match": "Refl\u00e9ter",
    "Match Check-Ins": "Refl\u00e9ter les enregistrements",
    "May": "Mai",
    "Midnight": "Minuit",
    "No Adjudicator Ratings Information": "Pas d\u2019information de rang de juge",
    "No Adjudicator-Adjudicator Feedback Information": "Pas d\u2019information d\u2019\u00e9valuations juge-juge",
    "No Gender Information": "Pas d\u2019information de genre",
    "No Position Information": "Pas d\u2019information de r\u00f4le",
    "No Region Information": "Pas d\u2019information de r\u00e9gion",
    "No Speaker Categories Information": "Pas d\u2019information des cat\u00e9gories d\u2019orateur",
    "No changes": "Aucun changement",
    "Noon": "Midi",
    "Not Checked-In": "Pas enregistr\u00e9",
    "Note: You are %s hour ahead of server time.": [
      "Note\u00a0: l'heure du serveur pr\u00e9c\u00e8de votre heure de %s heure.",
      "Note\u00a0: l'heure du serveur pr\u00e9c\u00e8de votre heure de %s heures."
    ],
    "Note: You are %s hour behind server time.": [
      "Note\u00a0: votre heure pr\u00e9c\u00e8de l'heure du serveur de %s heure.",
      "Note\u00a0: votre heure pr\u00e9c\u00e8de l'heure du serveur de %s heures."
    ],
    "November": "Novembre",
    "Now": "Maintenant",
    "October": "Octobre",
    "Re-Edit": "Re-modifier",
    "Remove": "Enlever",
    "Remove all": "Tout enlever",
    "Return to Draw": "Retour au tirage",
    "Review": "R\u00e9viser",
    "September": "Septembre",
    "Set All Breaking as Available": "Marquer tout qualifiant comme disponible",
    "Set all availabilities to exactly match check-ins.": "Fixer tous les disponibilit\u00e9s pour refl\u00e9ter les enregistrements.",
    "Set all the availabilities to exactly match what they were in the previous round.": "Fixer tous les disponibilit\u00e9s pour refl\u00e9ter leurs statuts dans la joute pr\u00e9c\u00e9dente.",
    "Set people as available only if they have a check-in and are currently unavailable \u2014 i.e. it will not overwrite any existing availabilities.": "Fixer participants comme disponible seulement s\u2019ils peuvent s\u2019enregistrer et qui sont pr\u00e9sentement indisponible \u2014 i.e. ne va pas \u00e9craser les disponibilit\u00e9s qui existent.",
    "Show": "Afficher",
    "Speaker Demographics": "D\u00e9mographiques des Orateurs",
    "Speaker Results": "R\u00e9sultats d\u2019orateur",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Ceci est une liste des \u00ab\u00a0%s\u00a0\u00bb disponibles. Vous pouvez en choisir en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab\u00a0Choisir\u00a0\u00bb entre les deux zones.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Ceci est la liste des \u00ab\u00a0%s\u00a0\u00bb choisi(e)s. Vous pouvez en enlever en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab Enlever \u00bb entre les deux zones.",
    "Today": "Aujourd'hui",
    "Tomorrow": "Demain",
    "Type into this box to filter down the list of available %s.": "\u00c9crivez dans cette zone pour filtrer la liste des \u00ab\u00a0%s\u00a0\u00bb disponibles.",
    "Unconfirmed": "Non-confirm\u00e9",
    "Unknown": "Inconnu",
    "Warning: you have unsaved changes": "Attention: vous avez des modifications non sauvegard\u00e9es",
    "Yesterday": "Hier",
    "You cannot confirm this ballot because you entered it": "Vous pouvez pas confirmer ce feuille parce que vous l\u2019avez saisi",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Vous avez s\u00e9lectionn\u00e9 une action, et vous n'avez fait aucune modification sur des champs. Vous cherchez probablement le bouton Envoyer et non le bouton Enregistrer.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Vous avez s\u00e9lectionn\u00e9 une action, mais vous n'avez pas encore sauvegard\u00e9 certains champs modifi\u00e9s. Cliquez sur OK pour sauver. Vous devrez r\u00e9appliquer l'action.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Vous avez des modifications non sauvegard\u00e9es sur certains champs \u00e9ditables. Si vous lancez une action, ces modifications vont \u00eatre perdues.",
    "adjudicators with gender data": "juges avec donn\u00e9es de genre",
    "deselect all": "d\u00e9s\u00e9lectionner tout",
    "feedback scores total": "totale des scores d\u2019\u00e9valuation",
    "one letter Friday\u0004F": "V",
    "one letter Monday\u0004M": "L",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "J",
    "one letter Tuesday\u0004T": "M",
    "one letter Wednesday\u0004W": "M",
    "select all": "s\u00e9lectionner tout",
    "speaker scores total": "total des scores d\u2019orateur",
    "speakers with gender data": "orateurs avec donn\u00e9es de genre"
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
        return value[django.pluralidx(count)];
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
    "DATETIME_FORMAT": "j F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d/%m/%Y",
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%d.%m.%Y",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j N Y H:i",
    "SHORT_DATE_FORMAT": "j N Y",
    "THOUSAND_SEPARATOR": "\u00a0",
    "TIME_FORMAT": "H:i",
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

