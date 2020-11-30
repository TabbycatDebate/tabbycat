

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
      "%(sel)s dari %(cnt)s terpilih"
    ],
    "6 a.m.": "6 pagi",
    "6 p.m.": "18.00",
    "April": "April",
    "August": "Agustus",
    "Available %s": "%s yang tersedia",
    "Break": "Break",
    "Cancel": "Batal",
    "Category": "Kategori",
    "Checked-In": "Sudah Cek-In",
    "Choose": "Pilih",
    "Choose a Date": "Pilih Tanggal",
    "Choose a Time": "Pilih Waktu",
    "Choose a time": "Pilih waktu",
    "Choose all": "Pilih semua",
    "Chosen %s": "%s terpilih",
    "Click to choose all %s at once.": "Pilih untuk memilih seluruh %s sekaligus.",
    "Click to remove all chosen %s at once.": "Klik untuk menghapus semua pilihan %s sekaligus.",
    "December": "Desember",
    "February": "Februari",
    "Filter": "Filter",
    "Hide": "Ciutkan",
    "January": "Januari",
    "July": "Juli",
    "June": "Juni",
    "March": "Maret",
    "May": "Mei",
    "Midnight": "Tengah malam",
    "Noon": "Siang",
    "Note: You are %s hour ahead of server time.": [
      "Catatan: Waktu Anda lebih cepat %s jam dibandingkan waktu server."
    ],
    "Note: You are %s hour behind server time.": [
      "Catatan: Waktu Anda lebih lambat %s jam dibandingkan waktu server."
    ],
    "November": "November",
    "Now": "Sekarang",
    "October": "Oktober",
    "Remove": "Hapus",
    "Remove all": "Hapus semua",
    "Room:": "Ruangan:",
    "September": "September",
    "Show": "Bentangkan",
    "Team": "Tim",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Berikut adalah daftar %s yang tersedia. Anda dapat memilih satu atau lebih dengan memilihnya pada kotak di bawah, lalu mengeklik tanda panah \"Pilih\" di antara kedua kotak.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Berikut adalah daftar %s yang terpilih. Anda dapat menghapus satu atau lebih dengan memilihnya pada kotak di bawah, lalu mengeklik tanda panah \"Hapus\" di antara kedua kotak.",
    "Today": "Hari ini",
    "Tomorrow": "Besok",
    "Type into this box to filter down the list of available %s.": "Ketik pada kotak ini untuk menyaring daftar %s yang tersedia.",
    "Unknown": "Tak diketahui",
    "Yesterday": "Kemarin",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Anda telah memilih sebuah aksi, tetapi belum mengubah bidang apapun. Kemungkinan Anda mencari tombol Buka dan bukan tombol Simpan.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Anda telah memilih sebuah aksi, tetapi belum menyimpan perubahan ke bidang yang ada. Klik OK untuk menyimpan perubahan ini. Anda akan perlu mengulangi aksi tersebut kembali.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Beberapa perubahan bidang yang Anda lakukan belum tersimpan. Perubahan yang telah dilakukan akan hilang.",
    "one letter Friday\u0004F": "J",
    "one letter Monday\u0004M": "S",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "M",
    "one letter Thursday\u0004T": "K",
    "one letter Tuesday\u0004T": "S",
    "one letter Wednesday\u0004W": "R"
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
    "DATETIME_FORMAT": "j N Y, G.i",
    "DATETIME_INPUT_FORMATS": [
      "%d-%m-%Y %H.%M.%S",
      "%d-%m-%Y %H.%M.%S.%f",
      "%d-%m-%Y %H.%M",
      "%d-%m-%y %H.%M.%S",
      "%d-%m-%y %H.%M.%S.%f",
      "%d-%m-%y %H.%M",
      "%m/%d/%y %H.%M.%S",
      "%m/%d/%y %H.%M.%S.%f",
      "%m/%d/%y %H.%M",
      "%m/%d/%Y %H.%M.%S",
      "%m/%d/%Y %H.%M.%S.%f",
      "%m/%d/%Y %H.%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j N Y",
    "DATE_INPUT_FORMATS": [
      "%d-%m-%Y",
      "%d/%m/%Y",
      "%d-%m-%y",
      "%d/%m/%y",
      "%d %b %Y",
      "%d %B %Y",
      "%m/%d/%y",
      "%m/%d/%Y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d-m-Y G.i",
    "SHORT_DATE_FORMAT": "d-m-Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "G.i",
    "TIME_INPUT_FORMATS": [
      "%H.%M.%S",
      "%H.%M",
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

