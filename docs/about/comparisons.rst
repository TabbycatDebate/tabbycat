==================================
Comparison With Other Tab Software
==================================

This page is, obviously, written by the developers of Tabbycat. We like Tabbycat. However you're probably here because you are interested in using Tabbycat and wondering if it is the best option for your tournament. Rarely is there a single best option for everyone: different softwares have made different trade-offs in their development focus on different aspects of tabbing. We have authored this in conjunction with experienced tab directors and chief adjudicators to fairly and accurately evaluate when and why you would you another software over Tabbycat, or vice-versa. As such we are limiting the discussion to the major software using for both British Parliamentary and World Schools / Australasian variations of two-team formats. As with all our documentation, this page is open-source and we welcome :ref:`feedback and contributions <contributing>`.

Preliminary Notes
-----------------

While some features may be critical to a tournament, all of the software mentioned here fulfil the basic functionality of generating draws, allocation adjudicators, and entering results. What is more difficult to capture are the various philosophies behind each software and the user experiences of how they handle the hundreds of small details that constitute the tabbing process. Trade-offs are often less about what a software *can* do than what it can accommodate: whether it gels with how you want to use it and whether it does so in a manner you expected. We believe one of our advantages is in the polish in Tabbycat's design and feature set, which has been iterated over a long period of time (the 'basic' functions of Tabbycat were functional since 2010) so would always encourage you to take it for a test drive.

- Note about licensing
- Note about flexiblity and configuration

Major Features Comparison
-------------------------

===========================  =========== =========== =========== =========== ============
Software                     Tabbycat    T2          Tournaman   Argotabs    Handtabbing
===========================  =========== =========== =========== =========== ============
Actively developed           ?           ?           ?           ?           ?
Actively maintained          ?           ?           ?           ?           ?
Open Source                  ?           ?           ?           ?           ?
Online operation/interfaces  ✅           ✅           X           ✅           X
LAN operation/interface      ✅           ?           ?           ?           X
Offline operation/interface  ✅           ?           ?           ?           ✅
Supported Formats            Various     BP          BP          Most 2-team All
===========================  =========== =========== =========== =========== ============


TODO:

- WUDC Draw compliance
- Data Import options
- Online Tab release
- Translations

- Printable Ballots
- Printable Feedback
- EBallots
- EFeedback
  - Configurable Questions

- Networked Entry
  - 'Assistant Users'
- Shadow Panels
- Mobile UI
- Documentation

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

Comparison with ArgoTabs
------------------------

- idk how argo tabs works but its really well designs and code, so maybe give it a shot
- does it work for anything that’s not WSDC?

Comparison with Tournaman
-------------------------

A crucial limitation, and strength, of tournaman, is that it is a native Windows desktop application. As such it is easy to install and run; however you need to do so on a Windows machine (or emulate Windows). It's worth noting that Tabbycat can also be run locally, in an offline manner. However doing so requires (at least one-off) setup costs.

- Note about tournaman features (is there anything it does better?)
- Note about networked access (if you need networks you're probably want online)
- Note about OSS vs closed source; Tournaman note feature evolving

Comparison with Excel/Hand Tabbing
----------------------------------

For small tournaments, hand tabbing is often the most quick and intuitive option. It has fewer setup costs, is easy to debug, and ...

However it relies on the person tabbing to have a good understanding of draw mathematics, and a high degree of accuracy (or disregard) for results.

It is up to you whether the setup costs are worth it. Tabbycat, and other software, also offer conveniences, such as for draw or tab release that are better than posting excel sheets.

