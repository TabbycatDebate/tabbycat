=======================
Tab Software Comparison
=======================

This page is, obviously, written by the developers of Tabbycat. We like Tabbycat. However you're probably here because you are interested in using Tabbycat; either in the abstract or for a particular upcoming tournament. Given that Tabbycat is a new entrant to the world of BP tabbing we thought it would be useful to make a document like this that outlines how it compares to the more established options.

Rarely is there a single best option for everyone and every situation: different tab programs imagine the tabbing process in a distinct way and have made distinct trade-offs in their development process and design decisions.

We have authored this in conjunction with experienced tab directors and chief adjudicators to try and give a fair and accurate evaluation of when, and why, you would use Tabbycat over other software and vice-versa. At present the guide just focuses on the major options available for the British Parliamentary format, although we'd like to see this to expand to incorporate the other formats that Tabbycat supports at some point in the future. As with all of our documentation, this page is open-source and we welcome :ref:`feedback and contributions <contributing>`.

Major Features
--------------

All of the software discussed here does the basics necessary to actually run a tournament: generating draws, allocating adjudicators, entering results, etc. Occasionally though there are special features or capabilities outside of these core tasks that are crucial to your vision of how a tournament should be tabbed. For these occasions, we've attempted to compile a feature comparison table below so you can identify the core abilities of each platform.

That said, we've produced such a check-list with a degree of trepidation. The raw specifications of a technology rarely define the core experience of what it is like to use that technology; whether it be a phone, a car, or indeed, a piece of tabbing software. That is to say the trade-offs between software are often less about what they can do than about what they can do *easily*. Each program has made different design decisions about the million tiny details that comprise the tabbing process, and for Tabbycat in particular we think the levels of polish and usability in even the 'basic' functionality is something that sets it apart.

===========================  =========== =========== =========== ============
Software                     Tabbycat    Tabbie2     Tournaman   Handtabs
===========================  =========== =========== =========== ============
Actively developed           ✅          ✅           ❔           ❔
Actively maintained          ✅          ✅           ✅           ❔
Open Source                  ✅          ✅           ❔           ❔
Documentation                ❔          ❔           ❔           ❔
Online operation/interfaces  ✅          ✅           ❌           ❌
LAN operation/interface      ✅          🔶           ✅           ❌
Offline operation/interface  ✅          🔶           ✅           ✅
===========================  =========== =========== =========== ============

===========================  =========== =========== =========== ============
Software                     Tabbycat    Tabbie2     Tournaman   Handtabs
===========================  =========== =========== =========== ============
Supported Formats            Various      BP          BP          Various
Parallel breaks (i.e. ESL)   ✅          ✅          ❔          ❔
Parallel tabs (i.e. ESL)     ✅          ✅          ❔          ❔
WUDC Draw Compliance         ✅          ✅          ✅          ✅
Position rotation            ❔          ❔          ❔          ❔
Adjudicator allocation       ❔          ❔          ❔          ❔
Energy/Importance            ❔          ❔          ❔          ❔
Shadow Panels                ❔          ✅          ❔          ❔
Diversity allocation         ❔          ❔          ❔          ❔
Diversity highlighting       ❔          ❔          ❔          ❔
===========================  =========== =========== =========== ============

===========================  =========== =========== =========== ============
Software                     Tabbycat    Tabbie2     Tournaman   Handtabs
===========================  =========== =========== =========== ============
Printable Ballots            ✅          ✅          ❔          ❔
Printable Feedback           ✅          ✅          ❔          ❔
eBallots                     ✅          ✅          ❔          ❔
eFeedback                    ✅          ✅          ❔          ❔
Configurable Questions       ✅          ❔          ❔          ❔
Mobile UI                    ✅          ✅          ❔          ❔
===========================  =========== =========== =========== ============

🔶 I think so; unclear? Difficult to setup

Note: have excluded small misc features that are marginal or exclusive to one software

<!-- Features to Add

- Venue accessibility features
- Assistant data entry options
- Data validation methods for ballots?
- Running break rounds
- Import options
    - CSV
    - Manual
    - ???
- Printable ID cards stuff
 -->


Comparison with T2
------------------

Centralised vs Decentralised

- Speakers in T2 tournaments are tied to their accounts; as such they come pre-populated with their institutional histories, full names, conflicts etc. As such, there is prima facie, lower setup costs to a tournament. However this comes with limitations of requiring that users who don't have accounts first sign up to them.
- Also in terms of data privacy; as a centralised service T2 retains those records, which are accessible by administrative users. This places limitations on sensitive information such as conflicts or gender; notably conflicts are only accessible to administrative 'super' users (otherwise anyone who started a tournament could see them). In tabbycat, data is only stored on a per-tournament basis. When providing information to a tournament, that information is then not accessible to other copies of Tabbycat. This means that conflicts could be revealed to small tournaments, without the expectation that they would be viewed by people outside that tournament's tab directors / adjudication core.
- Centralised systems are good for efeedback/ballots; users know roughly where to go and what to do. In contrast tabbycat requires per-tournament URLs be distributed to participants
- Tabbie tournaments have enduring records, motion banks etc. More discoverable?
- Heroku is the platform of choice; can be hosted in EU or US. Free, but for minor

Centralised system, while this has yet to happen, can be prone to errors that bring down the whole site our outages. However note that T2 and Heroku (our dominant deploy method) depend on the same AWS infrastructure so service-level bugs affect both.

Configuration vs Convention

- Tabbycat is highly customisable and flexible; having been developed to support numerous formats and rules…
- Tabbycat let's you edit the backing 'database' which often let's you fix issues on the fly. However this also needs to be done with caution.

Example about feedback questions

Small feature comparisons

- CSV import for Tabbycat requires offline access; although the visual importer is designed for easy copy/pasting from information
- Position rotation?
- Differences in allocation algorithms and interfaces
- Documentation and learning options

Comparison with Tournaman
-------------------------

A crucial limitation, and strength, of tournaman, is that it is a native Windows desktop application. As such it is easy to install and run; however you need to do so on a Windows machine (or emulate Windows). It's worth noting that Tabbycat can also be run locally, in an offline manner. However doing so requires (at least one-off) setup costs.

- Note about tournaman features (is there anything it does better?)
- Note about networked access (if you need networks you're probably want online)
- Note about OSS vs closed source; Tournaman note feature evolving

Comparison with Hand-Tabbing (i.e. using a spreadsheet)
-------------------------------------------------------

Hand tabbing is easy, until it isn't. Traditionally, hand-tabbing has been the go-to option for small tournaments as hey, you're pretty handy with a spreadsheet right? Or some since-retired elder has passed down an elaborate series of Excel macros and pointed you in the right direction. Either way, making draws in spreadsheets (or on paper) seems like a pretty approachable task; ultimately it's all cells and formula and tabs. However it does however require you to have a good working knowledge of how rules work and how your spreadsheet software of choice can be made to work them.

That process might be easy for you, or it might not be. But, either way, we'd like to think that Tabbycat offers a better alternative to hand-tabbing regardless of how well you can actually hand-tab. The setup costs of creating a copy of Tabbycat are pretty low and you can speed through the process of draw creation, adjudicator allocation, and result entry at a pace. It's still not going to be as fast a spreadsheet, but we think it's getting pretty close. And in exchange you get a much stronger guarantee of your draws being correct, options for online data entry and tab release, and a much more pleasant experience. Give it a shot!

TODO: fix last sentence

