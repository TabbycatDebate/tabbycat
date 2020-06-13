

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
    "%1 %2 from %3": "%1 %2 par %3",
    "%1 %2 from %3 %4": "%1 %2 par %3 %4",
    "%1 %2 from %3 on %4 (Chair)": "%1 %2 par %3 sur %4 (Pr\u00e9sident)",
    "%1 %2 from %3 on %4 (Panellist)": "%1 %2 par %3 sur %4 (Panelliste)",
    "%1 %2 from %3 on %4 (Trainee)": "%1 %2 par %3 sur %4 (Stagiaire)",
    "%1 (%2) with identifier of %3": "%1 (%2) avec l'identifiant %3",
    "%1 (%2) with no assigned identifier": "%1 (%2) sans identifiant",
    "%1 (%2, %3)": "%1 (%2, %3)",
    "%1 (Absent; id=%2)": "%1 (Absent\u00a0; id=%2)",
    "%1 (Present; id=%2)": "%1 (Pr\u00e9sent\u00a0; id=%2)",
    "%1 (no category) with identifier of %2": "%1 (aucune cat\u00e9gorie) avec l'identifiant %2",
    "%1 (no category) with no assigned identifier": "%1 (aucune cat\u00e9gorie) sans identifiant",
    "%1 checked in %2: %3": "%1 enregistr\u00e9 %2\u00a0: %3",
    "%1, %2": "%1, %2",
    "%1, a %2": "%1, un %2",
    "%1, a %2 from %3 with identifier of %4": "%1, un %2 de %3 avec l'identifiant %4",
    "%1, a %2 from %3 with no assigned identifier": "%1, un %2 de %3 sans identifiant",
    "%1, a %2 of no institutional affiliation with identifier of %3": "%1, un %2 sans affiliation avec l'identifiant %3",
    "%1, a %2 of no institutional affiliation with no assigned identifier": "%1, un %2 sans affiliation ni identifiant",
    "%1, a team with speakers %2": "%1, un \u00e9quipe avec orateurs %2",
    "%1:": "%1\u00a0:",
    "6 a.m.": "6:00",
    "6 p.m.": "18:00",
    "; ": " ; ",
    "<strong>%1</strong>: %2": "<strong>%1</strong>\u00a0: %2",
    "<strong>\u2613</strong> All": "<strong>\u2613</strong> Tous",
    "<strong>\u2713</strong> All": "<strong>\u2713</strong> Tous",
    "Add": "Ajouter",
    "Add Ballot": "Ajouter feuille",
    "Adjudicating with %1.": "Jugeant avec %1.",
    "Adjudicator Demographics": "D\u00e9mographiques des juges",
    "Adjudicator Results": "R\u00e9sultats de juge",
    "Aff Veto": "V\u00e9to Aff",
    "All": "Tout",
    "Anon": "Anon",
    "Anonymous (due to team codes)": "Anonyme (en raison des codes d'\u00e9quipe)",
    "April": "Avril",
    "August": "Ao\u00fbt",
    "Auto-Allocate": "Allouer automatiquement",
    "Auto-Prioritise": "Prioriser automatiquement",
    "Available %s": "%s disponible(s)",
    "Ballot Check-Ins": "Enregistrements de feuilles",
    "Ballot Statuses": "Statuts de feuilles",
    "Ballots Status": "Statuts des feuilles de jugement",
    "Break": "Qualification",
    "By %1": "Par %1",
    "By how many points did they win:": "Par combien de points ont-ils gagn\u00e9\u00a0:",
    "Cancel": "Annuler",
    "Category": "Cat\u00e9gorie",
    "Chair for Panel of %1": "Pr\u00e9sident pour le jury de %1",
    "Checked-In": "Enregistr\u00e9",
    "Choose": "Choisir",
    "Choose a Date": "Choisir une date",
    "Choose a Time": "Choisir une heure",
    "Choose a time": "Choisir une heure",
    "Choose all": "Tout choisir",
    "Chosen %s": "Choix des \u00ab\u00a0%s \u00bb",
    "Circle %1": "Encercler %1",
    "Circle Rank:": "Encerclez le rang\u00a0:",
    "Circle the last digit of the %1's score:": "Encerclez le dernier chiffre du score de %1\u00a0:",
    "Circle the last digit of the team's total:": "Encerclez le dernier chiffre du total de l'\u00e9quipe\u00a0:",
    "Click to check-in manually": "Cliquer pour enregistrer manuellement",
    "Click to choose all %s at once.": "Cliquez pour choisir tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Click to remove all chosen %s at once.": "Cliquez pour enlever tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Click to undo a check-in": "Cliquez pour annuler un enregistrement",
    "Confirmed": "Confirm\u00e9",
    "Copy From Check-Ins": "Copier \u00e0 partir des enregistrements",
    "Debated": "D\u00e9battu",
    "December": "D\u00e9cembre",
    "Delete": "\u00c9ffacer",
    "Did %1 deliver the adjudication?": "%1 a-t-il livr\u00e9 le jugement\u00a0?",
    "February": "F\u00e9vrier",
    "Filter": "Filtrer",
    "Find in Table": "Trouver dans la table",
    "Gender": "Genre",
    "General": "G\u00e9n\u00e9ral",
    "Hide": "Masquer",
    "ID %1,": "ID %1,",
    "IMPORTANT: Check and explicitly note if a speaker gives multiple speeches": "IMPORTANT\u00a0: Cochez et notez explicitement si un orateur a donn\u00e9 plusieurs discours",
    "If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can use the assistant version.": "Si vous voulez afficher cette page sans la barre lat\u00e9rale (comme pour l'affichage dans un auditorium), vous pouvez utiliser la version d'assistant.",
    "Independent": "Ind\u00e9pendant",
    "January": "Janvier",
    "July": "Juillet",
    "June": "Juin",
    "Latest Actions": "Derni\u00e8res Actions",
    "Latest Results": "Derni\u00e8res R\u00e9sultats",
    "March": "Mars",
    "Mark replies %1 to %2; <strong>%3</strong>.": "Marquer r\u00e9pliques de %1 \u00e0 %2\u00a0; <strong>%3</strong>.",
    "Mark speeches %1 to %2; <strong>%3</strong>.": "Marquer les discours de %1 \u00e0 %2\u00a0; <strong>%3</strong>.",
    "Match": "Refl\u00e9ter",
    "Match Check-Ins": "Refl\u00e9ter les enregistrements",
    "May": "Mai",
    "Midnight": "Minuit",
    "Neg Veto": "V\u00e9to N\u00e9g",
    "No": "Non",
    "No Actions Yet": "Aucune Action",
    "No Adjudicator Ratings Information": "Pas d\u2019information de rang de juge",
    "No Adjudicator-Adjudicator Feedback Information": "Pas d\u2019information d\u2019\u00e9valuations juge-juge",
    "No Category": "Aucune cat\u00e9gorie",
    "No Confirmed Results Yet": "Aucun R\u00e9sultat Confirm\u00e9",
    "No Gender Information": "Pas d\u2019information de genre",
    "No Position Information": "Pas d\u2019information de r\u00f4le",
    "No Region Information": "Pas d\u2019information de r\u00e9gion",
    "No Speaker Categories Information": "Pas d\u2019information des cat\u00e9gories d\u2019orateur",
    "No changes": "Aucun changement",
    "No code name set": "Aucun nom code d\u00e9fini",
    "No matching people found.": "Aucunes personnes correspondantes trouv\u00e9es.",
    "No matching venues found.": "Aucunes salles correspondantes trouv\u00e9es.",
    "No, I am submitting feedback on:": "Non, je donne un \u00e9valuation sur\u00a0:",
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
    "Open the assistant version.": "Ouvrir la version d'assistant.",
    "Panellist": "Membre",
    "Priority %1": "Priorit\u00e9 %1",
    "Rank": "Classement",
    "Re-Edit": "Re-modifier",
    "Region": "R\u00e9gion",
    "Remove": "Enlever",
    "Remove all": "Tout enlever",
    "Return ballots to %1.": "Soumettre feuilles de jugement \u00e0 %1.",
    "Return to Draw": "Retour au tirage",
    "Review": "R\u00e9viser",
    "Scan Using Camera": "Num\u00e9riser avec l'appareil photo",
    "Score:": "Score\u00a0:",
    "September": "Septembre",
    "Set All Breaking as Available": "Marquer tout qualifiant comme disponible",
    "Set all availabilities to exactly match check-ins.": "Fixer tous les disponibilit\u00e9s pour refl\u00e9ter les enregistrements.",
    "Set all the availabilities to exactly match what they were in the previous round.": "Fixer tous les disponibilit\u00e9s pour refl\u00e9ter leurs statuts dans la joute pr\u00e9c\u00e9dente.",
    "Set people as available only if they have a check-in and are currently unavailable \u2014 i.e. it will not overwrite any existing availabilities.": "Fixer participants comme disponible seulement s\u2019ils peuvent s\u2019enregistrer et qui sont pr\u00e9sentement indisponible \u2014 i.e. ne va pas \u00e9craser les disponibilit\u00e9s qui existent.",
    "Show": "Afficher",
    "Solo Chair": "Pr\u00e9sident Seul",
    "Speaker Demographics": "D\u00e9mographiques des Orateurs",
    "Speaker Results": "R\u00e9sultats d\u2019orateur",
    "Stop Camera Scan": "Arr\u00eater Num\u00e9risation",
    "Team": "\u00c9quipe",
    "The bracket range of the hypothetical debate": "La gamme des tranches du d\u00e9bat hypoth\u00e9tique",
    "The debate's bracket": "La tranche du d\u00e9bat",
    "The estimated total number of live break categories across all teams of the hypothetical debate": "Le nombre total estim\u00e9 de cat\u00e9gories de qualification vives sur toutes les \u00e9quipes du d\u00e9bat hypoth\u00e9tique",
    "The motion is <em>%1</em>": "La motion est <em>%1</em>",
    "The total number of live break categories across all teams": "Le nombre total de cat\u00e9gories de qualification vives sur toutes les \u00e9quipes",
    "This debate's priority": "La priorit\u00e9 de ce d\u00e9bat",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Ceci est une liste des \u00ab\u00a0%s\u00a0\u00bb disponibles. Vous pouvez en choisir en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab\u00a0Choisir\u00a0\u00bb entre les deux zones.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Ceci est la liste des \u00ab\u00a0%s\u00a0\u00bb choisi(e)s. Vous pouvez en enlever en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab Enlever \u00bb entre les deux zones.",
    "This page will live-update with new check-ins as they occur although the initial list may be up to a minute old.": "Cette page se met \u00e0 jour automatiquement avec chaque enregistrement, m\u00eame si la liste initiale peut \u00eatre jusqu'\u00e0 une minute hors-jour.",
    "This person does not have a check-in identifier so they can't be checked in": "Cette personne n'a pas d'identifiant donc elle ne peut pas \u00eatre enregistr\u00e9e",
    "Today": "Aujourd'hui",
    "Tomorrow": "Demain",
    "Total:": "Total\u00a0:",
    "Trainee": "Stagiaire",
    "Turn On Sounds": "Activer les sons",
    "Type into this box to filter down the list of available %s.": "\u00c9crivez dans cette zone pour filtrer la liste des \u00ab\u00a0%s\u00a0\u00bb disponibles.",
    "Unaffiliated": "Non-affili\u00e9",
    "Uncategorised": "Non cat\u00e9goris\u00e9",
    "Unconfirmed": "Non-confirm\u00e9",
    "Unknown": "Inconnu",
    "Unsure": "Incertain",
    "Venue:": "Salle\u00a0:",
    "Warning: you have unsaved changes": "Attention: vous avez des modifications non sauvegard\u00e9es",
    "Which team won the debate:": "Quelle \u00e9quipe \u00e0 gagn\u00e9 le d\u00e9bat\u00a0:",
    "Yes": "Oui",
    "Yesterday": "Hier",
    "You cannot confirm this ballot because you entered it": "Vous pouvez pas confirmer ce feuille parce que vous l\u2019avez saisi",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Vous avez s\u00e9lectionn\u00e9 une action, et vous n'avez fait aucune modification sur des champs. Vous cherchez probablement le bouton Envoyer et non le bouton Enregistrer.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Vous avez s\u00e9lectionn\u00e9 une action, mais vous n'avez pas encore sauvegard\u00e9 certains champs modifi\u00e9s. Cliquez sur OK pour sauver. Vous devrez r\u00e9appliquer l'action.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Vous avez des modifications non sauvegard\u00e9es sur certains champs \u00e9ditables. Si vous lancez une action, ces modifications vont \u00eatre perdues.",
    "adjudicators with gender data": "juges avec donn\u00e9es de genre",
    "decimal marks are allowed": "demi-scores sont permises",
    "deselect all": "d\u00e9s\u00e9lectionner tout",
    "feedback scores total": "totale des scores d\u2019\u00e9valuation",
    "no \u00bd marks": "pas de demi-points",
    "one letter Friday\u0004F": "V",
    "one letter Monday\u0004M": "L",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "J",
    "one letter Tuesday\u0004T": "M",
    "one letter Wednesday\u0004W": "M",
    "saving...": "enregistrement en cours...",
    "select all": "s\u00e9lectionner tout",
    "speaker scores total": "total des scores d\u2019orateur",
    "speakers with gender data": "orateurs avec donn\u00e9es de genre",
    "tab check": "v\u00e9rification tab",
    "tab entry": "saisie tab",
    "\u00bd marks are allowed": "demi-points sont permises"
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

