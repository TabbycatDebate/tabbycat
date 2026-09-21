
'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});


  django.pluralidx = function(n) {
    const v = 0;
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
      "%(sel)s dari %(cnt)s terpilih"
    ],
    "%s selected option not visible": [
      "%s pilihan terpilih tidak muncul"
    ],
    "(click to clear)": "(klik untuk membersihkan)",
    "6 a.m.": "6 pagi",
    "6 p.m.": "18.00",
    "April": "April",
    "August": "Agustus",
    "Available %s": "%s yang tersedia",
    "Break": "Break",
    "Cancel": "Batal",
    "Category": "Kategori",
    "Checked-In": "Sudah Cek-In",
    "Choose %s by selecting them and then select the \"Choose\" arrow button.": "Pilih %s dengan memilih mereka dan kemudian memilih tombol panah \"Choose\".",
    "Choose a Date": "Pilih Tanggal",
    "Choose a Time": "Pilih Waktu",
    "Choose a time": "Pilih waktu",
    "Choose all %s": "Pilih semua %s",
    "Choose selected %s": "Pilih terpilih %s",
    "Chosen %s": "%s terpilih",
    "December": "Desember",
    "February": "Februari",
    "Filter": "Filter",
    "Friday": "Jum'at",
    "January": "Januari",
    "July": "Juli",
    "June": "Juni",
    "March": "Maret",
    "May": "Mei",
    "Midnight": "Tengah malam",
    "Monday": "Senin",
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
    "Remove %s by selecting them and then select the \"Remove\" arrow button.": "Pindahkan%s dengan memilih mereka dan kemudian memilih tombol panah \"Remove\".",
    "Remove all %s": "Pindahkan semua %s",
    "Remove selected %s": "Pindahkan terpilih %s",
    "Room:": "Ruangan:",
    "Saturday": "Sabtu",
    "September": "September",
    "Sunday": "Ahad",
    "Team": "Tim",
    "Thursday": "Kamis",
    "Today": "Hari ini",
    "Tomorrow": "Besok",
    "Tuesday": "Selasa",
    "Type into this box to filter down the list of available %s.": "Ketik pada kotak ini untuk menyaring daftar %s yang tersedia.",
    "Type into this box to filter down the list of selected %s.": "Ketik di dalam kotak utnuk menyaring daftar dar %s terpilih.",
    "Unknown": "Tak diketahui",
    "Wednesday": "Rabu",
    "Yesterday": "Kemarin",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Anda telah memilih tindakan, dan Anda belum membuat perubahan apa pun di setiap bidang. Anda mungkin mencari tombol Buka daripada tombol Simpan.",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Anda telah memilih tindakan, tetapi Anda belum menyimpan perubahan ke masing-masing bidang. Silakan klik OK untuk menyimpan. Anda harus menjalankan kembali tindakan tersebut.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Beberapa perubahan bidang yang Anda lakukan belum tersimpan. Perubahan yang telah dilakukan akan hilang.",
    "abbrev. day Friday\u0004Fri": "Jum",
    "abbrev. day Monday\u0004Mon": "Sen",
    "abbrev. day Saturday\u0004Sat": "Sab",
    "abbrev. day Sunday\u0004Sun": "Ahd",
    "abbrev. day Thursday\u0004Thur": "Kam",
    "abbrev. day Tuesday\u0004Tue": "Sel",
    "abbrev. day Wednesday\u0004Wed": "Rab",
    "abbrev. month April\u0004Apr": "Apr",
    "abbrev. month August\u0004Aug": "Agu",
    "abbrev. month December\u0004Dec": "Des",
    "abbrev. month February\u0004Feb": "Feb",
    "abbrev. month January\u0004Jan": "Jan",
    "abbrev. month July\u0004Jul": "Jul",
    "abbrev. month June\u0004Jun": "Jun",
    "abbrev. month March\u0004Mar": "Mar",
    "abbrev. month May\u0004May": "Mei",
    "abbrev. month November\u0004Nov": "Nov",
    "abbrev. month October\u0004Oct": "Okt",
    "abbrev. month September\u0004Sep": "Sep",
    "one letter Friday\u0004F": "J",
    "one letter Monday\u0004M": "S",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "M",
    "one letter Thursday\u0004T": "K",
    "one letter Tuesday\u0004T": "S",
    "one letter Wednesday\u0004W": "R"
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

