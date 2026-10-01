
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
      "%(cnt)s\u500b\u4e2d%(sel)s\u500b\u9078\u629e"
    ],
    "%1 (%2) with identifier of %3": "%1\uff08%2\u3001\u8b58\u5225\u30b3\u30fc\u30c9%3\uff09",
    "%1 (%2) with no assigned identifier": "%1\uff08%2\u3001\u8b58\u5225\u30b3\u30fc\u30c9\u7121\u3057\uff09",
    "%1 (Absent; id=%2)": "%1\uff08\u6b20\u5e2d\u3001id=%2\uff09",
    "%1 (Present; id=%2)": "%1\uff08\u51fa\u5e2d\u3001id=%2\uff09",
    "%1 (no category) with identifier of %2": "%1\uff08\u30ab\u30c6\u30b4\u30ea\u30fc\u306a\u3057\u3001\u8b58\u5225\u30b3\u30fc\u30c9%2\uff09",
    "%1 (no category) with no assigned identifier": "%1\uff08\u30ab\u30c6\u30b4\u30ea\u30fc\u306a\u3057\u3001\u8b58\u5225\u30b3\u30fc\u30c9\u7121\u3057\uff09",
    "%1 checked in %2: %3": "%1\u306b%3\uff08\u30b3\u30fc\u30c9%2\uff09\u304c\u30c1\u30a7\u30c3\u30af\u30a4\u30f3",
    "%1, a %2 from %3 with identifier of %4": "%1\uff08%2\u3001\u30a4\u30f3\u30b9\u30c6%3\u3001\u8b58\u5225\u30b3\u30fc\u30c9%4\uff09",
    "%1, a %2 from %3 with no assigned identifier": "%1\uff08%2\u3001\u30a4\u30f3\u30b9\u30c6%3\u3001\u8b58\u5225\u30b3\u30fc\u30c9\u306a\u3057\uff09",
    "%1, a %2 of no institutional affiliation with identifier of %3": "%1\uff08%2\u3001\u30a4\u30f3\u30b9\u30c6\u306a\u3057\u3001\u8b58\u5225\u30b3\u30fc\u30c9%3\uff09",
    "%1, a %2 of no institutional affiliation with no assigned identifier": "%1\uff08%2\u3001\u30a4\u30f3\u30b9\u30c6\u306a\u3057\u3001\u8b58\u5225\u30b3\u30fc\u30c9\u306a\u3057\uff09",
    "%1, a team with speakers %2": "%1\uff08\u30c1\u30fc\u30e0\uff09\u3001\u30b9\u30d4\u30fc\u30ab\u30fc%2",
    "%s selected option not visible": [
      "\u9078\u629e\u3055\u308c\u305f%s\u4ef6\u306e\u30aa\u30d7\u30b7\u30e7\u30f3\u306f\u975e\u8868\u793a\u3067\u3059\u3002"
    ],
    "(click to clear)": "(\u30af\u30ea\u30c3\u30af\u3067\u30af\u30ea\u30a2)",
    "6 a.m.": "\u5348\u524d 6 \u6642",
    "6 p.m.": "\u5348\u5f8c 6 \u6642",
    "<strong>\u2613</strong> All": "<strong>\u2613</strong> \u5168\u54e1",
    "<strong>\u2713</strong> All": "<strong>\u2713</strong> \u3059\u3079\u3066",
    "Add Ballot": "\u30d0\u30ed\u30c3\u30c8\u3092\u8ffd\u52a0",
    "Adjudicator Demographics": "\u30b8\u30e3\u30c3\u30b8\u306e\u5c5e\u6027\u5206\u5e03",
    "Adjudicator Results": "\u30b8\u30e3\u30c3\u30b8\u306e\u7d50\u679c",
    "All": "\u3059\u3079\u3066",
    "Anon": "\u533f\u540d",
    "Anonymous (due to team codes)": "\u533f\u540d\uff08\u30c1\u30fc\u30e0\u30b3\u30fc\u30c9\u5236\u306e\u305f\u3081\uff09",
    "April": "4\u6708",
    "August": "8\u6708",
    "Auto-Allocate": "\u81ea\u52d5\u914d\u7f6e",
    "Auto-Prioritise": "\u81ea\u52d5\u3067\u512a\u5148\u5ea6\u4ed8\u3051",
    "Available %s": "\u5229\u7528\u53ef\u80fd %s",
    "Ballot Statuses": "\u30d0\u30ed\u30c3\u30c8\u306e\u72b6\u6cc1",
    "Ballots Status": "\u30d0\u30ed\u30c3\u30c8\u306e\u72b6\u6cc1",
    "Break": "\u30d6\u30ec\u30a4\u30af",
    "Cancel": "\u30ad\u30e3\u30f3\u30bb\u30eb",
    "Category": "\u30ab\u30c6\u30b4\u30ea\u30fc",
    "Checked-In": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u6e08\u307f",
    "Choose %s by selecting them and then select the \"Choose\" arrow button.": "%s\u3092\u9078\u629e\u3059\u308b\u306b\u306f\u3001\u9805\u76ee\u3092\u9078\u629e\u3057\u3066\u304b\u3089\"\u9078\u629e\"\u77e2\u5370\u30dc\u30bf\u30f3\u3092\u9078\u629e\u3057\u307e\u3059\u3002",
    "Choose a Date": "\u65e5\u4ed8\u3092\u9078\u629e",
    "Choose a Time": "\u6642\u9593\u3092\u9078\u629e",
    "Choose a time": "\u6642\u9593\u3092\u9078\u629e",
    "Choose all %s": "%s\u3092\u3059\u3079\u3066\u9078\u629e",
    "Choose selected %s": "\u9078\u629e\u3055\u308c\u305f%s\u3092\u9078\u629e",
    "Chosen %s": "\u9078\u629e\u3055\u308c\u305f %s",
    "Click to check-in manually": "\u3053\u3053\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u624b\u52d5\u3067\u30c1\u30a7\u30c3\u30af\u30a4\u30f3",
    "Click to undo a check-in": "\u3053\u3053\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u3092\u30ad\u30e3\u30f3\u30bb\u30eb",
    "Confirmed": "\u627f\u8a8d\u6e08\u307f",
    "Copy From Check-Ins": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u304b\u3089\u30b3\u30d4\u30fc",
    "December": "12\u6708",
    "February": "2\u6708",
    "Filter": "\u30d5\u30a3\u30eb\u30bf\u30fc",
    "Friday": "\u91d1\u66dc\u65e5",
    "Gender": "\u30b8\u30a7\u30f3\u30c0\u30fc",
    "If you want to view this page without the sidebar (i.e. for displaying to an auditorium) you can use the assistant version.": "\u30b5\u30a4\u30c9\u30d0\u30fc\u306a\u3057\u3067\u3053\u306e\u30da\u30fc\u30b8\u3092\u8868\u793a\u3057\u305f\u3044\u5834\u5408\uff08e.g. OR\u3067\u8868\u793a\u3059\u308b\u305f\u3081\uff09\u3001\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8\u306e\u3082\u306e\u3092\u4f7f\u7528\u3067\u304d\u307e\u3059\u3002",
    "Independent": "\u500b\u4eba",
    "January": "1\u6708",
    "July": "7\u6708",
    "June": "6\u6708",
    "Latest Actions": "\u76f4\u8fd1\u306e\u30a2\u30af\u30b7\u30e7\u30f3",
    "Latest Results": "\u76f4\u8fd1\u306e\u7d50\u679c",
    "March": "3\u6708",
    "Match Check-Ins": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u306b\u5408\u308f\u305b\u308b",
    "May": "5\u6708",
    "Midnight": "0\u6642",
    "Monday": "\u6708\u66dc\u65e5",
    "No": "\u3044\u3044\u3048",
    "No Actions Yet": "\u30a2\u30af\u30b7\u30e7\u30f3\u306a\u3057",
    "No Adjudicator Ratings Information": "\u30b8\u30e3\u30c3\u30b8\u306e\u8a55\u4fa1\u306e\u60c5\u5831\u306a\u3057",
    "No Adjudicator-Adjudicator Feedback Information": "\u30b8\u30e3\u30c3\u30b8\u9593\u30d5\u30a3\u30fc\u30c9\u30d0\u30c3\u30af\u306e\u60c5\u5831\u306a\u3057",
    "No Category": "\u30ab\u30c6\u30b4\u30ea\u30fc\u306a\u3057",
    "No Confirmed Results Yet": "\u627f\u8a8d\u6e08\u307f\u7d50\u679c\u306a\u3057",
    "No Gender Information": "\u30b8\u30a7\u30f3\u30c0\u30fc\u306e\u60c5\u5831\u306a\u3057",
    "No Position Information": "\u4f4d\u7f6e\u60c5\u5831\u306a\u3057",
    "No Region Information": "\u5730\u57df\u60c5\u5831\u306a\u3057",
    "No Speaker Categories Information": "\u30b9\u30d4\u30fc\u30ab\u30fc\u30ab\u30c6\u30b4\u30ea\u30fc\u306e\u60c5\u5831\u306a\u3057",
    "No changes": "\u5909\u66f4\u306a\u3057",
    "No code name set": "\u30b3\u30fc\u30c9\u540d\u306a\u3057",
    "No matching people found.": "\u8a72\u5f53\u306e\u53c2\u52a0\u8005\u304c\u3044\u307e\u305b\u3093\u3002",
    "No matching rooms found.": "\u8a72\u5f53\u306e\u90e8\u5c4b\u304c\u3042\u308a\u307e\u305b\u3093\u3002",
    "Noon": "12\u6642",
    "Not Checked-In": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u6e08\u307f\u3067\u306a\u3044",
    "Note: You are %s hour ahead of server time.": [
      "\u30ce\u30fc\u30c8: \u3042\u306a\u305f\u306e\u74b0\u5883\u306f\u30b5\u30fc\u30d0\u30fc\u6642\u9593\u3088\u308a\u3001%s\u6642\u9593\u9032\u3093\u3067\u3044\u307e\u3059\u3002"
    ],
    "Note: You are %s hour behind server time.": [
      "\u30ce\u30fc\u30c8: \u3042\u306a\u305f\u306e\u74b0\u5883\u306f\u30b5\u30fc\u30d0\u30fc\u6642\u9593\u3088\u308a\u3001%s\u6642\u9593\u9045\u308c\u3066\u3044\u307e\u3059\u3002"
    ],
    "November": "11\u6708",
    "Now": "\u73fe\u5728",
    "October": "10\u6708",
    "Open the assistant version.": "\u30a2\u30b7\u30b9\u30bf\u30f3\u30c8\u7248\u3092\u958b\u304f",
    "Panellist": "\u30d1\u30cd\u30eb",
    "Priority %1": "\u512a\u5148\u5ea6%1",
    "Rank": "\u30e9\u30f3\u30af",
    "Re-Edit": "\u518d\u7de8\u96c6",
    "Region": "\u5730\u57df",
    "Remove %s by selecting them and then select the \"Remove\" arrow button.": "%s\u3092\u524a\u9664\u3059\u308b\u306b\u306f\u3001\u9805\u76ee\u3092\u9078\u629e\u3057\u3066\u304b\u3089\"\u524a\u9664\"\u77e2\u5370\u30dc\u30bf\u30f3\u3092\u9078\u629e\u3057\u307e\u3059\u3002",
    "Remove all %s": "%s\u3092\u3059\u3079\u3066\u524a\u9664",
    "Remove selected %s": "\u9078\u629e\u3055\u308c\u305f%s\u3092\u524a\u9664",
    "Return to Draw": "\u5bfe\u6226\u8868\u306b\u623b\u308b",
    "Review": "\u518d\u95b2\u89a7",
    "Saturday": "\u571f\u66dc\u65e5",
    "Scan Using Camera": "\u30ab\u30e1\u30e9\u3067\u30b9\u30ad\u30e3\u30f3",
    "September": "9\u6708",
    "Set All Breaking as Available": "\u30d6\u30ec\u30a4\u30af\u3057\u305f\u5168\u54e1\u3092\u53c2\u52a0\u53ef\u80fd\u306b\u3059\u308b",
    "Set all availabilities to exactly match check-ins.": "\u30e9\u30a6\u30f3\u30c9\u306e\u53c2\u52a0\u72b6\u6cc1\u3092\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u72b6\u6cc1\u3068\u4e00\u81f4\u3055\u305b\u308b",
    "Set all the availabilities to exactly match what they were in the previous round.": "\u500b\u306e\u30e9\u30a6\u30f3\u30c9\u306e\u53c2\u52a0\u72b6\u6cc1\u3092\u76f4\u524d\u306e\u30e9\u30a6\u30f3\u30c9\u3068\u4e00\u81f4\u3055\u305b\u308b",
    "Set people as available only if they have a check-in and are currently unavailable \u2014 i.e. it will not overwrite any existing availabilities.": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u3092\u3057\u3066\u3044\u3066\u30e9\u30a6\u30f3\u30c9\u306e\u53c2\u52a0\u72b6\u6cc1\u304c\u4e0d\u53ef\u306e\u4eba\u306e\u307f\u3092\u53ef\u306b\u3059\u308b\u3002",
    "Solo Chair": "\u5358\u30c1\u30a7\u30a2",
    "Speaker Demographics": "\u30b9\u30d4\u30fc\u30ab\u30fc\u306e\u5c5e\u6027\u5206\u5e03",
    "Speaker Results": "\u30b9\u30d4\u30fc\u30ab\u30fc\u306e\u7d50\u679c",
    "Stop Camera Scan": "\u30ab\u30e1\u30e9\u30b9\u30ad\u30e3\u30f3\u3092\u4e2d\u6b62",
    "Sunday": "\u65e5\u66dc\u65e5",
    "Team": "\u30c1\u30fc\u30e0",
    "The bracket range of the hypothetical debate": "\u4eee\u88c5\u306e\u30c7\u30a3\u30d9\u30fc\u30c8\u306e\u30d6\u30e9\u30b1\u30c3\u30c8\u7bc4\u56f2",
    "The debate's bracket": "\u8a66\u5408\u306e\u30d6\u30e9\u30b1\u30c3\u30c8",
    "The estimated total number of live break categories across all teams of the hypothetical debate": "\u4eee\u306e\u8a66\u5408\u306e\u5168\u30c1\u30fc\u30e0\u306e\u30d6\u30ec\u30a4\u30af\u306e\u53ef\u80fd\u6027\u304c\u6b8b\u3063\u3066\u3044\u308b\u30ab\u30c6\u30b4\u30ea\u30fc\u306e\u7dcf\u6570",
    "The total number of live break categories across all teams": "\u5168\u30c1\u30fc\u30e0\u306e\u30d6\u30ec\u30a4\u30af\u306e\u53ef\u80fd\u6027\u304c\u6b8b\u3063\u3066\u3044\u308b\u30ab\u30c6\u30b4\u30ea\u30fc\u306e\u7dcf\u6570",
    "This debate's priority": "\u30c7\u30a3\u30d9\u30fc\u30c8\u306e\u512a\u5148\u5ea6",
    "This page will live-update with new check-ins as they occur although the initial list may be up to a minute old.": "\u65b0\u305f\u306a\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u306f\u81ea\u52d5\u7684\u306b\u53cd\u6620\u3055\u308c\u307e\u3059\uff08\u305f\u3060\u30571\u5206\u7a0b\u5ea6\u306e\u9045\u5ef6\u304c\u3042\u308b\u5834\u5408\u304c\u3042\u308a\u307e\u3059\uff09\u3002",
    "This person does not have a check-in identifier so they can't be checked in": "\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u306e\u8b58\u5225\u30b3\u30fc\u30c9\u304c\u306a\u3044\u305f\u3081\u30c1\u30a7\u30c3\u30af\u30a4\u30f3\u3067\u304d\u307e\u305b\u3093",
    "Thursday": "\u6728\u66dc\u65e5",
    "Today": "\u4eca\u65e5",
    "Tomorrow": "\u660e\u65e5",
    "Trainee": "\u30c8\u30ec\u30a4\u30cb\u30fc",
    "Tuesday": "\u706b\u66dc\u65e5",
    "Turn On Sounds": "\u97f3\u58f0\u3092\u30aa\u30f3\u306b\u3059\u308b",
    "Type into this box to filter down the list of available %s.": "\u4f7f\u7528\u53ef\u80fd\u306a %s \u306e\u30ea\u30b9\u30c8\u3092\u7d5e\u308a\u8fbc\u3080\u306b\u306f\u3001\u3053\u306e\u30dc\u30c3\u30af\u30b9\u306b\u5165\u529b\u3057\u307e\u3059\u3002",
    "Type into this box to filter down the list of selected %s.": "\u9078\u629e\u3055\u308c\u305f%s\u306e\u30ea\u30b9\u30c8\u3092\u7d5e\u308a\u8fbc\u3080\u306b\u306f\u3001\u3053\u306e\u30dc\u30c3\u30af\u30b9\u306b\u5165\u529b\u3057\u307e\u3059\u3002",
    "Unaffiliated": "\u7121\u6240\u5c5e",
    "Uncategorised": "\u30ab\u30c6\u30b4\u30ea\u30fc\u306a\u3057",
    "Unconfirmed": "\u672a\u627f\u8a8d",
    "Unknown": "\u4e0d\u660e",
    "Wednesday": "\u6c34\u66dc\u65e5",
    "Yes": "\u306f\u3044",
    "Yesterday": "\u6628\u65e5",
    "You cannot confirm this ballot because you entered it": "\u81ea\u5206\u3067\u5165\u529b\u3057\u305f\u30d0\u30ed\u30c3\u30c8\u306f\u627f\u8a8d\u3067\u304d\u307e\u305b\u3093",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "\u64cd\u4f5c\u3092\u9078\u629e\u3057\u307e\u3057\u305f\u304c\u3001\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u5909\u66f4\u306f\u3042\u308a\u307e\u305b\u3093\u3067\u3057\u305f\u3002\u3082\u3057\u304b\u3057\u3066\u4fdd\u5b58\u30dc\u30bf\u30f3\u3067\u306f\u306a\u304f\u3066\u5b9f\u884c\u30dc\u30bf\u30f3\u3092\u304a\u63a2\u3057\u3067\u3059\u304b\u3002",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "\u64cd\u4f5c\u3092\u9078\u629e\u3057\u307e\u3057\u305f\u304c\u3001\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\u3002OK\u3092\u30af\u30ea\u30c3\u30af\u3057\u3066\u4fdd\u5b58\u3057\u3066\u304f\u3060\u3055\u3044\u3002\u305d\u306e\u5f8c\u3001\u64cd\u4f5c\u3092\u518d\u5ea6\u5b9f\u884c\u3059\u308b\u5fc5\u8981\u304c\u3042\u308a\u307e\u3059\u3002",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "\u30d5\u30a3\u30fc\u30eb\u30c9\u306b\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u304c\u3042\u308a\u307e\u3059\u3002\u64cd\u4f5c\u3092\u5b9f\u884c\u3059\u308b\u3068\u672a\u4fdd\u5b58\u306e\u5909\u66f4\u306f\u5931\u308f\u308c\u307e\u3059\u3002",
    "abbrev. day Friday\u0004Fri": "\u91d1",
    "abbrev. day Monday\u0004Mon": "\u6708",
    "abbrev. day Saturday\u0004Sat": "\u571f",
    "abbrev. day Sunday\u0004Sun": "\u65e5",
    "abbrev. day Thursday\u0004Thur": "\u6728",
    "abbrev. day Tuesday\u0004Tue": "\u706b",
    "abbrev. day Wednesday\u0004Wed": "\u6c34",
    "abbrev. month April\u0004Apr": "4\u6708",
    "abbrev. month August\u0004Aug": "8\u6708",
    "abbrev. month December\u0004Dec": "12\u6708",
    "abbrev. month February\u0004Feb": "2\u6708",
    "abbrev. month January\u0004Jan": "1\u6708",
    "abbrev. month July\u0004Jul": "7\u6708",
    "abbrev. month June\u0004Jun": "6\u6708",
    "abbrev. month March\u0004Mar": "3\u6708",
    "abbrev. month May\u0004May": "5\u6708",
    "abbrev. month November\u0004Nov": "11\u6708",
    "abbrev. month October\u0004Oct": "10\u6708",
    "abbrev. month September\u0004Sep": "9\u6708",
    "adjudicators with gender data": "\u4eba\u306e\u30b8\u30a7\u30f3\u30c0\u30fc\u60c5\u5831\u3042\u308a\u306e\u30b8\u30e3\u30c3\u30b8",
    "feedback scores total": "\u3064\u306e\u30d5\u30a3\u30fc\u30c9\u30d0\u30c3\u30af\u30b9\u30b3\u30a2",
    "one letter Friday\u0004F": "\u91d1",
    "one letter Monday\u0004M": "\u6708",
    "one letter Saturday\u0004S": "\u571f",
    "one letter Sunday\u0004S": "\u65e5",
    "one letter Thursday\u0004T": "\u6728",
    "one letter Tuesday\u0004T": "\u706b",
    "one letter Wednesday\u0004W": "\u6c34",
    "saving...": "\u4fdd\u5b58\u4e2d...",
    "speaker scores total": "\u3064\u306e\u30b9\u30d4\u30fc\u30ab\u30fc\u30b9\u30b3\u30a2",
    "speakers with gender data": "\u4eba\u306e\u30b8\u30a7\u30f3\u30c0\u30fc\u60c5\u5831\u3042\u308a\u306e\u30b9\u30d4\u30fc\u30ab\u30fc"
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
    "DATETIME_FORMAT": "Y\u5e74n\u6708j\u65e5G:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M"
    ],
    "DATE_FORMAT": "Y\u5e74n\u6708j\u65e5",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%b %d %Y",
      "%b %d, %Y",
      "%d %b %Y",
      "%d %b, %Y",
      "%B %d %Y",
      "%B %d, %Y",
      "%d %B %Y",
      "%d %B, %Y"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "n\u6708j\u65e5",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "Y/m/d G:i",
    "SHORT_DATE_FORMAT": "Y/m/d",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "G:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "Y\u5e74n\u6708"
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

