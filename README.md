# Tabbycat

[![Deploy](https://img.shields.io/badge/%E2%86%91_Deploy_to-Heroku-7056bf.svg)](https://heroku.com/deploy) [![Docs](https://readthedocs.org/projects/tabbycat/badge/?version=latest)](http://tabbycat.readthedocs.io/en/latest/)  [![Docs](https://readthedocs.org/projects/tabbycat/badge/?version=stable)](http://tabbycat.readthedocs.io/en/stable/) [![Build Status](https://travis-ci.org/czlee/tabbycat.svg?branch=develop)](https://travis-ci.org/czlee/tabbycat) [![Dependency Status](https://gemnasium.com/badges/github.com/czlee/tabbycat.svg)](https://gemnasium.com/github.com/czlee/tabbycat)

Tabbycat is a draw tabulation system for 3 vs 3 debating tournaments. It was used at Australs in Auckland 2010, [Wellington 2012](https://www.facebook.com/Australs2012), [Dunedin 2014](http://australs2014.herokuapp.com), [Daejeon 2015](http://australs2015.herokuapp.com) and [Perth 2016](http://australs2016.herokuapp.com), as well as [many other tournaments of all sizes](http://tabbycat.readthedocs.io/en/stable/about/tournament-history.html).

Our **demo site** is at [tabbycatdebate.herokuapp.com](http://tabbycatdebate.herokuapp.com/). It's normally up, but its form will vary from time to time as we set up new feature demos for people. If it's down and you'd like to see it, or if you want to play with it as if you were running a tournament, [contact us](#authors-and-contacts). To see a post-tournament website, have a look at the [WAustrals 2016 tab website](http://australs2016.herokuapp.com).

## Features

- Enter data from multiple computers simultaneously
- Easily deployable to [Heroku](https://www.heroku.com/) for a fast and free setup
- Automated adjudicator allocations based on adjudicator ranking, room importance, and conflicts
- A drag and drop interface for adjudicator allocation that displays conflicts alongside gender and regional balance
- A fully responsive design that adapts to suit large screens, laptops, tablets, and phones
- Support for Australs, NZ Easters, Australian Easters, Joynt Scroll, UADC, and WSDC rule sets
- Configurable [draw generation rules](http://tabbycat.readthedocs.io/en/stable/features/draw-generation.html) and [team standings rules](http://tabbycat.readthedocs.io/en/stable/features/team-standings-rules.html)
- Configurable [adjudicator feedback questions](http://tabbycat.readthedocs.io/en/stable/features/adjudicator-feedback.html)
- Optional online submission of feedback and scoresheets
- Optional online post-tournament tab display

Tabbycat started as Australs tab software and has since evolved to support most two-team parliamentary formats. It is a goal of Tabbycat to be flexible and meet the needs of different tournaments. There are many configurable features, and they're best explored by launching your own copy using the "Deploy to Heroku" button above.

If your tournament has requirements that we don't currently support, please [get in touch with us](#authors-and-contacts). In many cases, we might have already put the idea on our [to-do list](https://github.com/czlee/tabbycat/issues). But we have many more ideas than we are able to implement. We prioritise our work by the features that will be used at upcoming tournaments, so if you need some changes, even if they're already on our list, please do contact us early rather than waiting for us to implement your requirement.

## Installation and User Guide

Our user guide is at [tabbycat.readthedocs.io](http://tabbycat.readthedocs.io/). The fastest way to launch a Tabbycat site is to click this button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

If you'd like to run a tournament with Tabbycat but are not able to set it up, get in touch with [Philip](http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=) and he can setup a private online copy of the software for your use.

## License and Development

We haven't released this under an open-source licence (so there is no formal general right to use this software), but if you're running a debating tournament, you're welcome to use it. It'd be nice if you could please let us know that you're doing so, and let us know how it went. [Our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) is a great place to start. We're happy to help if you have any questions or feature requests although we provide no warranty and disclaim all legal liability.

Pull requests are encouraged and if you're interested in helping out as a developer, we'd love to have you! [Join our Facebook group](https://www.facebook.com/groups/tabbycat.debate/) and contact us as below.

If you have a GitHub account, we'd prefer that **bug reports** be submitted to our [issues page](https://github.com/czlee/tabbycat/issues). Otherwise, feel free to [shoot us an email](#authors-and-contacts).

## Authors and Contacts

Tabbycat was authored by Qi-Shan Lim for Auckland Australs 2010. The current active developers are:

- Philip Belesky ([e-mail](http://www.google.com/recaptcha/mailhide/d?k=01aItEbHtwnn1PzIPGGM9W8A==&c=XWljk2iGokfhziV2Rt4OiKA5uab1vCrnxwXcPUsWgnM=))
- Chuan-Zheng Lee ([e-mail](mailto:czlee@stanford.edu))

Please don't hesitate to contact us with any questions, suggestions, or generally anything relating to Tabbycat.
