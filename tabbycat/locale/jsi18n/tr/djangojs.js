

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
      "%(sel)s / %(cnt)s se\u00e7ildi",
      "%(sel)s / %(cnt)s se\u00e7ildi"
    ],
    "%1 %2 from %3": "%1 %2'den %3",
    "%1 %2 from %3 %4": "%1 %2'den %3 %4",
    "%1 %2 from %3 on %4 (Chair)": "%1 %2'den %3'e %4 (Ba\u015fkan)",
    "%1 %2 from %3 on %4 (Panellist)": "%1 %2'den %3'e kadar% 4 (Panelist)",
    "%1 %2 from %3 on %4 (Trainee)": "%1 %2'den %3'e %4 (Acem,)",
    "%1 (%2) with identifier of %3": "%1 (%2), %3 tan\u0131mlay\u0131c\u0131s\u0131 ile",
    "%1 (%2) with no assigned identifier": "%1 (%2) atanm\u0131\u015f tan\u0131mlay\u0131c\u0131 yok",
    "%1 (%2, %3)": "%1 (%2, %3)",
    "%1 (Absent; id=%2)": "%1 (Yok; id=%2)",
    "%1 (Present; id=%2)": "%1 (Mevcut; id=%2)",
    "%1 (no category) with identifier of %2": "%1 (kategori yok) ve %2 tan\u0131mlay\u0131c\u0131s\u0131",
    "%1 (no category) with no assigned identifier": "%1 (kategori yok) atanm\u0131\u015f tan\u0131mlay\u0131c\u0131 yok",
    "%1 checked in %2: %3": "%1 %2'ye giri\u015f yapt\u0131: %3",
    "%1, %2": "%1, %2",
    "%1, a %2": "%1, bir %2",
    "%1, a %2 from %3 with identifier of %4": "%1, %3'ten %4 tan\u0131mlay\u0131c\u0131l\u0131 bir %2",
    "%1, a %2 from %3 with no assigned identifier": "%1, atanm\u0131\u015f tan\u0131mlay\u0131c\u0131 olmadan %3'ten bir %2",
    "%1, a %2 of no institutional affiliation with identifier of %3": "%1, %3 tan\u0131mlay\u0131c\u0131s\u0131 ile kurumsal ba\u011flant\u0131s\u0131 olmayan %2'si",
    "%1, a %2 of no institutional affiliation with no assigned identifier": "%1, atanm\u0131\u015f tan\u0131mlay\u0131c\u0131s\u0131 olmayan kurumsal bir ili\u015fkinin %2'si",
    "%1, a team with speakers %2": "%1, konu\u015fmac\u0131l\u0131 bir ekip %2",
    "%1:": "%1:",
    "%s selected option not visible": [
      "%s se\u00e7ilen se\u00e7enek g\u00f6r\u00fcn\u00fcr de\u011fil",
      "%s se\u00e7ilen se\u00e7enek g\u00f6r\u00fcn\u00fcr de\u011fil"
    ],
    "6 a.m.": "Sabah 6",
    "6 p.m.": "6 \u00f6.s.",
    "; ": "; ",
    "<strong>%1</strong>: %2": "<strong>%1</strong>: %2",
    "<strong>\u2613</strong> All": "<strong>\u2613</strong> T\u00fcm\u00fc",
    "<strong>\u2713</strong> All": "<strong>\u2713</strong> T\u00fcm\u00fc",
    "Add Ballot": "Ballot ekle",
    "Adjudicating with %1.": "%1 ile j\u00fcri g\u00f6revinde",
    "Adjudicator Demographics": "J\u00fcri Demografisi",
    "Adjudicator Results": "J\u00fcri Sonu\u00e7lar\u0131",
    "Aff Veto": "H\u00fckumet Veto",
    "All": "T\u00fcm",
    "Anon": "Anon",
    "Anonymous (due to team codes)": "Anonim (tak\u0131m kodlar\u0131 nedeniyle)",
    "April": "Nisan",
    "August": "A\u011fustos",
    "Auto-Allocate": "Otomatik Tahsis",
    "Auto-Prioritise": "Otomatik \u00d6nceliklendirme",
    "Available %s": "Mevcut %s",
    "Ballot Check-Ins": "Ballot Giri\u015fi",
    "Ballot Statuses": "Ballot Durumlar\u0131",
    "Ballots Status": "Ballotlar\u0131n Durumu",
    "Break": "Break",
    "By %1": "%1'e g\u00f6re",
    "By how many points did they win:": "Ka\u00e7 puanla kazand\u0131\u011f\u0131:",
    "Cancel": "\u0130ptal",
    "Category": "Kategori",
    "Chair for Panel of %1": "%1 Paneli Ba\u015fkan\u0131",
    "Checked-In": "Giri\u015fli",
    "Choose": "Se\u00e7in",
    "Choose a Date": "Bir Tarih Se\u00e7in",
    "Choose a Time": "Bir Saat Se\u00e7in",
    "Choose a time": "Bir saat se\u00e7in",
    "Choose all": "T\u00fcm\u00fcn\u00fc se\u00e7in",
    "Chosen %s": "Se\u00e7ilen %s",
    "Circle %1": "%1 yuvarlak i\u00e7ine al",
    "Circle Rank:": "Daire S\u0131ralamas\u0131:",
    "Circle the last digit of the %1's score:": "%1'in puan\u0131n\u0131n son basama\u011f\u0131n\u0131 daire i\u00e7ine al\u0131n:",
    "Circle the last digit of the team's total:": "Tak\u0131m\u0131n toplam\u0131n\u0131n son basama\u011f\u0131n\u0131 daire i\u00e7ine al\u0131n:",
    "Click to check-in manually": "Elle giri\u015f yapmak i\u00e7in t\u0131klay\u0131n",
    "Click to choose all %s at once.": "Bir kerede t\u00fcm %s se\u00e7ilmesi i\u00e7in t\u0131klay\u0131n.",
    "Click to remove all chosen %s at once.": "Bir kerede t\u00fcm se\u00e7ilen %s kald\u0131r\u0131lmas\u0131 i\u00e7in t\u0131klay\u0131n.",
    "Click to undo a check-in": "Giri\u015fi geri almak i\u00e7in t\u0131klay\u0131n",
    "Confirmed": "Onaylanm\u0131\u015f",
    "Copy From Check-Ins": "Giri\u015flerdem Kopyala",
    "Debated": "Tart\u0131\u015f\u0131lan",
    "December": "Aral\u0131k",
    "Did %1 deliver the adjudication?": "%1'i karar\u0131 verdi mi?",
    "February": "\u015eubat",
    "Filter": "S\u00fczge\u00e7",
    "Find in Table": "Tabloda Bul",
    "Gender": "Cinsiyet",
    "Hide": "Gizle",
    "ID %1,": "Kimlik %1,",
    "IMPORTANT: Check and explicitly note if a speaker gives multiple speeches": "\u00d6NEML\u0130: Bir konu\u015fmac\u0131n\u0131n birden fazla konu\u015fma yap\u0131p yapmad\u0131\u011f\u0131n\u0131 kontrol edin ve a\u00e7\u0131k\u00e7a not edin",
    "If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can use the assistant version.": "Bu sayfay\u0131 kenar \u00e7ubu\u011fu olmadan g\u00f6r\u00fcnt\u00fclemek istiyorsan\u0131z (yani bir oditoryumda g\u00f6r\u00fcnt\u00fclemek i\u00e7in) yard\u0131mc\u0131 s\u00fcr\u00fcm\u00fc kullanabilirsiniz.",
    "Independent": "Ba\u011f\u0131ms\u0131z",
    "January": "Ocak",
    "July": "Temmuz",
    "June": "Haziran",
    "Latest Actions": "Son Eylemler",
    "Latest Results": "Son Sonu\u00e7lar",
    "March": "Mart",
    "Mark replies %1 to %2; <strong>%3</strong>.": "Yan\u0131tlar\u0131 %1 ile %2 aras\u0131 puanlay\u0131n; <strong>%3</strong>.",
    "Mark speeches %1 to %2; <strong>%3</strong>.": "Konu\u015fmalar\u0131 %1 ila %2 aras\u0131nda puanlay\u0131n;<strong>%3</strong>.",
    "Match": "E\u015fle\u015ftir",
    "Match Check-Ins": "Giri\u015flerle E\u015fle\u015ftir",
    "May": "May\u0131s",
    "Midnight": "Geceyar\u0131s\u0131",
    "Neg Veto": "Muhalefet Veto",
    "No": "Hay\u0131r",
    "No Actions Yet": "Hen\u00fcz \u0130\u015flem Yok",
    "No Adjudicator Ratings Information": "J\u00fcri Derecelendirme Bilgileri Yok",
    "No Adjudicator-Adjudicator Feedback Information": "J\u00fcri-J\u00fcri Geri Bildirim Bilgisi Yok",
    "No Category": "Kategori Yok",
    "No Confirmed Results Yet": "Hen\u00fcz Do\u011frulanm\u0131\u015f Sonu\u00e7 Yok",
    "No Gender Information": "Cinsiyet Bilgisi Yok",
    "No Position Information": "Pozisyon bilgisi yok",
    "No Region Information": "B\u00f6lge Bilgisi Yok",
    "No Speaker Categories Information": "Konu\u015fmac\u0131 Kategorisi Bilgisi Yok",
    "No changes": "De\u011fi\u015fiklik yok",
    "No code name set": "Kod ad\u0131 ayarlanmad\u0131",
    "No matching people found.": "E\u015fle\u015fen ki\u015fi bulunamad\u0131.",
    "No matching rooms found.": "E\u015fle\u015fen oda bulunamad\u0131.",
    "No, I am submitting feedback on:": "Hay\u0131r, a\u015fa\u011f\u0131dakilerle ilgili geri bildirim g\u00f6nderiyorum:",
    "Noon": "\u00d6\u011fle",
    "Not Checked-In": "Giri\u015f Yap\u0131lmad\u0131",
    "Note: You are %s hour ahead of server time.": [
      "Not: Sunucu saatinin %s saat ilerisindesiniz.",
      "Not: Sunucu saatinin %s saat ilerisindesiniz."
    ],
    "Note: You are %s hour behind server time.": [
      "Not: Sunucu saatinin %s saat gerisindesiniz.",
      "Not: Sunucu saatinin %s saat gerisindesiniz."
    ],
    "November": "Kas\u0131m",
    "Now": "\u015eimdi",
    "October": "Ekim",
    "Open the assistant version.": "Yard\u0131mc\u0131 s\u00fcr\u00fcm\u00fcn\u00fc a\u00e7\u0131n.",
    "Panellist": "Panelist",
    "Priority %1": "\u00d6ncelik %1",
    "Rank": "S\u0131ralama",
    "Re-Edit": "Yeniden D\u00fczenle",
    "Region": "B\u00f6lge",
    "Remove": "Kald\u0131r",
    "Remove all": "T\u00fcm\u00fcn\u00fc kald\u0131r",
    "Return ballots to %1.": "Ballotlar\u0131 %1'e d\u00f6nd\u00fcr\u00fcn.",
    "Return to Draw": "Kuraya D\u00f6n",
    "Review": "\u0130ncele",
    "Room:": "Oda:",
    "Scan Using Camera": "Kamera Kullanarak Tara",
    "Score:": "Puan:",
    "September": "Eyl\u00fcl",
    "Set All Breaking as Available": "T\u00fcm Break'leri Kullan\u0131labilir Olarak Ayarla",
    "Set all availabilities to exactly match check-ins.": "T\u00fcm kullan\u0131labilirlikleri giri\u015flerle tam olarak e\u015fle\u015fecek \u015fekilde ayarlay\u0131n.",
    "Set all the availabilities to exactly match what they were in the previous round.": "T\u00fcm kullan\u0131labilirlikleri bir \u00f6nceki turdakiyle tam olarak e\u015fle\u015fecek \u015fekilde ayarla.",
    "Set people as available only if they have a check-in and are currently unavailable \u2014 i.e. it will not overwrite any existing availabilities.": "Ki\u015fileri yaln\u0131zca bir giri\u015f i\u015flemi varsa ve \u015fu anda kullan\u0131lam\u0131yorsa kullan\u0131labilir olarak ayarlay\u0131n - yani mevcut kullan\u0131labilirlikleri silmez.",
    "Show": "G\u00f6ster",
    "Solo Chair": "Tek Ba\u015fkan",
    "Speaker Demographics": "Konu\u015fmac\u0131 Demografisi",
    "Speaker Results": "Konu\u015fmac\u0131 Sonu\u00e7lar\u0131",
    "Stop Camera Scan": "Kamera Taramas\u0131n\u0131 Durdur",
    "Team": "Tak\u0131m",
    "The bracket range of the hypothetical debate": "Varsay\u0131msal ma\u00e7\u0131n a\u015fama aral\u0131\u011f\u0131",
    "The debate's bracket": "Bu ma\u00e7\u0131n a\u015famas\u0131",
    "The estimated total number of live break categories across all teams of the hypothetical debate": "Varsay\u0131msal tart\u0131\u015fmada t\u00fcm tak\u0131mlardaki m\u00fcmk\u00fcn break kategorilerinin toplam say\u0131s\u0131",
    "The motion is <em>%1</em>": "\u00d6nerge <em>%1</em'dir>",
    "The total number of live break categories across all teams": "T\u00fcm tak\u0131mlardaki m\u00fcmk\u00fcn break kategorilerinin toplam say\u0131s\u0131",
    "This debate's priority": "Bu ma\u00e7\u0131n \u00f6nceli\u011fi",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Bu mevcut %s listesidir. A\u015fa\u011f\u0131daki kutudan baz\u0131lar\u0131n\u0131 i\u015faretleyerek ve ondan sonra iki kutu aras\u0131ndaki \"Se\u00e7in\" okuna t\u0131klayarak se\u00e7ebilirsiniz.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Bu se\u00e7ilen %s listesidir. A\u015fa\u011f\u0131daki kutudan baz\u0131lar\u0131n\u0131 i\u015faretleyerek ve ondan sonra iki kutu aras\u0131ndaki \"Kald\u0131r\" okuna t\u0131klayarak kald\u0131rabilirsiniz.",
    "This page will live-update with new check-ins as they occur although the initial list may be up to a minute old.": "Bu sayfa, ilk liste en fazla bir dakika gecikmeli olsa da, ger\u00e7ekle\u015ftikleri anda yeni giri\u015flerle canl\u0131 olarak g\u00fcncellenecektir.",
    "This person does not have a check-in identifier so they can't be checked in": "Bu ki\u015finin bir giri\u015f tan\u0131mlay\u0131c\u0131s\u0131 yok, bu nedenle giri\u015f yapam\u0131yor",
    "Today": "Bug\u00fcn",
    "Tomorrow": "Yar\u0131n",
    "Total:": "Toplam:",
    "Trainee": "Acemi",
    "Turn On Sounds": "Sesleri A\u00e7",
    "Type into this box to filter down the list of available %s.": "Mevcut %s listesini s\u00fczmek i\u00e7in bu kutu i\u00e7ine yaz\u0131n.",
    "Type into this box to filter down the list of selected %s.": "Se\u00e7ilen %s listesini s\u00fczmek i\u00e7in bu kutu i\u00e7ine yaz\u0131n.",
    "Unaffiliated": "Ba\u011f\u0131ms\u0131z",
    "Uncategorised": "Kategorize edilmemi\u015f",
    "Unconfirmed": "Onaylanmam\u0131\u015f",
    "Unknown": "Bilinmeyen",
    "Unsure": "Emin de\u011filim",
    "Which team won the debate:": "Tart\u0131\u015fmay\u0131 hangi tak\u0131m\u0131n kazand\u0131\u011f\u0131:",
    "Yes": "Evet",
    "Yesterday": "D\u00fcn",
    "You cannot confirm this ballot because you entered it": "Bu ballotu girdi\u011finiz i\u00e7in onaylayamazs\u0131n\u0131z",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Bir eylem se\u00e7tiniz, ancak tek tek alanlarda herhangi bir de\u011fi\u015fiklik yapmad\u0131n\u0131z. Muhtemelen Kaydet d\u00fc\u011fmesi yerine Git d\u00fc\u011fmesini ar\u0131yorsunuz.",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Bir eylem se\u00e7tiniz, ancak de\u011fi\u015fikliklerinizi tek tek alanlara kaydetmediniz. Kaydetmek i\u00e7in l\u00fctfen TAMAM d\u00fc\u011fmesine t\u0131klay\u0131n. Eylemi yeniden \u00e7al\u0131\u015ft\u0131rman\u0131z gerekecek.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Bireysel d\u00fczenlenebilir alanlarda kaydedilmemi\u015f de\u011fi\u015fiklikleriniz var. E\u011fer bir eylem \u00e7al\u0131\u015ft\u0131r\u0131rsan\u0131z, kaydedilmemi\u015f de\u011fi\u015fiklikleriniz kaybolacakt\u0131r.",
    "abbrev. month April\u0004Apr": "Nis",
    "abbrev. month August\u0004Aug": "A\u011fu",
    "abbrev. month December\u0004Dec": "Ara",
    "abbrev. month February\u0004Feb": "\u015eub",
    "abbrev. month January\u0004Jan": "Oca",
    "abbrev. month July\u0004Jul": "Tem",
    "abbrev. month June\u0004Jun": "Haz",
    "abbrev. month March\u0004Mar": "Mar",
    "abbrev. month May\u0004May": "May",
    "abbrev. month November\u0004Nov": "Kas",
    "abbrev. month October\u0004Oct": "Eki",
    "abbrev. month September\u0004Sep": "Eyl",
    "adjudicators with gender data": "cinsiyet verilerine sahip j\u00fcriler",
    "decimal marks are allowed": "ondal\u0131k i\u015faretlere izin verilir",
    "feedback scores total": "geri bildirim puanlar\u0131 toplam\u0131",
    "no \u00bd marks": "yar\u0131m puan yok",
    "one letter Friday\u0004F": "C",
    "one letter Monday\u0004M": "Pt",
    "one letter Saturday\u0004S": "Ct",
    "one letter Sunday\u0004S": "P",
    "one letter Thursday\u0004T": "Pe",
    "one letter Tuesday\u0004T": "S",
    "one letter Wednesday\u0004W": "\u00c7",
    "saving...": "kaydediliyor...",
    "speaker scores total": "konu\u015fmac\u0131 puanlar\u0131 toplam\u0131",
    "speakers with gender data": "cinsiyet verileri olan konu\u015fmac\u0131lar",
    "tab check": "tab kontrol\u00fc",
    "tab entry": "tab giri\u015fi",
    "\u00bd marks are allowed": "yar\u0131m puan var"
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
    "DATETIME_FORMAT": "d F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "d F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "d F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d M Y H:i",
    "SHORT_DATE_FORMAT": "d M Y",
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

