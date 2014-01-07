Tabbycat
========

Tabbycat is a draw tabulation system for 3 vs 3 debating tournaments.

Tabbycat was authored by Qi-Shan Lim for Auckland Australs 2010, was used at Victoria
Australs 2012, and will be used at Otago Australs 2014.

We haven't released this under an open-source licence (so there is no formal general
right to use this software), but if you're running a debating tournament,
you're certainly welcome to use it.  It'd be nice if you could please
let us know that you're doing so, and let us know how it went.  Pull requests
are welcome and encouraged.

Requirements and getting started
--------------------------------
Tabbycat runs on Linux, and requires Python (which is normally distributed with
Linux).  It runs a Django-based server.  All requirements are included in the
installation instructions in the INSTALL file.

You'll need to set up a PostgreSQL database, or your favourite Django-compatible
database engine should work just as well.

We haven't yet done a user-friendly data import function.  But there are plenty
of example data import scripts in the src/data directory.  The easiest thing to do
is just to write a script to suit your data format.

Contact
-------
Contact Chuan-Zheng Lee with any questions.  I shouldn't be too hard to find, but
the easiest thing to do is check out the repository and find my e-mail address
in the commit history.  Or message me on Facebook (czlee) or Twitter (@czlee11).